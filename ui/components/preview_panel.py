"""
ATTACHORA Attachment Preview Panel
Provides safe in-app preview rendering for PDFs, images, spreadsheets, code,
and safe archive inspection with archive bomb protection.
"""

from io import BytesIO
import os
from pathlib import Path
import pandas as pd
from PIL import Image
import pymupdf  # PyMuPDF
import streamlit as st
from src.security.validator import inspect_zip_archive_safely


def render_attachment_preview(attachment: dict):
    """Renders a comprehensive, safe preview panel for a selected attachment."""
    if not attachment:
        st.info("Select an attachment row above to inspect details and preview content.")
        return

    path_str = attachment.get("current_path") or attachment.get("original_path")
    if not path_str or not Path(path_str).exists():
        st.warning(f"File payload is not available on disk (Path: {path_str})")
        return

    file_path = Path(path_str)
    ext = (attachment.get("extension") or file_path.suffix.lstrip(".")).lower()
    file_size_kb = attachment.get("file_size", 0) / 1024

    st.markdown(
        f"""
        <div style="background:#FFFFFF; border:1px solid #E1E5E2; border-radius:6px; padding:12px; margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <strong style="font-size:1.05rem;">{attachment.get('original_filename')}</strong>
                    <div style="font-size:0.8rem; color:#737C78;">
                        Category: <b>{attachment.get('category')}</b> &nbsp;|&nbsp;
                        Size: <b>{file_size_kb:.1f} KB</b> &nbsp;|&nbsp;
                        Method: <b>{attachment.get('classification_method')}</b>
                    </div>
                </div>
                <div>
                    <code class="hash-pill" title="SHA-256 Hash">{attachment.get('sha256')[:16]}...</code>
                </div>
            </div>
            <div style="margin-top:6px; font-size:0.8rem; color:#252B29; background:#F8F9F8; padding:6px 10px; border-radius:4px;">
                Reason: <i>{attachment.get('classification_reason', 'N/A')}</i>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. PDF Preview
    if ext == "pdf":
        try:
            doc = pymupdf.open(str(file_path))
            if len(doc) > 0:
                page = doc[0]
                pix = page.get_pixmap(dpi=130)
                img = Image.open(BytesIO(pix.tobytes("png")))
                st.caption(f"PDF Preview · Page 1 of {len(doc)}")
                st.image(img, use_container_width=True)
                doc.close()
            else:
                st.info("PDF document contains no renderable pages.")
        except Exception as e:
            st.error(f"Could not render PDF preview: {str(e)}")

    # 2. Image Preview
    elif ext in ("png", "jpg", "jpeg", "gif", "webp", "bmp"):
        try:
            img = Image.open(file_path)
            st.image(img, caption=f"{attachment.get('original_filename')} ({img.width}x{img.height})", use_container_width=True)
        except Exception as e:
            st.error(f"Could not load image: {str(e)}")

    # 3. Spreadsheets / CSV Preview
    elif ext in ("csv", "tsv"):
        try:
            sep = "\t" if ext == "tsv" else ","
            df = pd.read_csv(file_path, sep=sep, nrows=25)
            st.caption(f"CSV Preview (First {len(df)} rows)")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Could not parse CSV: {str(e)}")

    elif ext in ("xlsx", "xls"):
        try:
            df = pd.read_excel(file_path, nrows=25)
            st.caption(f"Excel Preview (First {len(df)} rows)")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.info(f"Excel binary file detected ({file_size_kb:.1f} KB). Preview requires openpyxl or desktop app.")

    # 4. Text & Code Preview
    elif ext in ("txt", "py", "sql", "json", "xml", "yml", "yaml", "html", "css", "md", "log", "sh", "bat"):
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(20_000)  # Read up to 20KB
            st.caption(f"Source Text / Code Preview")
            st.code(content, language=ext if ext in ("python", "sql", "json", "html", "css") else "text")
        except Exception as e:
            st.error(f"Could not read text: {str(e)}")

    # 5. Safe ZIP Archive Inspection
    elif ext == "zip":
        st.caption("Safe Archive Inspection (Zero Decompression to Disk)")
        inspection = inspect_zip_archive_safely(file_path)
        if not inspection["is_safe"]:
            st.error(f"Security Alert: {inspection.get('warning')}")
        else:
            c1, c2 = st.columns(2)
            c1.metric("Archive Entries", inspection["entry_count"])
            uncompressed_mb = inspection["total_uncompressed_bytes"] / (1024 * 1024)
            c2.metric("Uncompressed Size", f"{uncompressed_mb:.2f} MB")

            if inspection["entries"]:
                entries_df = pd.DataFrame(inspection["entries"])
                st.dataframe(entries_df[["filename", "uncompressed_size", "compressed_size"]], use_container_width=True)

    # 6. Fallback Metadata Card
    else:
        st.info(f"Binary format '.{ext}' cannot be rendered safely in browser.")
        st.markdown(
            f"""
            - **MIME Type:** `{attachment.get('mime_type')}`
            - **Payload Size:** `{file_size_kb:.1f} KB`
            - **Storage Path:** `{file_path}`
            """
        )

    # Action: Open in Windows default application (Safe explicit user confirmation)
    st.markdown("---")
    st.caption("External Execution Guard")
    open_confirm = st.checkbox("I verify this file is safe to launch in local default application", key=f"open_chk_{attachment.get('id')}")
    if open_confirm:
        if st.button("Launch in Windows Default Application", key=f"btn_open_{attachment.get('id')}"):
            try:
                # Use os.startfile on Windows
                os.startfile(str(file_path.resolve()))
                st.success(f"Dispatched '{file_path.name}' to default system application.")
            except Exception as e:
                st.error(f"Failed to launch application: {str(e)}")
