from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from pyprojroot import here
import yaml
import os


class prepareDatabase:
    
    def __init__(self,
            doc_dir: str,
            chunk_size: int,
            chunk_overlap: int,
            embedding_model: str,
            vectordb_dir: str,
            collection_name: str) -> None:
        
        self.doc_dir = doc_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = embedding_model
        self.vectordb_dir = vectordb_dir
        self.collection_name = collection_name
        
        
    def run():
        pass        
