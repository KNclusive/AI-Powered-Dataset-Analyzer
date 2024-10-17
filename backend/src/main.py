from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, create_react_agent
from langchain.tools.render import render_text_description
from langchain_experimental.tools import PythonAstREPLTool
from Agent_tools import df1, df2, get_dataset_info_tool, get_dataset_indexing_structure, get_value_from_df
from Agent_prompts import get_schema_query_prompt, get_supervisor_prompt
from typing import Dict, TypedDict, Annotated, Sequence, List
import operator
import json
import uuid

llm = ChatOpenAI(model="gpt-4o-mini")

# Setup for response validation
import pandas as pd
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Literal

class FinalResponse(BaseModel):
    original_user_query: str = Field(description="The user's original natural language query.")
    constructed_pandas_query: str = Field(description="The pandas query constructed to answer user's query.")
    output: str = Field(description="The result of the executed query.")
    charts: Optional[List[Dict]] = Field(default=None, description="List of charts generated, if any.")

class SupervisorResponse(BaseModel):
    next_action: Literal["FINISH", "EXECUTE_QUERY", "Schema_Query_Agent"]
    sub_queries: List[str] = Field(description="List containing Query or Sub-Queries.")
    dataset: List[str] = Field(description="Dataset to query (df1 or df2).")
    final_response: Optional[FinalResponse] = None

class SchemaQueryResponse(BaseModel):
    final_query: str = Field(description="The constructed single-line or multi-line Pandas query.")

def validate_response(response):
    try:
        final_response = SupervisorResponse.model_validate(response)
        return_answer = final_response.final_response
        return return_answer.json() if return_answer else None #converting to string
    except Exception as e:  
        return f"Error parsing final response: {e}"

# Initialize MemorySaver
memory = MemorySaver()

# Initialize tools
python_repl_tool = PythonAstREPLTool(locals={'df1': df1, 'df2': df2})
schema_query_tools = [get_dataset_info_tool, get_dataset_indexing_structure, get_value_from_df]
tool_node = ToolNode(schema_query_tools + [python_repl_tool])

# Define the state
class AgentState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage | SystemMessage], operator.add]
    next: str
    return_values: Annotated[List[Dict], operator.add]

# Create the graph
workflow = StateGraph(AgentState)

supervisor_parser = PydanticOutputParser(pydantic_object=SupervisorResponse)
supervisor_prompt = get_supervisor_prompt()

# Define the Supervisor node
supervisor_formatted_prompt = ChatPromptTemplate.from_messages([
    ("system", supervisor_prompt),
    MessagesPlaceholder(variable_name="messages"),
    (
        "system",
        "Given the conversation above, what should be the next action? "
        "Select one of: {options}",
    ),
]).partial(options=str(["FINISH", "EXECUTE_QUERY", "Schema_Query_Agent"]), members=", ".join(["Schema_Query_Agent"]), format_instructions=supervisor_parser.get_format_instructions())

def supervisor(state: AgentState) -> AgentState:
    print("inside Supervisor now.\n")
    supervisor_chain = supervisor_formatted_prompt | llm.with_structured_output(SupervisorResponse)
    response = supervisor_chain.invoke(state)
    print("Supervisor Response is: \n", response)
    next_action = response.next_action

    if next_action == "Schema_Query_Agent":
        print("Supervisor said next_action should be Schema Query agent")
        state['next'] = "Schema_Query_Agent"
        state['return_values'].append({"sub_queries": response.sub_queries, "dataset": response.dataset}, name='Supervisor')
    elif next_action == "EXECUTE_QUERY":
        print("Supervisor says Execute the query: \n", response.final_response.constructed_pandas_query)
        state['next'] = "EXECUTE_QUERY"
        state['return_values'].append({"query": response.final_response.constructed_pandas_query}, name='Supervisor')
    elif next_action == "FINISH":
        final_response = validate_response(response)
        print("Supervisor says finish: \n", final_response)
        if final_response:
            state['messages'].append(HumanMessage(content=final_response, name="Supervisor"))
        else:
            state['messages'].append(HumanMessage(content="No final response provided.", name="Supervisor"))
        state['next'] = "FINISH"
    else:
        state['messages'].append(HumanMessage(content="Unexpected error", name="Supervisor"))
        state['next'] = "FINISH"

    return state

