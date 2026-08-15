# EasySummarizer 📚

EasySummarizer was a multimodal AI-powered document assistant that was developed to allow users to upload PDF documents or images and ask questions about their contents.

The application used **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from uploaded files and generate grounded responses using an LLM. It also supported OCR-based image processing and short-term conversational memory.

The application was deployed using **Streamlit Community Cloud**.

---

## 🚀 Features

EasySummarizer provided the following features:

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

The application followed a modular RAG architecture.

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

The document processing pipeline followed these stages:

### 1. Document Upload

Users uploaded either a PDF document or an image through the Streamlit interface.

### 2. Text Extraction

For PDFs, `PyPDFLoader` was used to extract the document text.

For images, **Tesseract OCR** was used to extract textual information.

### 3. Chunking

The extracted text was divided into smaller overlapping chunks using `RecursiveCharacterTextSplitter`.

The following configuration was used:

```text
Chunk size: 600
Chunk overlap: 100
```

### 4. Embeddings

Each text chunk was converted into a vector representation using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

### 5. Vector Storage

The generated embeddings were stored in a **Chroma vector database**.

Each uploaded file was assigned a unique Chroma collection to prevent different documents from being mixed together.

### 6. Retrieval

When a user asked a question, the question was embedded and compared against the stored vectors.

The system retrieved the **top 4 most relevant chunks**.

### 7. Generation

The retrieved chunks were provided as context to the Groq-hosted LLM.

The model was instructed to answer using the retrieved context and avoid inventing information that was not present in the uploaded content.

---

## 🧠 Short-Term Conversation Memory

EasySummarizer supported short-term conversational memory using Streamlit's `session_state`.

The application retained the most recent conversation messages and passed them to the LLM along with the retrieved document context.

This allowed users to ask follow-up questions such as:

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

The assistant was therefore able to use the previous conversation to understand references and follow-up questions.

The conversation history was cleared whenever the user uploaded a new document or selected the clear-file option.

---

## 🖼️ Image Processing

Images were processed using an OCR pipeline.

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

The image itself was also displayed as a preview in the Streamlit application.

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

The main Streamlit application was responsible for:

* UI rendering
* File uploads
* Image previews
* Session state
* Short-term chat memory
* User interaction
* Displaying retrieved context

### `ingestion_pdf.py`

The PDF ingestion module was responsible for:

* Processing uploaded PDFs
* Extracting text
* Chunking documents
* Creating embeddings
* Storing vectors in Chroma

### `ingestion_images.py`

The image ingestion module was responsible for:

* Processing uploaded images
* Running Tesseract OCR
* Extracting text
* Chunking extracted content
* Creating embeddings
* Storing vectors in Chroma

### `retrieval.py`

The retrieval module was responsible for:

* Loading the appropriate Chroma collection
* Loading the embedding model
* Creating the retriever
* Returning the most relevant document chunks

### `qa_chain.py`

The question-answering module was responsible for:

* Loading the Groq LLM
* Constructing the RAG prompt
* Combining retrieved context with conversation history
* Generating the final response

---

## 🔐 Security

API credentials were kept outside the source code.

During local development, environment variables were used through `.env`.

For Streamlit Community Cloud deployment, the Groq API key was stored using **Streamlit Secrets**.

The `.env` file was excluded from GitHub using `.gitignore`.

Generated Chroma data and the local virtual environment were also excluded from version control.

---

## ☁️ Deployment

The application was deployed using **Streamlit Community Cloud**.

The deployment required:

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

This allowed the OCR functionality to run in the Linux-based Streamlit deployment environment.

---

## ⚙️ Local Setup

The project was developed using a Python virtual environment.

The dependencies were installed using:

```bash
pip install -r requirements.txt
```

The application was started using:

```bash
streamlit run app.py
```

The application was then accessed through the local Streamlit URL.

---

## 🔑 Environment Variables

For local development, the Groq API key was stored in a `.env` file:

```env
GROQ_API_KEY="your_api_key"
```

The `.env` file was not committed to GitHub.

For Streamlit Cloud, the API key was added through the application's **Secrets** configuration.

---

## 🎯 Project Objective

EasySummarizer was developed to demonstrate an end-to-end implementation of a **multimodal RAG application**.

The project combined:

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

The project demonstrated how unstructured user-provided content could be transformed into a searchable knowledge base and used to generate context-aware answers.

---

## 🔮 Future Improvements

The following improvements were identified for future versions:

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

**EasySummarizer** was developed by **AnandAnalytics**.

🌐 **anandanalytics.online**

---

## 📌 Key Learning Outcomes

The project provided hands-on experience with the complete lifecycle of a modern RAG application:

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

It demonstrated how individual GenAI components could be combined into a complete, deployable AI application rather than using an LLM as a standalone chatbot.
