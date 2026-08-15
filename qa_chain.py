# Here we build the RAG chain

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatGroq(
    model = "llama-3.3-70b-versatile",
    temperature = 0,
)

prompt = ChatPromptTemplate.from_template(
    """
    You are a helpful assistant that reads the document provided by the user.
    
    Answer ONLY from the provided context.
    If the answer is not in the context, say:
    "I could not find the answer in the uploaded document or image."

    Context: {context}
    Question: {question}
    Answer:
    """
)

# Define parser
parser = StrOutputParser()

def answer_question(retriever, question):

    docs = retriever.invoke(question)

    context = "\n\n".join(doc.page_content for doc in docs)

    chain = prompt | llm | parser

    answer = chain.invoke({
        "context":context,
        "question":question,
    })
    return answer, docs