# Define the Schema Query node
schema_query_parser = JsonOutputParser(pydantic_object=SchemaQueryResponse)
schema_query_prompt = get_schema_query_prompt()
schema_query_formatted_prompt = ChatPromptTemplate.from_messages([
    ("system", schema_query_prompt),
    MessagesPlaceholder(variable_name="messages"),
    ("human", "Construct a pandas query to answer the user's question."),
]).partial(tools_list=render_text_description(schema_query_tools), tool_names=", ".join(t.name for t in schema_query_tools), format_instructions=schema_query_parser.get_format_instructions())

schema_query_agent = create_react_agent(llm, tools=tool_node, state_modifier=schema_query_formatted_prompt)

def schema_query(state: AgentState) -> AgentState:
    print("Now inside Schema Query Agent.\n")
    last_return_value = state["return_values"][-1]
    print("Printing last return value inside schema query agent: \n", last_return_value)

    sub_queries = last_return_value.get("sub_queries")
    dataset = last_return_value.get("dataset")
    print("The subqueries the schema query agent got is: \n", sub_queries)
    print("The datasets the schema query agent got is: \n", dataset)
    results = []
    for query, df in zip(sub_queries, dataset):
        print("Query: \n", query)
        response = schema_query_agent.invoke({'Query': query, 'df':df})
        print("Schema query agent response: \n", response.pretty_print())
        try:
            parsed_response = schema_query_parser.parse(response.content)
            print("Parsing schema query agents response: \n", parsed_response)
        except ValidationError as e:
            parsed_response = {'final_query': "print('Could not Construct Pandas Query!')"}
        sq = parsed_response.get['final_query']
        results.append(sq)
        state['messages'].append(HumanMessage(content=f'The pandas query {sq} is generated.', name='Schema_Query_Agent'))

    state['return_values'].append({"constructed_query": results}, name='Schema_Query_Agent')
    return state

# Define the Execute Query node
def execute_query(state: AgentState) -> AgentState:
    print("Inside execute Query now.")
    last_return_value = state["return_values"][-1]
    print("Printing last return value inside Execute Query: \n", last_return_value)
    queries = last_return_value.get("constructed_queries")
    print("The queries to be executed: \n", queries)
    
    result=[]
    for query in queries:
        try:
            res = tool_node.invoke({"tool": "python_repl_ast", "tool_input": query})
            print("The result after query execution: \n", res)
            if isinstance(result, (pd.DataFrame, pd.Series)):
                fres=res.to_string()
            else:
                fres=str(res)
        except Exception as e:
            result.append(f"Error in {query} execution")

        result.append(fres)
        state['messages'].append(HumanMessage(content=f'The pandas query {query} is executed; the result is {fres}.', name='EXECUTE_QUERY'))

    state['return_values'].append({"result": result}, name='EXECUTE_QUERY')
    return state

# Add nodes to the graph
workflow.add_node("Supervisor", supervisor)
workflow.add_node("Schema_Query_Agent", schema_query)
workflow.add_node("EXECUTE_QUERY", execute_query)

# Add edges to the graph
workflow.add_edge("Schema_Query_Agent", "Supervisor")
workflow.add_edge("EXECUTE_QUERY", "Supervisor")

# Set the entry point
workflow.add_edge(START, "Supervisor")

# Set conditional edges from Supervisor
workflow.add_conditional_edges(
    "Supervisor",
    lambda x: x["next"],
    {
        "Schema_Query_Agent": "Schema_Query_Agent",
        "Supervisor": "Supervisor",
        "FINISH": END
    }
)

# Compile the graph
graph = workflow.compile(checkpointer=memory)

# Example usage
def main():
    user_query = "What is the ratio of male population from sustainability survey (df1) and christmas survey (df2)?"
    state = {"messages": [HumanMessage(content=user_query)], "return_values": []}

    thread_id = str(uuid.uuid4())
    
    # Create a config dictionary with the thread_id
    config = {"configurable": {"thread_id": thread_id}}
    
    for output in graph.stream(state, config=config):
        if "final_response" in output["return_values"][-1]:
            print("Final Response:", output["return_values"][-1]["final_response"])
            break
        else:
            print("Intermediate Step:", output["return_values"][-1])

if __name__ == "__main__":
    main()