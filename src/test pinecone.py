from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pyprojroot import here
import time
from uuid import uuid4
load_dotenv()

pc = Pinecone()
index_name = "addoc"
llm = ChatOpenAI(model="gpt-4o-mini")
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")   


def create_index():
    try:
        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        if index_name not in existing_indexes:
            print(f"Index {index_name} not found, creating...")
            pc.create_index(
                name=index_name,
                dimension=3072,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            while not pc.describe_index(index_name).status["ready"]:
                time.sleep(1)
            print(f"Index {index_name} created successfully")
        else:
            print(f"Index {index_name} already exists")

        index = pc.Index(index_name)
        return index
    except Exception as e:
        print(f"Error creating/accessing index: {str(e)}")
        return None

def document_loader(file_path):
    try:
        pc_index = pc.Index(index_name)    
        loader = PyPDFLoader(file_path)
        pages = loader.lazy_load()
        
        # Split your data up into smaller documents with Chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        documents = text_splitter.split_documents(pages)
        uuids = [str(uuid4()) for _ in range(len(documents))]
        
        # Pincecone working / add documents to pincecone
        # PineconeVectorStore.from_documents(documents, embeddings, index_name="indexname") 
        vector_store = PineconeVectorStore(index=pc_index, embedding=embeddings)
        vector_store.add_documents(documents=documents, ids=uuids)
        print("Documents added to Pinecone")
        return True
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    
    
def test_query(query):
    pc_index = pc.Index(index_name)
    vector_store = PineconeVectorStore(embedding=embeddings, index=pc_index)
    results = vector_store.similarity_search(query, k=2)
    for res in results:
        print(f"\n* {res.page_content} [{res.metadata}]")
        
    
if __name__ == "__main__":
    # Create the index
    index = create_index()
    if index is None:
        exit()
        
    pdf_path = here("data/unstructured_docs/Hotel.pdf")
    flag  = document_loader(pdf_path)
    if flag is False:
        #to see if document loader is working or not 
        exit()
    
    test_query("Amenities and Services")
    
    