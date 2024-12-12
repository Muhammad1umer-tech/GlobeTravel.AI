from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import Optional

from testing_flight_db import input_to_query, func_execute_query
from prepare_rag import input_to_rag
load_dotenv()

llm = ChatOpenAI(model="gpt-4o")
nodes = ["SQLAgent", "RAGAgent", "SearchToolAgent", "END"]
memory = MemorySaver()
config = {"configurable": {"thread_id": "1"}}
   
class AgentState(BaseModel):
    input: Optional[str] = None
    outputs: Optional[str] = ""
    inputs: list[str] = []
    remaining_input: Optional[str] = None
    query_result: Optional[str] = None
    max_itration: Optional[int] = 0
    is_fulfullied: Optional[bool] = None
    next_node: Optional[str] = None
    output: Optional[str] = None
    database: Optional[str] = None
    error: Optional[str] = None

class Inputrefine(BaseModel):
    inputs: list[str] = Field(
        description="""Divide the input into multiple chunks according to input
        if user requests multiple things.""")
    
def InputRefiner(state: AgentState):
    system = ("""
        System: You are an InputRefiner Agent. Your job is to analyze user input, 
        determine how many distinct commands or requests are being made, 
        and divide the input into smaller chunks. 
        You can update the chunk if you think, specific chunk does not have corrct context.
        
        There would be two types of chunks: 
        * If user ask details about Flights and hotels etc, price, date time country, start rating. 
        * If user ask details like policies, or contact of flights and hotels.
        Examples:
        Input:
        "Tell me about the flight from UK or to UK and its prices as well, and I also want the details of hotels. How can I contact GlobeFlights?"
        
        Output:
        ["Tell me about the flight from UK or to UK, and Prices of flights from UK to UK", 
        "Details of hotels in UK", (uk is being added to have full context and meaning) 
        "Contact details of GlobeFlights"]

        """)
    
    check_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            MessagesPlaceholder(variable_name="input")
        ]
    )
    print("\nBefore state InputRefiner ", state)    
    
    input = state.input
        
    structured_llm = llm.with_structured_output(Inputrefine)
    chain = check_prompt | structured_llm
    response = chain.invoke({"input": [HumanMessage(content=input)]})

    state.inputs = response.inputs
    state.input = response.inputs[0]
    print("\nafter state InputRefiner: ", state)
    return state
    
    
def PrimaryAgent(state: AgentState):
    system_prompt = (
        "You are a Primary Agent Your job is to identify which agent to assign the task to based on the user input."
        "Next agent can be either SQLAgent, RAGAgent or END. \n\n"
        "If input is related to information about Tour and Travel, assign the task to SQLAgent."
        "If input is related to any other query like policies, laws, regulations or how to contact, assign the task to RAGAgent."
        "If input is related to Travel and Tourism, and searching the internet, assign the task to SearchToolAgent."
        "If input is irrelevent, assign the task to END."
        "Output should be the name of the next agent to be assigned the task. Not other than name of the agent.")
    
       
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="input"),
    ])

    chain = prompt | llm | StrOutputParser()
    input = ''
    print("\nBefore Primary Agent ", state)    
    
    if state.is_fulfullied == False:
        input = state.remaining_input
    else :
        input = state.input
    
    response = chain.invoke({"input": [HumanMessage(content=input)]})
    
    state.next_node = response
    return state

class SelectDatabase(BaseModel):
    database: str = Field(
        description="Select the database that is relevant to the input and output.")


Database = ["Flight.db", "Hotel.db"]

def SQLAgent(state: AgentState):
    
    system = ("""You are an SQL Agent with access to two databases: Flight.db and Hotel.db. 
    Select appropriate database based on user input."""
    f"Database: {Database}")
    
    
    check_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            MessagesPlaceholder(variable_name="input")
        ]
    )
    print("\nBefore SQLAgent ", state)    
    
    input = ''
    if state.is_fulfullied == False:
        input = state.remaining_input
    else:
        input = state.input

        
    structured_llm = llm.with_structured_output(SelectDatabase)
    database_selector = check_prompt | structured_llm
    relevance = database_selector.invoke({"input": [HumanMessage(content=input)]})
    
    state.database = relevance.database
    print("\nAfter SQLAgent: ", state.database)
    return state


def ConvertToSql(state: AgentState):
    input = ''
    if state.error != None:
        input = state.error
        
    elif state.is_fulfullied == False:
        input = state.remaining_input
    else:
        input = state.input
    
    database = state.database
    response = input_to_query(database, input)
    print("\nConvertToSql response: ", response)

    if response['status'] == 200:
        state.query_result = response['output']
        state.next_node = 'ExecuteSQL'
    else:
        state.error = f"""My input is {state.input}, but after covnert input to sql query, I am getting this 
        error: {response['output']}. Solve the error and give accurate sql query."""
        state.next_node = 'RegenerateQuery'
        
    print("\nend ConvertToSql state: ", state)
    return state

