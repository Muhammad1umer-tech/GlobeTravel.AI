from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import Optional

from Baseclass import AgentState
from nodes import InputRefiner, HumanInALoop, PrimaryAgent, SQLAgent, ConvertToSql, ExecuteSQL, GenerateHumanResponse, RegenerateQuery, OutputChecker, RAGAgent, RAGAgentToQueryToHumanResponse, SearchToolAgent, OutputNode
from nodes import Where_To_Continue_1, Where_To_Continue_2, Where_To_Continue_3, Where_To_Continue_4, Where_To_Continue_5

memory = MemorySaver()
config = {"configurable": {"thread_id": "1"}}
   

workflow = StateGraph(AgentState)

workflow.add_node("InputRefiner", InputRefiner)
workflow.add_node("PrimaryAgent", PrimaryAgent)
workflow.add_node("HumanInALoop", HumanInALoop)
workflow.add_node("SQLAgent", SQLAgent)
workflow.add_node("ConvertToSql", ConvertToSql)
workflow.add_node("ExecuteSQL", ExecuteSQL)
workflow.add_node("GenerateHumanResponse", GenerateHumanResponse)
workflow.add_node("RegenerateQuery", RegenerateQuery)
workflow.add_node("OutputChecker", OutputChecker)
workflow.add_node("OutputNode", OutputNode)

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
    "HumanInALoop",
    Where_To_Continue_5,
    {
        "PrimaryAgent": "PrimaryAgent",
        "OutputNode": "OutputNode"
    }
)
workflow.add_conditional_edges(
    "RegenerateQuery",
    Where_To_Continue_3,
    {
        "ConvertToSql": "ConvertToSql",
        "HumanInALoop": "HumanInALoop"
    }
)
workflow.add_edge("GenerateHumanResponse", "OutputChecker")
workflow.add_edge("RAGAgentToQueryToHumanResponse", "OutputChecker")

workflow.add_conditional_edges(
    "OutputChecker",
    Where_To_Continue_4,
    {
        "PrimaryAgent": "PrimaryAgent",
        "OutputNode": "OutputNode"
    }
)
workflow.add_edge("RAGAgent", "RAGAgentToQueryToHumanResponse")

workflow.add_edge("OutputNode", END)
workflow.add_edge("SearchToolAgent", END)

graph = workflow.compile(checkpointer=memory, interrupt_before=["HumanInALoop"],)
# graph = workflow.compile()

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
    # result = graph.invoke({"input": input}, config)
    snapshot = graph.get_state(config)
    print("run graph ", snapshot)
        
    first_arg_message = {"input": input}
    
    if(len(snapshot.next) != 0 and snapshot.next[0] == 'HumanInALoop'):
        print("snapshot.values ",  snapshot.values)
        state = snapshot.values
        state['input'] = input            
        graph.update_state(config, state)
        first_arg_message = None
            
    
    result = graph.invoke(first_arg_message, config)
    return result['output']
    
# result = graph.invoke({"input": "tell me about the flight to uk "})
# result = graph.invoke({"input": "tell me about the flight to uk and its prices as well, and i also want the details of hotel in usa. How can I contact you guys?"})
# result = graph.invoke({"input": "tell me about the flight from usa and hotels as well. How can i contect to book a flight and policies of flight and hotels"})
# result = graph.invoke({"input": "I wanna go to use for a tour, suggest me flights, dates and hotels in USA. what is the cancellation policy."})
# print("results", result['outputs'])
save_graph()
