"""
ATTACHORA File & Document Integrity Verification Page
Provides cryptographic SHA-256 hash validation, tamper detection,
archive decompression safety audits, and directory path traversal defenses.
"""

from pathlib import Path
import streamlit as st
from src.config import CONFIG
from src.database.db_manager import DB
from src.security.hasher import calculate_sha256
from src.security.sanitizer import sanitize_filename
from src.security.validator import inspect_zip_archive_safely, validate_file_size


def render_integrity_page():
    st.markdown(
        """
        <div style="margin-bottom: 14px;">
            <h1 style="font-size:22px; font-weight:700; color:#202824; margin:0 0 4px 0;">
                Document & Storage Integrity
            </h1>
            <div style="font-size:13px; color:#66716B;">
                Verify cryptographic SHA-256 checksums, audit archive safety limits, and test path traversal defenses.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    t1, t2, t3 = st.tabs(["SHA-256 Audit", "Archive Bomb Defense", "Filename Sanitizer Test"])

    # ------------------ TAB 1: SHA-256 AUDIT ------------------
    with t1:
        st.markdown("#### Cryptographic SHA-256 Health Check")
        st.caption("Verifies that files currently stored on disk exactly match their registered database hashes (anti-tampering audit).")

        attachments = DB.get_attachments_workspace()
        if not attachments:
            st.info("No attachments indexed in database.")
        else:
            col_a, col_b = st.columns([8, 2])
            with col_b:
                run_audit = st.button("Run Full Integrity Scan", type="primary", use_container_width=True)

            audit_results = []
            if run_audit:
                with st.spinner("Calculating SHA-256 hashes of all stored files..."):
                    for att in attachments:
                        p_str = att.get("current_path") or att.get("original_path")
                        p = Path(p_str) if p_str else None
                        if not p or not p.exists():
                            status = "Missing on Disk"
                            is_match = False
                        else:
                            disk_hash = calculate_sha256(p)
                            is_match = (disk_hash.lower() == att["sha256"].lower())
                            status = "Verified Match" if is_match else "Tampered / Hash Mismatch"

                        audit_results.append({
                            "ID": att["id"],
                            "Filename": att["original_filename"],
                            "Category": att["category"],
                            "Registered Hash": att["sha256"][:12] + "...",
                            "Integrity Status": status,
                        })

                st.success(f"Audit completed across {len(audit_results)} documents.")
                import pandas as pd
                df = pd.DataFrame(audit_results)
                st.dataframe(df, use_container_width=True)
            else:
                st.info(f"Click 'Run Full Integrity Scan' to verify all {len(attachments)} documents currently registered.")

    # ------------------ TAB 2: ARCHIVE BOMB DEFENSE ------------------
    with t2:
        st.markdown("#### Safe ZIP Archive Inspector")
        st.caption("Inspects archive headers and compression ratios in memory without extracting payloads to local disk.")

        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #DCE3DE; border-radius:6px; padding:12px; margin-bottom:14px; font-size:12px;">
                <div><b>Maximum Decompression Limit:</b> {CONFIG.MAX_ARCHIVE_SIZE_BYTES / (1024*1024):.0f} MB</div>
                <div><b>Maximum Entry Count:</b> {CONFIG.MAX_ARCHIVE_ENTRIES} files</div>
                <div><b>Maximum Compression Ratio:</b> {CONFIG.MAX_DECOMPRESSION_RATIO}:1</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        test_zip = st.file_uploader("Upload ZIP to Test Defenses", type=["zip"])
        if test_zip:
            # Inspect safely
            from io import BytesIO
            import zipfile
            try:
                zf = zipfile.ZipFile(BytesIO(test_zip.read()))
                total_uncomp = sum(zi.file_size for zi in zf.infolist())
                ratio = total_uncomp / max(1, test_zip.size)
                is_safe = (total_uncomp <= CONFIG.MAX_ARCHIVE_SIZE_BYTES and ratio <= CONFIG.MAX_DECOMPRESSION_RATIO)

                if is_safe:
                    st.success(f"Archive is SAFE: {len(zf.infolist())} entries, {total_uncomp/1024:.1f} KB uncompressed, ratio {ratio:.1f}:1.")
                else:
                    st.error(f"Archive VIOLATES safety limits: {total_uncomp/(1024*1024):.1f} MB exceeds limits!")
            except Exception as e:
                st.error(f"Failed to inspect archive: {str(e)}")

    # ------------------ TAB 3: SANITIZER TEST ------------------
    with t3:
        st.markdown("#### Windows Device & Traversal Defense Tester")
        st.caption("Test how the sanitizer neutralizes illegal characters, Windows reserved names (CON, PRN, AUX, NUL), and traversal sequences.")

        sample_inputs = [
            "../../etc/passwd",
            "CON.pdf",
            "report<v2>:final?.docx",
            "invoice_strip_spaces   ..pdf",
            "NUL.tar.gz",
        ]
        sel_sample = st.selectbox("Select or enter a test filename", options=sample_inputs)
        custom_input = st.text_input("Or custom filename to sanitize:", value=sel_sample)

        if custom_input:
            sanitized = sanitize_filename(custom_input)
            st.markdown(
                f"""
                <div style="background:#FFFFFF; border:1px solid #DCE3DE; border-radius:6px; padding:12px; margin-top:10px;">
                    <div>Input Filename: <code>{custom_input}</code></div>
                    <div style="margin-top:6px; color:#286B50; font-weight:600;">Sanitized Output: <code>{sanitized}</code></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
