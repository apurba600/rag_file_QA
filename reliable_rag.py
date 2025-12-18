
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from helper_functions import (
    EmbeddingProvider,
    replace_t_with_space,
    get_langchain_embedding_provider
)
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

def encode_pdf(path, chunk_size=500, chunk_overlap=100):
    loader = PyPDFLoader(path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )

    docs = splitter.split_documents(documents)
    cleaned_docs = replace_t_with_space(docs)

    embeddings = get_langchain_embedding_provider(
        EmbeddingProvider.OPENAI
    )

    vectorstore = FAISS.from_documents(
        cleaned_docs,
        embeddings
    )

    return vectorstore

def get_retriever(vectorstore, k=4):
    return vectorstore.as_retriever(
        search_kwargs={"k": k}
    )

def answer_with_llm(retriever, question):
    # Retrieve docs
    retrieved_docs = retriever.invoke(question)

    # 🔹 ADD THIS PART
    retrieved_docs_content = [
        r_doc.page_content for r_doc in retrieved_docs
    ]

    # Build context
    context = "\n\n".join(retrieved_docs_content)

    # LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a helpful assistant. Answer the question ONLY using the provided context. "
            "If the answer is not in the context, say you don't know."
            "If the question asks for an account number, return ONLY the number."
            "Do NOT include timestamps, prefixes, or extra words."
            "If the answer is not present, say 'I don't know'."
        ),
        (
            "human",
            "Context:\n{context}\n\nQuestion:\n{question}"
        )
    ])

    response = llm.invoke(
        prompt.format(
            context=context,
            question=question
        )
    )

    return response.content
