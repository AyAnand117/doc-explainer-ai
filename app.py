import streamlit as st

from ingestion_pdf import ingest_pdf
from ingestion_images import ingest_image
from retrieval import get_retriever
from qa_chain import answer_question

st.set_page_config(
    page_title="Multimodal RAG Assistant",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Multimodal RAG Assistant")
st.write(
    "Upload a **PDF or an image** and ask questions based on its content."
)

uploaded_file = st.file_uploader(
    "Upload a PDF or image",
    type=["pdf", "png", "jpg", "jpeg"],
)

if uploaded_file is not None:

    current_file = uploaded_file.name

    if st.session_state.get("last_uploaded_file") != current_file:

        with st.spinner("Processing file and creating knowledge base..."):

            if uploaded_file.type == "application/pdf":
                collection_name = ingest_pdf(uploaded_file)
            else:
                collection_name = ingest_image(uploaded_file)

        st.session_state.collection_name = collection_name
        st.session_state.last_uploaded_file = current_file

        st.success("File processed successfully!")

    st.divider()

    question = st.text_input(
        "Ask a question about the uploaded file",
        placeholder="What is the main topic of this document?",
    )

    if question:

        with st.spinner("Searching document and generating answer..."):

            retriever = get_retriever(st.session_state.collection_name)
            answer, docs = answer_question(retriever, question)

        st.subheader("Answer")
        st.write(answer)

        st.divider()

        with st.expander("Retrieved context"):
            for i, doc in enumerate(docs, start=1):
                st.markdown(f"### Chunk {i}")
                st.write(doc.page_content)

                if doc.metadata:
                    st.caption(f"Metadata: {doc.metadata}")

                st.divider()

else:
    st.info("Upload a PDF or image to begin.")