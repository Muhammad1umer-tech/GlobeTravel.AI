
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain.schema.runnable import RunnableLambda
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from dotenv import load_dotenv
from pyprojroot import here
import json
import os


load_dotenv()
collection_name = "addoc"
llm = ChatOpenAI(model="gpt-3.5-turbo")
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")


def print_x(x):
    """"SELECT Flights.FlightID, Flights.AirlineName, Flights.DepartureCountry, Flights.DepartureCity, Flights.ArrivalCountry, Flights.ArrivalCity, Flights.DepartureTime, Flights.ArrivalTime, Pricing.Price, Pricing.Currency\nFROM Flights\nJOIN Pricing ON Flights.FlightID = Pricing.FlightID\nWHERE Flights.FlightType = 'One Way'\nLIMIT 1;\n```"
        TYPE OF  <class 'str'>
        Error: (sqlite3.ProgrammingError) You can only execute one statement at a time.
        [SQL: SELECT Flights.FlightID, Flights.AirlineName, Flights.DepartureCountry, Flights.DepartureCity, Flights.ArrivalCountry, Flights.ArrivalCity, Flights.DepartureTime, Flights.ArrivalTime, Pricing.Price, Pricing.Currency
        FROM Flights
        JOIN Pricing ON Flights.FlightID = Pricing.FlightID
        WHERE Flights.FlightType = 'One Way'
        LIMIT 1;
        ```]
        (Background on this error at: https://sqlalche.me/e/20/f405)
    """
    if x['query'] .endswith('```'):
        x['query'] = x['query'][:-3] 
        
    return x['query']

def input_to_query(db, query):
    try:
        sqldb_directory = here("data/" + db)
        database = SQLDatabase.from_uri(f"sqlite:///{sqldb_directory}")
        write_query = create_sql_query_chain(llm, database)
        response = write_query.invoke({"question": query})
        print("\ninput_to_query response: ", response)
        return {"status": 200, "output": response}
        
    except Exception as e:
        print(f"error input_to_query: output {str(e)}")
        return {"status":400, "output": str(e)}
    
    
def input_to_rag(query, ragAgent):
    collection_name = "addoc"
    chroma_directory = str(here("data/"+ ragAgent+ ".json_db"))
    vector_store = Chroma(collection_name=collection_name, 
                                embedding_function=embeddings, 
                                persist_directory=chroma_directory)
     
    results = vector_store.similarity_search(query, k=2)
    # print("\ninput_to_rag ", results)
    return results



def func_execute_query(db, query):
    try:
        sqldb_directory = here("data/" + db)
        db = SQLDatabase.from_uri(f"sqlite:///{sqldb_directory}")
        execute_query = QuerySQLDataBaseTool(db=db)
                
        chain = RunnableLambda(print_x) | execute_query
        response = chain.invoke({"query": query})
        print("\nexecute_query ", response)
        if "Error" not in response:
            return {"status": 200, "output": response}
        else: 
            return {"status": 400, "output": response} 
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        return {"status": 400, "output": str(e)}