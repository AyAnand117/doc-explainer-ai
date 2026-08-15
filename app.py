import streamlit as st
import os
from datetime import datetime

from ingestion_pdf import ingest_pdf
from ingestion_images import ingest_image
from retrieval import get_retriever
from qa_chain import answer_question


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="EasySummarizer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# FILE PATHS
# ============================================================

LOGO_PATH = os.path.join("assets", "logo.png")
MAX_FILE_SIZE_MB = 25


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- Global ---------- */
    .stApp {
        background: linear-gradient(180deg, rgba(36,141,149,0.03) 0%, rgba(0,0,0,0) 250px);
    }

    #MainMenu, footer {visibility: hidden;}

    /* ---------- Header ---------- */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin-top: 4px;
        margin-bottom: 2px;
    }

    .main-title {
        font-size: 40px;
        font-weight: 800;
        text-align: center;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #000648, #248D95);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .subtitle {
        text-align: center;
        opacity: 0.65;
        font-size: 16px;
        margin-bottom: 28px;
    }

    /* ---------- Pills / badges ---------- */
    .badge-row {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 30px;
        flex-wrap: wrap;
    }

    .badge {
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 12.5px;
        font-weight: 600;
        border: 1px solid rgba(36,141,149,0.35);
        background: rgba(36,141,149,0.08);
        color: #248D95;
    }

    /* ---------- Upload cards ---------- */
    .upload-card-title {
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 2px;
    }

    .upload-card-desc {
        font-size: 13px;
        opacity: 0.6;
        margin-bottom: 12px;
    }

    /* ---------- Status box ---------- */
    .status-box {
        padding: 16px 18px;
        border-radius: 12px;
        margin: 18px 0;
        border: 1px solid rgba(46, 160, 67, 0.3);
        background: rgba(46, 160, 67, 0.08);
        font-size: 15px;
    }

    .status-box b {
        color: #248D95;
    }

    /* ---------- Sidebar ---------- */
    .sidebar-brand {
        text-align: center;
        margin-top: -5px;
    }

    .sidebar-brand h2 {
        margin-bottom: 3px;
        font-weight: 800;
    }

    .developer-text {
        opacity: 0.6;
        font-size: 12.5px;
    }

    .file-meta-card {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 10px;
        padding: 12px 14px;
        font-size: 13px;
        line-height: 1.6;
    }

    .file-meta-label {
        opacity: 0.6;
    }

    /* ---------- Chat ---------- */
    .chat-empty-state {
        text-align: center;
        padding: 40px 20px;
        opacity: 0.55;
        font-size: 14px;
        border: 1px dashed rgba(128,128,128,0.3);
        border-radius: 12px;
        margin-top: 10px;
    }

    /* ---------- Footer ---------- */
    .footer {
        text-align: center;
        padding: 35px 0 10px 0;
        opacity: 0.5;
        font-size: 12.5px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "chat_history": [],
    "collection_name": None,
    "retriever": None,
    "uploaded_file_name": None,
    "uploaded_file_type": None,
    "uploaded_file_size": None,
    "image_preview": None,
    "exit_requested": False,
    "upload_version": 0,
    "processing_error": None,
}

for key, default_value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


def reset_file_state():
    st.session_state.chat_history = []
    st.session_state.collection_name = None
    st.session_state.retriever = None
    st.session_state.uploaded_file_name = None
    st.session_state.uploaded_file_type = None
    st.session_state.uploaded_file_size = None
    st.session_state.image_preview = None
    st.session_state.processing_error = None
    st.session_state.upload_version += 1


