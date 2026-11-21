"""
ATTACHORA Attachment Preview Panel
Provides in-app preview rendering for PDFs, images, spreadsheets, and source code,
plus safe ZIP archive inspection with decompression limits.
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
    """Renders a safe preview panel for the selected attachment."""
    if not attachment:
        st.info("Select an attachment to preview.")
        return

    path_str = attachment.get("current_path") or attachment.get("original_path")
    if not path_str or not Path(path_str).exists():
        st.warning(f"Attachment payload file is not available on disk: {path_str}")
        return

    file_path = Path(path_str)
    ext = (attachment.get("extension") or file_path.suffix.lstrip(".")).lower()
    file_size_kb = attachment.get("file_size", 0) / 1024

    st.markdown(
        f"""
        <div style="background:#FFFFFF; border:1px solid #E1E5E2; border-radius:5px; padding:8px 12px; margin-bottom:10px;">
            <div style="font-weight:600; font-size:13px; color:#252B29;">
                {file_path.name}
            </div>
            <div style="font-size:11px; color:#737C78;">
                Type: <b>{ext.upper()}</b> · Size: <b>{file_size_kb:.1f} KB</b> · Path: <code class="hash-pill">{file_path.parent.name}</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. PDF Preview via PyMuPDF
    if ext == "pdf":
        try:
            doc = pymupdf.open(str(file_path))
            if len(doc) > 0:
                page = doc[0]
                pix = page.get_pixmap(dpi=120)
                img = Image.open(BytesIO(pix.tobytes("png")))
                st.caption(f"PDF Document · Page 1 of {len(doc)}")
                st.image(img, use_container_width=True)
                doc.close()
            else:
                st.info("PDF document contains no renderable pages.")
        except Exception as e:
            st.error(f"Unable to render PDF preview: {str(e)}")

    # 2. Image Preview
    elif ext in ("png", "jpg", "jpeg", "gif", "webp", "bmp"):
        try:
            img = Image.open(file_path)
            st.caption(f"Image ({img.width}x{img.height})")
            st.image(img, use_container_width=True)
        except Exception as e:
            st.error(f"Unable to load image: {str(e)}")

    # 3. CSV / Tabular Preview
    elif ext in ("csv", "tsv"):
        try:
            sep = "\t" if ext == "tsv" else ","
            df = pd.read_csv(file_path, sep=sep, nrows=20)
            st.caption(f"CSV Data Preview (First {len(df)} rows)")
            st.dataframe(df, use_container_width=True, height=220)
        except Exception as e:
            st.error(f"CSV parse error: {str(e)}")

    # 4. Excel Preview
    elif ext in ("xlsx", "xls"):
        try:
            df = pd.read_excel(file_path, nrows=20)
            st.caption(f"Excel Sheet Preview (First {len(df)} rows)")
            st.dataframe(df, use_container_width=True, height=220)
        except Exception:
            st.info(f"Excel binary spreadsheet ({file_size_kb:.1f} KB).")

    # 5. Text & Source Code
    elif ext in ("txt", "py", "sql", "json", "xml", "yml", "yaml", "html", "css", "md", "log", "sh", "bat"):
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(15_000)
            st.caption("Source Text / Code Preview")
            st.code(content, language=ext if ext in ("python", "sql", "json", "html", "css") else "text")
        except Exception as e:
            st.error(f"Cannot read text file: {str(e)}")

    # 6. Safe ZIP Inspection
    elif ext == "zip":
        st.caption("Safe Archive Contents (In-Memory Inspection)")
        inspection = inspect_zip_archive_safely(file_path)
        if not inspection["is_safe"]:
            st.error(f"Security Alert: {inspection.get('warning')}")
        else:
            zc1, zc2 = st.columns(2)
            zc1.markdown(f"<div style='font-size:12px;'>Files: <b>{inspection['entry_count']}</b></div>", unsafe_allow_html=True)
            uncomp_mb = inspection["total_uncompressed_bytes"] / (1024 * 1024)
            zc2.markdown(f"<div style='font-size:12px;'>Uncompressed: <b>{uncomp_mb:.2f} MB</b></div>", unsafe_allow_html=True)

            if inspection["entries"]:
                entries_df = pd.DataFrame(inspection["entries"])[["filename", "uncompressed_size", "compressed_size"]]
                st.dataframe(entries_df, use_container_width=True, height=200)

    # Fallback Metadata
    else:
        st.info(f"Binary format '.{ext}' cannot be previewed in browser.")
        st.markdown(
            f"""
            - **MIME Type:** `{attachment.get('mime_type')}`
            - **File Size:** `{file_size_kb:.1f} KB`
            """
        )

    # Windows Default Application Launch (Explicit Safety Checkbox)
    st.markdown("<div style='margin-top:12px; border-top:1px solid #E1E5E2; padding-top:8px;'></div>", unsafe_allow_html=True)
    open_confirm = st.checkbox("Confirm file is trusted to launch locally", key=f"launch_chk_{attachment.get('id')}")
    if open_confirm:
        if st.button("Open in Windows Default App", key=f"btn_open_{attachment.get('id')}", use_container_width=True):
            try:
                os.startfile(str(file_path.resolve()))
                st.success(f"Launched '{file_path.name}'.")
            except Exception as e:
                st.error(f"Failed to open file: {str(e)}")
