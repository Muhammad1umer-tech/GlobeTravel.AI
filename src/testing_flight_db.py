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
    sqldb_directory = here("data/Flight.db")
    db = SQLDatabase.from_uri(f"sqlite:///{sqldb_directory}")
    print(db.run("""SELECT "FlightID", "AirlineName", "DepartureCity", "ArrivalCity", "DepartureTime", "ArrivalTime"
FROM Flights
WHERE DepartureCountry = 'India' AND ArrivalCountry = 'USA'
LIMIT 5;"""))

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

def print_(x):
    print(x)
    return x

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
        

def query_testing_flight_bot(query):    
    sqldb_directory = here("data/Flight.db")
    print("sqldb_directory ", sqldb_directory)
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
        RunnablePassthrough.assign(query=write_query | RunnableLambda(print_x)).assign(
            result=itemgetter("query") | execute_query)
        | answer_prompt
        | llm
        | StrOutputParser())

    response =chain.invoke({"question": query})
    print(response)

def get_db_schema(db_name):
    try:
        sqldb_directory = here("data/" + db_name)
        db = SQLDatabase.from_uri(f"sqlite:///{sqldb_directory}")
        
        # Get all table names
        tables = db.run("SELECT name FROM sqlite_master WHERE type='table';")
        print("\nTables in database:")
        print(tables)
        
        # Get columns for each table
        for table in tables.split('\n'):
            table = table.strip()
            if table:
                columns = db.run(f"PRAGMA table_info({table});")
                print(f"\nColumns in {table} table:")
                print(columns)
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage:
# print(func_execute_query("Flight.db", """SELECT "FlightID", "AirlineName", "DepartureCountry", "DepartureCity", "ArrivalCountry", "ArrivalCity", "DepartureTime", "ArrivalTime", "FlightType"
# FROM "Flights" WHERE "DepartureCountry" = 'UK' AND "ArrivalCountry" = 'UK' LIMIT 5;"""))
# get_db_schema("Flight.db")

# input_to_query("Flight.db", "I need to have a one way flight. Tell me about it and its price as well")
# query_testing_flight_bot("Tell me about the flight from or to ukc")