def ExecuteSQL(state: AgentState):
    query = state.query_result
    database = state.database
    
    response = func_execute_query(database, query)
    print("\nExecuteSQL response: ", response)
    if response['status'] == 200:
        state.query_result = response['output']
        state.next_node = 'GenerateHumanResponse'
    else:
        state.error = f"""My input is {state.input}, but after executing sql, I am getting this 
        error: {response['output']}. Solve the error and give accurate sql query."""
        state.next_node = 'RegenerateQuery'
            
    print("\nend ExecuteSQL state: ", state)
    return state


def RegenerateQuery(state: AgentState):
    print("\nRegenerate Query max_itration ", state.max_itration)
    state.max_itration += 1
    if state.max_itration > 3:
        state.output = "Error, max iteration reached"
        state.next_node = 'END'
    else:
        state.next_node = 'ConvertToSql'
    return state
   
   
def GenerateHumanResponse(state: AgentState):
    query_result = state.query_result
    input = ''
    if state.is_fulfullied == False:
        input = state.remaining_input
    else:
        input = state.input
    
    system_prompt = (
        """You are a human response generator. Generate a response strictly based on the given query result and user input. 
           Do not add any information or assumptions beyond what is provided in the query result. 
           If some info is missing in query result that input have, simple ignore it. Your main responsibiity is to make 
           query result human readable. I am giving input just for the context that what query result is about.

        Query result: {query_result}
        User input: {input}
        """)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt)])

    chain = prompt | llm | StrOutputParser()
    
    response = chain.invoke({"input": input, 'query_result': query_result})
    print("\nresponse GenerateHumanResponse ", response)
    
    state.output = response
    print("\nend GenerateHumanResponse state: ", state)
    return state

class SelectOutputChecker(BaseModel):
    missing_info: Optional[str] = Field(description="Description of any missing information in the response", default=None)
    fulfilled: bool = Field(description="Whether the response fully answers the user's query")

def OutputChecker(state: AgentState):
    system_prompt = (
    """You are an Output Checker responsible for validating if the output addresses the input query. 
       Your goal is to check if output aligns with input. If output is relevent to input, then it is good.
    
    - If the output answers the input, return `fulfilled: True`.
    - If the output does not answers the input, return `fulfilled: False` and specify what is missing in `missing_info`.
    - Do **not** include any extra details that is not mentioned in the input query.
    
    input: {input}
    output: {output}""")

    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
    ])
        
    chain = prompt | llm.with_structured_output(SelectOutputChecker)
    
    output = state.output
    input = state.input

    response = chain.invoke({"output": output, "input": input})
    print("\nOutputChecker response " ,response," ", type(response))
    
    if len(state.inputs) == 1 and response.fulfilled == True: 
        print("\nOutputChecker if ", state.inputs ," ", response)
        state.inputs = state.inputs[1:]
        state.outputs = state.outputs + " " + output
        print("Final Answer: ---> ", state.outputs)
        state.next_node = "END"
    elif len(state.inputs) > 1 and response.fulfilled == True:
        print("\nOutputChecker elif ", state.inputs ," ", response)
        
        state.inputs = state.inputs[1:]
        state.input = state.inputs[0]
        state.outputs = state.outputs + " " + output
        state.next_node = "PrimaryAgent"
    else:
        print("\nOutputChecker else ", state.inputs ," ", response)
        state.remaining_input = response.missing_info
        state.is_fulfullied = False
        state.next_node = "PrimaryAgent"    
    return state
    

def RAGAgent(state: AgentState):
    Database = ["Flight", "Hotel"]
    system = ("""You are an RAG Agent with access to two databases: Flight and Hotel. 
    Select appropriate database based on user input."""
    f"Database: {Database}")
    
    
    check_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            MessagesPlaceholder(variable_name="input")
        ]
    )
    print("\nstate RAGAgent ", state)    
    
    input = ''
    if state.is_fulfullied == False:
        input = state.remaining_input
    else:
        input = state.input
        
    structured_llm = llm.with_structured_output(SelectDatabase)
    database_selector = check_prompt | structured_llm
    relevance = database_selector.invoke({"input": [HumanMessage(content=input)]})
    
    state.database = relevance.database
    print("\nresponse RAGAgent: ", state.database)
    return state