def format_size(num_bytes):
    if num_bytes is None:
        return "—"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes / (1024 * 1024):.1f} MB"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.warning("Logo not found. Make sure assets/logo.png exists.")

    st.markdown(
        """
        <div class="sidebar-brand">
            <h2>EasySummarizer</h2>
            <div class="developer-text">
                Developed by <b>Ayush Anand</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown("## ⚙️ Controls")
    st.caption("Upload a PDF or image and start asking questions.")

    st.divider()

    col_clear, col_exit = st.columns(2)

    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True):
            reset_file_state()
            st.rerun()

    with col_exit:
        if st.button("🚪 Exit", use_container_width=True):
            st.session_state.exit_requested = True

    st.divider()
    st.markdown("### 📄 Current File")

    if st.session_state.uploaded_file_name:
        icon = "📄" if st.session_state.uploaded_file_type == "pdf" else "🖼️"
        st.markdown(
            f"""
            <div class="file-meta-card">
                {icon} <b>{st.session_state.uploaded_file_name}</b><br>
                <span class="file-meta-label">Type:</span> {st.session_state.uploaded_file_type.upper()}<br>
                <span class="file-meta-label">Size:</span> {format_size(st.session_state.uploaded_file_size)}<br>
                <span class="file-meta-label">Messages:</span> {len(st.session_state.chat_history)}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("No file uploaded yet.")

    if st.session_state.chat_history:
        st.divider()
        transcript = "\n\n".join(
            f"{m['role'].upper()}: {m['content']}"
            for m in st.session_state.chat_history
        )
        st.download_button(
            "⬇️ Download chat transcript",
            data=transcript,
            file_name=f"easysummarizer_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            use_container_width=True,
        )


# ============================================================
# EXIT MESSAGE
# ============================================================

if st.session_state.exit_requested:
    st.markdown(
        """
        <div style="text-align: center; padding: 100px 20px;">
            <h1>👋 Thanks for using EasySummarizer</h1>
            <p style="opacity: 0.7;">
                Your current session has ended.
                You can safely close this browser tab.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="app-header"><span style="font-size:38px;">📚</span>'
    '<div class="main-title">EasySummarizer</div></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Your AI-powered document and image assistant</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="badge-row">
        <span class="badge">📄 PDF Q&A</span>
        <span class="badge">🖼️ Image OCR</span>
        <span class="badge">💬 Conversational Memory</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown("### 📤 Upload your content")

pdf_column, image_column = st.columns(2, gap="medium")


# ============================================================
# PDF UPLOAD
# ============================================================

with pdf_column:
    with st.container(border=True):
        st.markdown('<div class="upload-card-title">📄 Upload PDF</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="upload-card-desc">Reports, papers, contracts — up to '
            f'{MAX_FILE_SIZE_MB}MB</div>',
            unsafe_allow_html=True,
        )

        pdf_file = st.file_uploader(
            "Choose a PDF document",
            type=["pdf"],
            key=f"pdf_uploader_{st.session_state.upload_version}",
            label_visibility="collapsed",
        )

        if pdf_file is not None:
            size_mb = pdf_file.size / (1024 * 1024)

            if size_mb > MAX_FILE_SIZE_MB:
                st.error(f"File too large ({size_mb:.1f}MB). Max size is {MAX_FILE_SIZE_MB}MB.")

            elif (
                st.session_state.uploaded_file_name != pdf_file.name
                or st.session_state.uploaded_file_type != "pdf"
            ):
                progress = st.progress(0, text="Reading PDF...")

                try:
                    st.session_state.chat_history = []
                    st.session_state.processing_error = None

                    progress.progress(30, text="Extracting and chunking text...")
                    collection_name = ingest_pdf(pdf_file)

                    progress.progress(70, text="Building vector index...")
                    retriever = get_retriever(collection_name)

                    progress.progress(100, text="Done!")

                    st.session_state.collection_name = collection_name
                    st.session_state.retriever = retriever
                    st.session_state.uploaded_file_name = pdf_file.name
                    st.session_state.uploaded_file_type = "pdf"
                    st.session_state.uploaded_file_size = pdf_file.size
                    st.session_state.image_preview = None

                    progress.empty()
                    st.success("PDF processed successfully! 🎉")

                except Exception as e:
                    progress.empty()
                    st.session_state.processing_error = str(e)
                    st.error(f"Error processing PDF: {str(e)}")


# ============================================================
# IMAGE UPLOAD
# ============================================================

with image_column:
    with st.container(border=True):
        st.markdown('<div class="upload-card-title">🖼️ Upload Image</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="upload-card-desc">Scanned pages, screenshots, photos — PNG, JPG, WEBP</div>',
            unsafe_allow_html=True,
        )

        image_file = st.file_uploader(
            "Choose an image",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"image_uploader_{st.session_state.upload_version}",
            label_visibility="collapsed",
        )

        if image_file is not None:
            size_mb = image_file.size / (1024 * 1024)

            st.image(image_file, caption=image_file.name, use_container_width=True)

            if size_mb > MAX_FILE_SIZE_MB:
                st.error(f"File too large ({size_mb:.1f}MB). Max size is {MAX_FILE_SIZE_MB}MB.")

            elif (
                st.session_state.uploaded_file_name != image_file.name
                or st.session_state.uploaded_file_type != "image"
            ):
                progress = st.progress(0, text="Reading image...")

                try:
                    st.session_state.chat_history = []
                    st.session_state.processing_error = None

                    progress.progress(35, text="Running OCR...")
                    collection_name = ingest_image(image_file)

                    progress.progress(75, text="Building vector index...")
                    retriever = get_retriever(collection_name)

                    progress.progress(100, text="Done!")

                    st.session_state.collection_name = collection_name
                    st.session_state.retriever = retriever
                    st.session_state.uploaded_file_name = image_file.name
                    st.session_state.uploaded_file_type = "image"
                    st.session_state.uploaded_file_size = image_file.size
                    st.session_state.image_preview = image_file

                    progress.empty()
                    st.success("Image processed successfully! 🎉")

                except Exception as e:
                    progress.empty()
                    st.session_state.processing_error = str(e)
                    st.error(f"Error processing image: {str(e)}")


# ============================================================
# FILE STATUS
# ============================================================

if st.session_state.retriever is not None:
    st.markdown(
        f"""
        <div class="status-box">
        ✅ <b>Ready!</b> You can now ask questions about
        <b>{st.session_state.uploaded_file_name}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )
elif not st.session_state.processing_error:
    st.info("👆 Upload a PDF or image above to start.")


# ============================================================
# CHAT SECTION
# ============================================================

st.markdown("### 💬 Chat")

if not st.session_state.chat_history:
    st.markdown(
        """
        <div class="chat-empty-state">
            No messages yet — ask something like<br>
            <i>"Summarize this document in 3 bullet points"</i>
        </div>
        """,
        unsafe_allow_html=True,
    )

for message in st.session_state.chat_history:
    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input("Ask a question about your uploaded file...")

if question:

    if st.session_state.retriever is None:
        st.warning("Please upload a PDF or image before asking a question.")
        st.stop()

    st.session_state.chat_history.append({"role": "user", "content": question})

    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                recent_history = st.session_state.chat_history[-10:]
                answer, docs = answer_question(
                    st.session_state.retriever,
                    question,
                    recent_history,
                )

                st.markdown(answer)

                if docs:
                    with st.expander(f"🔎 View retrieved context ({len(docs)} sources)"):
                        for i, doc in enumerate(docs, start=1):
                            st.markdown(f"**Source {i}**")
                            st.write(doc.page_content)
                            if doc.metadata:
                                st.caption(f"Metadata: {doc.metadata}")
                            if i < len(docs):
                                st.divider()

            except Exception as e:
                answer = "I encountered an error while generating the answer."
                st.error(f"Error: {str(e)}")

    st.session_state.chat_history.append({"role": "assistant", "content": answer})

    if len(st.session_state.chat_history) > 10:
        st.session_state.chat_history = st.session_state.chat_history[-10:]


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        Developed by <b>Ayush Anand</b> · EasySummarizer
    </div>
    """,
    unsafe_allow_html=True,
)