import streamlit as st

from ingestion_pdf import ingest_pdf
from ingestion_images import ingest_image
from retrieval import get_retriever
from qa_chain import answer_question

# ----------------------------------------------------
# Page configuration
# ----------------------------------------------------
st.set_page_config(
    page_title="EasySummarizer",
    page_icon="📄",
    layout="wide",
)

# ----------------------------------------------------
# Custom CSS
# ----------------------------------------------------
st.markdown(
    """
    <style>
        .main-title {
            font-size: 42px;
            font-weight: 700;
            color: #2E86C1;
            text-align: center;
            margin-bottom: 5px;
        }

        .subtitle {
            font-size: 18px;
            color: #666666;
            text-align: center;
            margin-bottom: 30px;
        }

        .stButton>button {
            width: 100%;
            border-radius: 10px;
            height: 45px;
            font-weight: 600;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------
# Header
# ----------------------------------------------------
st.markdown(
    '<div class="main-title">📄 EasySummarizer</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Upload a PDF or image and ask intelligent questions based on its content.</div>',
    unsafe_allow_html=True,
)

# ----------------------------------------------------
# Session state
# ----------------------------------------------------
if "collection_name" not in st.session_state:
    st.session_state.collection_name = None

if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

# ----------------------------------------------------
# Action buttons
# ----------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("🗑️ Clear Current File"):
        st.session_state.collection_name = None
        st.session_state.last_uploaded_file = None
        st.success("Previous file removed successfully.")
        st.rerun()

with col2:
    if st.button("❌ Exit App"):
        st.info("Session ended. You may close this browser tab.")
        st.stop()

st.divider()

# ----------------------------------------------------
# Upload section
# ----------------------------------------------------
st.subheader("Upload your content")

left, right = st.columns(2)

uploaded_file = None
file_type = None

# ---------------- PDF Upload ----------------
with left:
    with st.container(border=True):
        st.markdown("### 📄 PDF Document")

        pdf_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            key="pdf_uploader",
        )

        if pdf_file:
            uploaded_file = pdf_file
            file_type = "pdf"

            st.success(f"Selected: **{pdf_file.name}**")

# ---------------- Image Upload ----------------
with right:
    with st.container(border=True):
        st.markdown("### 🖼️ Image")

        image_file = st.file_uploader(
            "Choose an image",
            type=["png", "jpg", "jpeg"],
            key="image_uploader",
        )

        if image_file:
            uploaded_file = image_file
            file_type = "image"

            st.image(
                image_file,
                caption=f"Preview: {image_file.name}",
                use_container_width=True,
            )

            st.success("Image preview loaded successfully.")

# ----------------------------------------------------
# Process upload
# ----------------------------------------------------
if uploaded_file is not None:

    current_file = uploaded_file.name

    if st.session_state.last_uploaded_file != current_file:

        with st.spinner("Processing file and building your knowledge base..."):

            if file_type == "pdf":
                collection_name = ingest_pdf(uploaded_file)
            else:
                collection_name = ingest_image(uploaded_file)

        st.session_state.collection_name = collection_name
        st.session_state.last_uploaded_file = current_file

        st.success(f"Successfully processed **{current_file}**")

# ----------------------------------------------------
# Question answering section
# ----------------------------------------------------
if st.session_state.collection_name:

    st.divider()

    st.subheader("Ask a question")

    question = st.chat_input(
        "Ask anything about the uploaded PDF or image..."
    )

    if question:

        with st.chat_message("user"):
            st.write(question)

        with st.spinner("Searching relevant content and generating answer..."):

            retriever = get_retriever(st.session_state.collection_name)
            answer, docs = answer_question(retriever, question)

        with st.chat_message("assistant"):
            st.write(answer)

        st.divider()

        with st.expander("View retrieved context"):

            for i, doc in enumerate(docs, start=1):

                st.markdown(f"### Chunk {i}")

                st.write(doc.page_content)

                if doc.metadata:
                    st.caption(doc.metadata)

                st.divider()

else:
    st.info(
        "Upload a PDF or image above to begin interacting with your content."
    )