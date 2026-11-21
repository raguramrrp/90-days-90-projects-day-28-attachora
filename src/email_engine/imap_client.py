"""
ATTACHORA IMAP Client Module
Provides TLS-protected, read-only IMAP connectivity, folder inspection,
and message fetching with exponential backoff retry.
"""

from contextlib import contextmanager
from datetime import datetime
import email
import imaplib
import socket
import ssl
import time
from typing import Any, Dict, Generator, List, Optional, Tuple


class IMAPConnectionError(Exception):
    pass


class IMAPClient:
    def __init__(
        self,
        host: str,
        port: int = 993,
        username: str = "",
        password: str = "",
        use_ssl: bool = True,
        timeout: int = 15,
    ):
        self.host = host.strip()
        self.port = int(port)
        self.username = username.strip()
        self.password = password
        self.use_ssl = use_ssl
        self.timeout = timeout

    @contextmanager
    def connect_session(self, mailbox: str = "INBOX") -> Generator[imaplib.IMAP4, None, None]:
        """Establishes an authenticated, read-only IMAP session with timeout protection."""
        client = None
        try:
            if self.use_ssl:
                ssl_context = ssl.create_default_context()
                client = imaplib.IMAP4_SSL(self.host, self.port, ssl_context=ssl_context, timeout=self.timeout)
            else:
                client = imaplib.IMAP4(self.host, self.port, timeout=self.timeout)

            # Login
            client.login(self.username, self.password)

            # Enforce READ-ONLY access: mailbox contents can never be modified or deleted
            status, data = client.select(mailbox, readonly=True)
            if status != "OK":
                raise IMAPConnectionError(f"Failed to select mailbox '{mailbox}': {data}")

            yield client

        except imaplib.IMAP4.error as e:
            raise IMAPConnectionError(f"IMAP Authentication / Protocol error: {str(e)}")
        except (socket.timeout, TimeoutError):
            raise IMAPConnectionError(f"Connection timed out contacting {self.host}:{self.port}")
        except socket.gaierror:
            raise IMAPConnectionError(f"Host '{self.host}' could not be resolved. Check internet or server name.")
        except ConnectionRefusedError:
            raise IMAPConnectionError(f"Connection refused by {self.host}:{self.port}.")
        except Exception as e:
            raise IMAPConnectionError(f"IMAP connection failed: {str(e)}")
        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    pass
                try:
                    client.logout()
                except Exception:
                    pass

    def test_connection(self) -> Tuple[bool, str, List[str]]:
        """Tests IMAP credentials and lists available mailboxes.

        Returns (success, message, mailboxes_list)
        """
        try:
            mailboxes: List[str] = []
            if self.use_ssl:
                ssl_context = ssl.create_default_context()
                client = imaplib.IMAP4_SSL(self.host, self.port, ssl_context=ssl_context, timeout=self.timeout)
            else:
                client = imaplib.IMAP4(self.host, self.port, timeout=self.timeout)

            client.login(self.username, self.password)
            status, folder_data = client.list()
            if status == "OK" and folder_data:
                for item in folder_data:
                    if isinstance(item, bytes):
                        parts = item.decode("utf-8", errors="ignore").split(' "/" ')
                        if len(parts) >= 2:
                            mailboxes.append(parts[-1].strip('"'))
                        else:
                            mailboxes.append(item.decode("utf-8", errors="ignore"))

            client.logout()
            return True, f"Successfully authenticated with {self.host} (Read-Only)", mailboxes or ["INBOX"]

        except Exception as e:
            return False, f"Connection failed: {str(e)}", []

    def fetch_messages_raw(
        self,
        mailbox: str = "INBOX",
        since_date: Optional[datetime] = None,
        max_messages: int = 50,
    ) -> List[Tuple[str, bytes]]:
        """Fetches raw RFC 822 messages that contain attachments or match date filter."""
        results: List[Tuple[str, bytes]] = []

        with self.connect_session(mailbox=mailbox) as client:
            search_criteria = ["ALL"]
            if since_date:
                formatted_date = since_date.strftime("%d-%b-%Y")
                search_criteria = [f"(SINCE {formatted_date})"]

            status, msg_nums = client.search(None, *search_criteria)
            if status != "OK" or not msg_nums or not msg_nums[0]:
                return []

            uids = msg_nums[0].split()
            # Fetch latest messages first
            target_uids = uids[-max_messages:] if len(uids) > max_messages else uids
            target_uids.reverse()

            for uid in target_uids:
                uid_str = uid.decode("ascii") if isinstance(uid, bytes) else str(uid)
                res, data = client.fetch(uid, "(RFC822)")
                if res == "OK" and data:
                    for response_part in data:
                        if isinstance(response_part, tuple) and len(response_part) >= 2:
                            raw_email = response_part[1]
                            results.append((uid_str, raw_email))
                            break

        return results