def RAGAgentToQueryToHumanResponse(state: AgentState):
    input = ''
    if state.is_fulfullied == False:
        input = state.remaining_input
    else:
        input = state.input

    docs = input_to_rag(input, state.database)
    
    system_prompt = (
        """You are a human response generator. You will get Two documents, your job is to convert 
        that document to response of input. Don't add any info other than provided document. 
        Your job is to make docs into human response, dont tell us that is it correct or not.
        Just make human response.
            
        docs: {docs}
        User input: {input}
        """)
    
    check_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
        ]
    )
    print("\nstate RAGAgentToQueryToHumanResponse ", state)
    
    chain = check_prompt | llm | StrOutputParser()
    response = chain.invoke({"input": [HumanMessage(content=input)], "docs": docs})
    
    state.output = response
    print("\nresponse RAGAgentToQueryToHumanResponse: ", response)
    return state
     

def SearchToolAgent(state):
    pass

def Where_To_Continue_1(state: AgentState):
    next_node = state.next_node
    print("\nWhere_To_Continue_1 function --->", next_node)

    return next_node

def Where_To_Continue_2(state: AgentState):
    next_node = state.next_node
    print("\nWhere_To_Continue_2 function --->", next_node)

    return next_node

def Where_To_Continue_3(state: AgentState):
    next_node = state.next_node
    print("\nWhere_To_Continue_3 function --->", next_node)

    return next_node

def Where_To_Continue_4(state: AgentState):
    next_node = state.next_node
    print("\nWhere_To_Continue_4 function --->", next_node)

    return next_node
 

workflow = StateGraph(AgentState)

workflow.add_node("InputRefiner", InputRefiner)
workflow.add_node("PrimaryAgent", PrimaryAgent)
workflow.add_node("SQLAgent", SQLAgent)
workflow.add_node("ConvertToSql", ConvertToSql)
workflow.add_node("ExecuteSQL", ExecuteSQL)
workflow.add_node("GenerateHumanResponse", GenerateHumanResponse)
workflow.add_node("RegenerateQuery", RegenerateQuery)
workflow.add_node("OutputChecker", OutputChecker)

workflow.add_node("RAGAgent", RAGAgent)
workflow.add_node("RAGAgentToQueryToHumanResponse", RAGAgentToQueryToHumanResponse)

workflow.add_node("SearchToolAgent", SearchToolAgent)

workflow.add_edge(START, "InputRefiner")

workflow.add_edge("InputRefiner", "PrimaryAgent")
workflow.add_conditional_edges(
    "PrimaryAgent",
    Where_To_Continue_1,
    {
        "RAGAgent": "RAGAgent",
        "SearchToolAgent": "SearchToolAgent",
        "SQLAgent": "SQLAgent",
        "END": END
    }
)
workflow.add_edge("SQLAgent", "ConvertToSql")
workflow.add_edge("ConvertToSql", "ExecuteSQL")
workflow.add_conditional_edges(
    "ExecuteSQL",
    Where_To_Continue_2,
    {
        "RegenerateQuery": "RegenerateQuery",
        "GenerateHumanResponse": "GenerateHumanResponse",
    }
)
workflow.add_conditional_edges(
    "RegenerateQuery",
    Where_To_Continue_3,
    {
        "ConvertToSql": "ConvertToSql",
        "END": END
    }
)
workflow.add_edge("GenerateHumanResponse", "OutputChecker")
workflow.add_edge("RAGAgentToQueryToHumanResponse", "OutputChecker")

workflow.add_conditional_edges(
    "OutputChecker",
    Where_To_Continue_4,
    {
        "PrimaryAgent": "PrimaryAgent",
        "END": END
    }
)
workflow.add_edge("RAGAgent", "RAGAgentToQueryToHumanResponse")
workflow.add_edge("SearchToolAgent", END)

graph = workflow.compile(checkpointer=memory)

def save_graph():
    graph_png_data = graph.get_graph().draw_mermaid_png()
    with open("./langgraph_output.png", "wb") as f:
        f.write(graph_png_data)

def run():
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("\nGoodbye!")
            break

        events = graph.invoke({"input": user_input})
        print("\nevents ", events)
        for event in events:
            for value in event.values():
                print("\nAssistant:", value)



def run_graph(input):
    result = graph.invoke({"input": input})
    return result['outputs']
    
# result = graph.invoke({"input": "tell me about the flight to uk and its prices as well, and i also want the details of hotel in usa. How can I contact you guys?"})
# result = graph.invoke({"input": "tell me about the flight from usa and hotels as well. How can i contect to book a flight and policies of flight and hotels"})
# result = graph.invoke({"input": "I wanna go to use for a tour, suggest me flights, dates and hotels in USA. what is the cancellation policy."})
# print("results", result['outputs'])
# save_graph()


