from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain.tools.render import render_text_description
from langchain_experimental.tools import PythonAstREPLTool
from Agent_tools import df1, df2, get_dataset_info_tool, get_dataset_indexing_structure, get_value_from_df
from Agent_prompts import get_schema_query_prompt, get_supervisor_prompt
from typing import Dict, TypedDict, Annotated, Sequence, List
import operator
import json
import functools
import uuid

llm = ChatOpenAI(model="gpt-4o-mini")

# Setup for response validation
import pandas as pd
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Literal

class FinalResponse(BaseModel):
    original_user_query: str = Field(description="The user's original natural language query.")
    constructed_pandas_query: str = Field(description="The Final panda's query constructed to answer user's query.")
    output: str = Field(description="The result of the executed panda's query.")
    charts: Optional[List[Dict]] = Field(default=None, description="List of charts generated, if any.")

class SupervisorResponse(BaseModel):
    next_action: Literal["FINISH", "EXECUTE_QUERY", "Schema_Query_Agent"]
    sub_queries: List[str] = Field(description="List containing Query or Sub-Queries.")
    final_response: Optional[FinalResponse] = None

class SchemaQueryResponse(BaseModel):
    final_query: str = Field(description="Constructed single-line panda's query.")

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

# Define the state
class AgentState(TypedDict):
    next: str
    messages: Annotated[Sequence[HumanMessage | AIMessage | SystemMessage], operator.add]
    sub_queries: Optional[List[str]]
    constructed_queries: Optional[List[str]]
    current_index: Optional[int]
    results: Optional[List[str]]

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
        squeries = response.sub_queries
        state['sub_queries'] = squeries
        state['current_index'] = 0
        state['next'] = next_action
        state['messages'].append(HumanMessage(content=f'Queries: {squeries}', name="Supervisor"))
    elif next_action == "EXECUTE_QUERY":
        state['next'] = next_action
    elif next_action == "FINISH":
        final_response = validate_response(response)
        print("Supervisor says finish: \n", final_response)
        if final_response:
            state['messages'].append(HumanMessage(content=final_response, name="Supervisor"))
        else:
            state['messages'].append(HumanMessage(content="No final response provided.", name="Supervisor"))
        state['next'] = next_action
    else:
        state['messages'].append(HumanMessage(content="Unexpected error", name="Supervisor"))
        state['next'] = next_action

    return state

# Define the Schema Query node
schema_query_parser = JsonOutputParser(pydantic_object=SchemaQueryResponse)
schema_query_prompt = get_schema_query_prompt()
schema_query_formatted_prompt = ChatPromptTemplate.from_messages([
    ("system", schema_query_prompt),
    MessagesPlaceholder(variable_name="messages"),
    ("human", "Construct a pandas query to answer the question."),
]).partial(tools_list=render_text_description(schema_query_tools), tool_names=", ".join(t.name for t in schema_query_tools), format_instructions=schema_query_parser.get_format_instructions())

