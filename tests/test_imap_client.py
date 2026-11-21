"""
Unit tests for IMAP Client Module with Mocked Sessions.
"""

from unittest.mock import MagicMock, patch
import pytest
from src.email_engine.imap_client import IMAPClient, IMAPConnectionError


@patch("imaplib.IMAP4_SSL")
def test_imap_test_connection_success(mock_imap):
    instance = MagicMock()
    mock_imap.return_value = instance

    instance.login.return_value = ("OK", [b"Logged in"])
    instance.list.return_value = ("OK", [b'(\\HasNoChildren) "/" "INBOX"', b'(\\HasNoChildren) "/" "Archive"'])

    client = IMAPClient(host="imap.example.com", port=993, username="user@test.com", password="app_password", use_ssl=True)
    success, msg, mailboxes = client.test_connection()

    assert success is True
    assert "Successfully authenticated" in msg
    assert "INBOX" in mailboxes
    assert "Archive" in mailboxes
    instance.logout.assert_called_once()


@patch("imaplib.IMAP4_SSL")
def test_imap_enforces_readonly_mode(mock_imap):
    instance = MagicMock()
    mock_imap.return_value = instance

    instance.login.return_value = ("OK", [b"Logged in"])
    instance.select.return_value = ("OK", [b"10"])

    client = IMAPClient(host="imap.example.com", port=993, username="user@test.com", password="pass", use_ssl=True)

    with client.connect_session(mailbox="INBOX") as session:
        # Verify select was called with readonly=True!
        instance.select.assert_called_with("INBOX", readonly=True)


@patch("imaplib.IMAP4_SSL")
def test_imap_authentication_failure(mock_imap):
    import imaplib

    instance = MagicMock()
    mock_imap.return_value = instance
    instance.login.side_effect = imaplib.IMAP4.error("Invalid credentials")

    client = IMAPClient(host="imap.example.com", port=993, username="user@test.com", password="wrong_password", use_ssl=True)
    success, msg, mailboxes = client.test_connection()

    assert success is False
    assert "Invalid credentials" in msg
