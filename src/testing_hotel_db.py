from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain.schema.runnable import RunnableLambda, RunnableParallel
from langchain_community.agent_toolkits import create_sql_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from operator import itemgetter
from dotenv import load_dotenv
from pyprojroot import here

load_dotenv()
llm = ChatOpenAI(model="gpt-3.5-turbo")

def test_database():    
    sqldb_directory = here("data/Hotel.db")
    db = SQLDatabase.from_uri(f"sqlite:///{sqldb_directory}")
    print(db.run("select * from hotels"))


def remove_extrachars_from_end_of_query(x):
    print(repr(x))
    
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
    if x .endswith('```'):
        x = x[:-3] 
        
    print("\nTYPE OF ", type(x))
    return x

def print_(x):
    print(x)
    return x


def query_to_execity(query):
    try:
        sqldb_directory = here("data/Flight.db")
        db = SQLDatabase.from_uri(f"sqlite:///{sqldb_directory}")
        execute_query = QuerySQLDataBaseTool(db=db)
        response = execute_query.invoke(query)
        print("\n", response)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
        
def input_to_query(db, query):
    try:
        sqldb_directory = here("data/" + db)
        db = SQLDatabase.from_uri(f"sqlite:///{sqldb_directory}")
        execute_query = QuerySQLDataBaseTool(db=db)
        write_query = create_sql_query_chain(llm, db)
        chain = write_query | RunnableLambda(remove_extrachars_from_end_of_query) | execute_query
        response = chain.invoke({"question": query})
        print("\n", response)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def query_testing_hotel_bot(query):    
    sqldb_directory = here("data/Flight.db")
    db = SQLDatabase.from_uri(f"sqlite:///{sqldb_directory}")

    execute_query = QuerySQLDataBaseTool(db=db)     #[(0,8)]
    write_query = create_sql_query_chain(llm, db)   #SELECT COUNT(*) as EmployeeCount FROM Employee;

    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, 
        and SQL result, answer the user question.
        Question: {question}
        SQL Query: {query}
        SQL Result: {result}
        Answer: """)
    
    chain = (
        RunnablePassthrough.assign(query=write_query | RunnableLambda(remove_extrachars_from_end_of_query))
        .assign(result=itemgetter("query") | execute_query)
        | answer_prompt
        | llm
        | StrOutputParser()
    )

    response =chain.invoke({"question": query})
    print(response)

# input_to_query("Hotel.db", "tell me the hotels in usa")

# print(query_to_execity("""SELECT * from Flights WHERE "DepartureCountry" = 'UK' or "ArrivalCountry" = 'UK' LIMIT 5;"""))

# query_testing_hotel_bot("Tell me about the flight from or to uk")

