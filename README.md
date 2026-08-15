# EasySummarizer 📚

EasySummarizer is a multimodal AI-powered document assistant that is developed to allow users to upload PDF documents or images and ask questions about their contents.

The application uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from uploaded files and generate grounded responses using an LLM. It also supports OCR-based image processing and short-term conversational memory.

The application is deployed using **Streamlit Community Cloud**.

---

## 🚀 Features

EasySummarizer provides the following features:

* PDF document upload
* Image upload
* Image preview after upload
* OCR-based text extraction from images
* Automatic document chunking
* HuggingFace-based text embeddings
* Chroma vector database
* Semantic similarity-based retrieval
* LLM-powered question answering
* Short-term conversation memory
* Context-aware follow-up questions
* Retrieved source/context display
* Clear current document functionality
* Separate PDF and image upload sections
* Easy-to-use Streamlit interface
* Streamlit Cloud deployment
* Custom EasySummarizer branding

---

## 🏗️ Architecture

The application follows a modular RAG architecture.

```text
                    EasySummarizer
                           │
              ┌────────────┴────────────┐
              │                         │
         PDF Upload                Image Upload
              │                         │
        PyPDFLoader                 Tesseract
              │                         │
        Text Extraction             OCR Text
              │                         │
              └────────────┬────────────┘
                           │
                       Chunking
                           │
                    HuggingFace
                     Embeddings
                           │
                       Chroma DB
                           │
                    User Question
                           │
                 Short-Term Memory
                           │
                    Similarity Search
                           │
                    Retrieved Chunks
                           │
                Context + Chat History
                           │
                       Groq LLM
                           │
                         Answer
```

---

## 🔄 RAG Pipeline

The document processing pipeline follows these stages:

### 1. Document Upload

Users upload either a PDF document or an image through the Streamlit interface.

### 2. Text Extraction

For PDFs, `PyPDFLoader` is used to extract the document text.

For images, **Tesseract OCR** is used to extract textual information.

### 3. Chunking

The extracted text is divided into smaller overlapping chunks using `RecursiveCharacterTextSplitter`.

The following configuration is used:

```text
Chunk size: 600
Chunk overlap: 100
```

### 4. Embeddings

Each text chunk is converted into a vector representation using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

### 5. Vector Storage

The generated embeddings are stored in a **Chroma vector database**.

Each uploaded file is assigned a unique Chroma collection to prevent different documents from being mixed together.

### 6. Retrieval

When a user asks a question, the question is embedded and compared against the stored vectors.

The system retrieves the **top 4 most relevant chunks**.

### 7. Generation

The retrieved chunks are provided as context to the Groq-hosted LLM.

The model is instructed to answer using the retrieved context and avoid inventing information that is not present in the uploaded content.

---

## 🧠 Short-Term Conversation Memory

EasySummarizer supports short-term conversational memory using Streamlit's `session_state`.

The application retains the most recent conversation messages and passes them to the LLM along with the retrieved document context.

This allows users to ask follow-up questions such as:

```text
User:
What was the company's refund policy?

Assistant:
The company allowed refunds within 30 days...

User:
What were the exceptions?

Assistant:
The exceptions included...
```

The assistant is therefore able to use the previous conversation to understand references and follow-up questions.

The conversation history is cleared whenever the user uploads a new document or selects the clear-file option.

---

## 🖼️ Image Processing

Images are processed using an OCR pipeline.

```text
Image Upload
     ↓
Temporary File
     ↓
Tesseract OCR
     ↓
Extracted Text
     ↓
LangChain Document
     ↓
Chunking
     ↓
Embeddings
     ↓
Chroma
     ↓
Retrieval
```

The image itself is also displayed as a preview in the Streamlit application.

The OCR pipeline was particularly suitable for:

* Screenshots
* Receipts
* Invoices
* Forms
* Scanned documents
* Text-heavy images

---

## 🛠️ Technology Stack

| Technology                | Purpose                    |
| ------------------------- | -------------------------- |
| Python                    | Application development    |
| Streamlit                 | Web application and UI     |
| LangChain                 | RAG pipeline orchestration |
| HuggingFace               | Text embeddings            |
| Sentence Transformers     | Embedding model            |
| Chroma                    | Vector database            |
| Groq                      | LLM inference              |
| Tesseract OCR             | Image text extraction      |
| PyPDF                     | PDF text extraction        |
| GitHub                    | Version control            |
| Streamlit Community Cloud | Deployment                 |

