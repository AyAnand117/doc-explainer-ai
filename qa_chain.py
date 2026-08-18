# Here we build the RAG chain
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatGroq(
    model = "qwen/qwen3.6-27b",
    temperature = 0.05,
)

prompt = ChatPromptTemplate.from_template(
    """
    You are a helpful assistant named EasySummarizer that reads the document provided by the user.
    
    Use the document context and recent conversation to answer
    the user's question.

    Recent conversation:
    {chat_history}

    Document context:
    {context}

    Current question:
    {question}

    Rules:

    1. Answer using the document context when the question relates
        to the uploaded document or image.

    2. Use the recent conversation to understand follow-up questions
        and references such as:
        - "it"
        - "that"
        - "the previous point"
        - "the second section"
        - "explain this further"

    3. Do not invent information that is not supported by the
        document context.

    4. If the answer cannot be found in the document context, say:

        "I could not find the answer in the uploaded document."

    5. Keep the answer clear and concise.
    """
)


parser = StrOutputParser()

def answer_question(retriever, question, chat_history):
    """
        Retrieves relevant document chunks and generates an answer
        using the uploaded document and recent conversation history.

        Args:
            retriever: Chroma retriever for the current document.
            question: User's current question.
            chat_history: Recent conversation messages.

        Returns:
            tuple:
                answer: Generated response.
                docs: Retrieved document chunks.
    """
    docs = retriever.invoke(question)

    context = "\n\n".join(doc.page_content for doc in docs)

    history = "\n".join(f"{msg['role']}:{msg['content']}" for msg in chat_history)

    chain = prompt | llm | parser

    answer = chain.invoke({
        "context":context,
        "question":question,
        "chat_history":chat_history,
    })
    return answer, docs
