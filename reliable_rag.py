
# Import libraries
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from helper_functions import (
    EmbeddingProvider,
    replace_t_with_space,
    get_langchain_embedding_provider
)

def encode_pdf(pdf_path, chunk_size=1000, chunk_overlap=200):
    """
    Encodes a PDF file into a vector store using OpenAI embeddings.

    Args:
        pdf_path: The path to the PDF file to process.
        chunk_size: The desired size of each text chunk (default: 1000).
        chunk_overlap: The amount of overlap between consecutive chunks (default: 200).

    Returns:
        A FAISS vector store containing the encoded document content.
    """
    try:
        # Load PDF document
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        
        texts = text_splitter.split_documents(documents)
        cleaned_texts = replace_t_with_space(texts)

        # Create embeddings
        embeddings = get_langchain_embedding_provider(EmbeddingProvider.OPENAI)

        # Create and return vector store
        vectorstore = FAISS.from_documents(cleaned_texts, embeddings)
        return vectorstore
        
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")

def get_retriever(vectorstore, k=2):
    """
    Creates a retriever from a vector store.
    
    Args:
        vectorstore: The vector store to create a retriever from.
        k: Number of documents to return (default: 2).
        
    Returns:
        A retriever object.
    """
    return vectorstore.as_retriever(search_kwargs={"k": k})