---

## 📁 Project Structure

```text
projectabc/
│
├── assets/
│   └── logo.png
│
├── app.py
├── ingestion_pdf.py
├── ingestion_images.py
├── retrieval.py
├── qa_chain.py
│
├── requirements.txt
├── packages.txt
├── .gitignore
└── README.md
```

### `app.py`

The main Streamlit application is responsible for:

* UI rendering
* File uploads
* Image previews
* Session state
* Short-term chat memory
* User interaction
* Displaying retrieved context

### `ingestion_pdf.py`

The PDF ingestion module is responsible for:

* Processing uploaded PDFs
* Extracting text
* Chunking documents
* Creating embeddings
* Storing vectors in Chroma

### `ingestion_images.py`

The image ingestion module is responsible for:

* Processing uploaded images
* Running Tesseract OCR
* Extracting text
* Chunking extracted content
* Creating embeddings
* Storing vectors in Chroma

### `retrieval.py`

The retrieval module is responsible for:

* Loading the appropriate Chroma collection
* Loading the embedding model
* Creating the retriever
* Returning the most relevant document chunks

### `qa_chain.py`

The question-answering module is responsible for:

* Loading the Groq LLM
* Constructing the RAG prompt
* Combining retrieved context with conversation history
* Generating the final response

---

## 🔐 Security

API credentials are kept outside the source code.

During local development, environment variables are used through `.env`.

For Streamlit Community Cloud deployment, the Groq API key is stored using **Streamlit Secrets**.

The `.env` file is excluded from GitHub using `.gitignore`.

Generated Chroma data and the local virtual environment are also excluded from version control.

---

## ☁️ Deployment

The application is deployed using **Streamlit Community Cloud**.

The deployment requires:

```text
requirements.txt
```

for Python dependencies and:

```text
packages.txt
```

for system-level dependencies such as Tesseract OCR.

The `packages.txt` file contained:

```text
tesseract-ocr
```

This allows the OCR functionality to run in the Linux-based Streamlit deployment environment.

---

## ⚙️ Local Setup

The project is developed using a Python virtual environment.

The dependencies were installed using:

```bash
pip install -r requirements.txt
```

The application was started using:

```bash
streamlit run app.py
```

The application is then accessed through the local Streamlit URL.

---

## 🔑 Environment Variables

For local development, the Groq API key is stored in a `.env` file:

```env
GROQ_API_KEY="your_api_key"
```

The `.env` file is not committed to GitHub.

For Streamlit Cloud, the API key is added through the application's **Secrets** configuration.

---

## 🎯 Project Objective

EasySummarizer is developed to demonstrate an end-to-end implementation of a **multimodal RAG application**.

The project combines:

* Document ingestion
* OCR
* Text chunking
* Embeddings
* Vector databases
* Semantic retrieval
* LLM generation
* Conversational memory
* Streamlit application development
* Cloud deployment

The project demonstrates how unstructured user-provided content can be transformed into a searchable knowledge base and used to generate context-aware answers.

---

## 🔮 Future Improvements

The following improvements are identified for future versions:

* Support for DOCX, PPTX and XLSX files
* Vision-language model support for charts and diagrams
* Improved semantic chunking
* Hybrid keyword + vector retrieval
* Reranking of retrieved chunks
* Source citations with page numbers
* Automatic document summarization
* Downloadable summaries
* Persistent user conversations
* User authentication
* Conversation history across sessions
* Retrieval evaluation and monitoring
* Improved OCR accuracy
* Production-grade vector database deployment

---

## 👨‍💻 Developer

**EasySummarizer** is developed by **AnandAnalytics - Ayush Anand**.

🌐 **[anandanalytics.online](https://anandanalytics.online/)**

---

## 📌 Key Learning Outcomes

The project provides hands-on experience with the complete lifecycle of a modern RAG application:

```text
Unstructured Data
       ↓
Ingestion
       ↓
Chunking
       ↓
Embeddings
       ↓
Vector Database
       ↓
Retrieval
       ↓
Context Construction
       ↓
LLM
       ↓
Conversational Response
```

It demonstrates how individual GenAI components can be combined into a complete, deployable AI application rather than using an LLM as a standalone chatbot.
