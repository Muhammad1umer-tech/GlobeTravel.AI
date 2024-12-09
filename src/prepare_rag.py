from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from dotenv import load_dotenv
from pyprojroot import here
from uuid import uuid4
import json
import os
load_dotenv()

collection_name = "addoc"
llm = ChatOpenAI(model="gpt-4o-mini")
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")   


def create_chroma(chroma_name, chroma_directory):
    # Check if directory doesn't exist
    print(chroma_directory)
    if not os.path.exists(chroma_directory):
        try:        
            Chroma(collection_name=collection_name, 
                                embedding_function=embeddings, 
                                persist_directory=chroma_directory)
            print("Successfully created the database")
            return 1
        
        except Exception as e:
            print(f"Error creating database: {str(e)}")
            return -1
        
    print("Database Already exists")
    return 2


def load_json(file_path): 
    datas = []
    with open(file_path, 'r') as file:
        datas = json.load(file)  # Parses the file content into a Python dictionary or list
    return datas
    

def load_data_to_chromadb(datas, chroma_directory):
    try:
        vector_store = Chroma(collection_name=collection_name, 
                                    embedding_function=embeddings, 
                                    persist_directory=chroma_directory)
        
        vector_store.add_documents(documents=datas)
        print("Documents added to Chroma")
        return True
    except Exception as e:
        print(f"Error -> load_data_to_chromadb: {str(e)}")
        return False
    

def document_loader(file_path, chroma_directory):
    try:
        whole_data = []
        datas = load_json(file_path) # []
        

        for index, data in enumerate(datas):
            current_entry = ", ".join(list(data.keys())) + ": " + ", ".join(list(data.values()))
            doc = Document(
                page_content=current_entry,
            )
            whole_data.append(doc)

        load_data_to_chromadb(whole_data, chroma_directory) 
        print("Successfully loaded data to Chroma")   
        return True
        
    except Exception as e:
        print(f"Error -> document_loader: {str(e)}")
        return False

def test_query(query, chroma_directory):
    vector_store = Chroma(collection_name=collection_name, 
                                embedding_function=embeddings, 
                                persist_directory=chroma_directory)
     
    results = vector_store.similarity_search(query, k=2)
    for res in results:
        print(f"\n\n* {res.page_content} [{res.metadata}]")
       


def input_to_rag(query, ragAgent):
    collection_name = "addoc"
    chroma_directory = str(here("data/"+ ragAgent+ ".json_db"))
    vector_store = Chroma(collection_name=collection_name, 
                                embedding_function=embeddings, 
                                persist_directory=chroma_directory)
     
    results = vector_store.similarity_search(query, k=2)
    # print("\ninput_to_rag ", results)
    return results
               
def test_connection():
    vector_store = Chroma(collection_name=collection_name, 
                                embedding_function=embeddings, 
                                persist_directory=chroma_directory)
    print(vector_store._collection.peek())  # See a few documents

    
# if __name__ == "__main__":
#     json_folder = here("data/unstructured_docs/json")
    
    
#     # Process all JSON files in the folder
#     for json_file in os.listdir(json_folder):
#         chroma_directory = str(here("data/"+json_file+"_db"))
#         # Create Chroma DB if it doesn't exist
#         flag = create_chroma(json_file, chroma_directory)
#         if flag == -1:
#             exit()
            
#         if json_file.endswith('.json'):
#             file_path = os.path.join(json_folder, json_file)
            
#             if flag == 1:  # Only load documents if DB was just created
#                 print(f"Processing {json_file}...")
#                 flag = document_loader(file_path, chroma_directory)
#                 if flag == False:
#                     print(f"Failed to load {json_file}")
#                     continue
    

# print(input_to_rag("how to contact for booking", "Flight"))
    
    
    