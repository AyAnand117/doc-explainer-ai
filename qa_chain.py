# Here we build the RAG chain
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatGroq(
    model = "llama-3.3-70b-versatile",
    temperature = 0.01,
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
    - Answer using the document context when appropriate.
    - Use the conversation history to understand follow-up questions.
    - Do not invent information.
    - If the answer isn't available in the document, say:
      "I could not find the answer in the uploaded document."
    """
)

# Define parser
parser = StrOutputParser()

def answer_question(retriever, question, chat_history):

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