def schema_query(state, agent):
    print("Now inside Schema Query Agent.\n")
    index = state.get('current_index', 0)
    print("Current index is:\n", index)
    sub_queries = state.get('sub_queries', [])
    if not sub_queries:
        # No sub-queries to process
        state['messages'].append(HumanMessage(content=f"Did not recieve any sub-queries to construct panda's query", name='Schema_Query_Agent'))
        state['next'] = 'Supervisor'
        return state
    
    print("Sub queries are:\n", sub_queries)
    if index >= len(sub_queries):
        print("Index greater than equal")
        state['messages'].append(HumanMessage(content=f"Current Index indicates all sub-queries have been processed.", name='Schema_Query_Agent'))
        # All sub-queries have been processed
        state['next'] = "Supervisor"
        return state

    query_in_play = sub_queries[index]
    print("Query in play is:\n", query_in_play)

    agent_state = {'messages': [HumanMessage(content=query_in_play, name="Supervisor")]}

    result = agent.invoke(agent_state)
    agent_message = result["messages"][-1].content
    print("Agent message printing:\n",agent_message)
    try:
        output = schema_query_parser.parse(agent_message)
        print("Parsing schema query agents response: \n", output)
    except ValidationError as e:
        print(f"Validation error {e}")
        output = {'final_query': "print('Could not Construct Pandas Query!')"}

    query_cons = output.get("final_query")
    print(f"The constructed Pandas query is:\n", query_cons)
    state['constructed_queries'].append(query_cons)
    state['messages'].append(HumanMessage(content=f'Pandas query for {query_in_play} is:\n{query_cons}', name='Schema_Query_Agent'))
    
    state['current_index'] = index + 1
    if state['current_index'] < len(sub_queries):
        # There are more sub-queries to process
        state['next'] = "Schema_Query_Agent"
    else:
        # All sub-queries processed
        state['next'] = "EXECUTE_QUERY"

    return state

schema_query_agent = create_react_agent(llm, tools=schema_query_tools, state_modifier=schema_query_formatted_prompt)
schema_query_node = functools.partial(schema_query, agent=schema_query_agent)

# Define the Execute Query node
def execute_query(state: AgentState) -> AgentState:
    print("Inside execute Query now.")
    queries_to_execute = state['constructed_queries']
    print("Printing queries to execute inside Execute Query: \n", queries_to_execute)

    if not queries_to_execute:
        print("Could not find queries to execute.")
        state['messages'].append(HumanMessage(content=f'No queries to execute', name='EXECUTE_QUERY'))
        return state

    for query in queries_to_execute:
        print(f"Executing {query} now")
        try:
            res = python_repl_tool.run(query)
            print("The result after query execution: \n", res)
        except Exception as e:
            res = f"Error in {query} execution"

        if isinstance(res, (pd.DataFrame, pd.Series)):
            state['results'].append(res.to_string())
        else:
            state['results'].append(str(res))

        state['messages'].append(HumanMessage(content=f'The pandas query {query} is executed; the result is {res}.', name='EXECUTE_QUERY'))
    return state

# Create the graph
workflow = StateGraph(AgentState)

# Set the entry point
workflow.add_edge(START, "Supervisor")

# Add nodes to the graph
workflow.add_node("Supervisor", supervisor)
workflow.add_node("Schema_Query_Agent", schema_query_node)
workflow.add_node("EXECUTE_QUERY", execute_query)

# Add edges to the graph
workflow.add_edge("EXECUTE_QUERY", "Supervisor")

# Set conditional edges from Supervisor
workflow.add_conditional_edges(
    "Supervisor",
    lambda x: x["next"],
    {
        "Schema_Query_Agent": "Schema_Query_Agent",
        "EXECUTE_QUERY": "EXECUTE_QUERY",
        "Supervisor": "Supervisor",
        "FINISH": END
    }
)

# Set conditional edges from Supervisor
workflow.add_conditional_edges(
    "Schema_Query_Agent",
    lambda x: x["next"],
    {
        "Schema_Query_Agent": "Schema_Query_Agent",
        "EXECUTE_QUERY": "EXECUTE_QUERY",
        "Supervisor": "Supervisor"
    }
)

# Compile the graph
graph = workflow.compile(checkpointer=memory)
# print(graph.get_graph().draw_ascii())

# Example usage
def main():
    user_query = "What is the ratio of male population between sustainability survey and christmas survey?"
    state = {"next": None, "messages": [HumanMessage(content=user_query)], "sub_queries": [], "constructed_queries": [], "current_index": 0, "results": []}

    thread_id = str(uuid.uuid4())

    # Create a config dictionary with the thread_id
    config = {"configurable": {"thread_id": thread_id}}
    answer = graph.invoke(state, config=config)
    print(answer)

    return answer["messages"][-1].content

if __name__ == "__main__":
    main()