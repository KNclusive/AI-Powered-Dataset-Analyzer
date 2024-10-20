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
from src.Agent_prompts import get_schema_query_prompt, get_supervisor_prompt
from src.Agent_tools import df1, df2, get_value_from_df, get_dataset_info_tool, get_dataset_indexing_structure
from typing import Dict, TypedDict, Annotated, Sequence, List
import operator
import functools
import uuid
import json

# Import FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# Setup for response validation
import pandas as pd
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Literal

class FinalResponse(BaseModel):
    original_user_query: str = Field(description="The user's original natural language query.")
    constructed_pandas_query: str = Field(description="The single-line final panda's query constructed to answer user's query.")
    output: str = Field(description="The result of the executed single-line panda's query.")
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
    supervisor_chain = supervisor_formatted_prompt | llm.with_structured_output(SupervisorResponse)
    response = supervisor_chain.invoke(state)
    next_action = response.next_action

    if next_action == "Schema_Query_Agent":
        squeries = response.sub_queries
        state['sub_queries'] = squeries
        state['current_index'] = 0
        state['next'] = next_action
    elif next_action == "EXECUTE_QUERY":
        state['next'] = next_action
    elif next_action == "FINISH":
        final_response = validate_response(response)
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
    index = state.get('current_index', 0)
    sub_queries = state.get('sub_queries', [])
    if not sub_queries:
        # No sub-queries to process
        state['messages'].append(HumanMessage(content=f"Did not recieve any sub-queries to construct panda's query", name='Schema_Query_Agent'))
        state['next'] = 'Supervisor'
        return state

    if index >= len(sub_queries):
        state['messages'].append(HumanMessage(content=f"Current Index indicates all sub-queries have been processed.", name='Schema_Query_Agent'))
        # All sub-queries have been processed
        state['next'] = "Supervisor"
        return state

    query_in_play = sub_queries[index]

    agent_state = {'messages': [HumanMessage(content=query_in_play, name="Supervisor")]}

    result = agent.invoke(agent_state)
    agent_message = result["messages"][-1].content
    try:
        output = schema_query_parser.parse(agent_message)
    except ValidationError as e:
        print(f"Validation error {e}")
        output = {'final_query': "print('Could not Construct Pandas Query!')"}

    query_cons = output.get("final_query")
    state['constructed_queries'].append(query_cons)

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
    queries_to_execute = state['constructed_queries']

    if not queries_to_execute:
        state['messages'].append(HumanMessage(content=f'No queries to execute', name='EXECUTE_QUERY'))
        return state

    for query in queries_to_execute:
        try:
            res = python_repl_tool.run(query)
        except Exception as e:
            res = f"Error in {e} in  {query} execution"

        if isinstance(res, (pd.DataFrame, pd.Series)):
            state['results'].append(res.to_string())
        else:
            state['results'].append(str(res))

        state['messages'].append(HumanMessage(content=f'The pandas query {query} is executed; the result is {res}.', name='EXECUTE_QUERY'))
    return state

# Define a Pydantic model for the request body
class QueryRequest(BaseModel):
    query: str

app = FastAPI()

app.add_middleware(GZipMiddleware, minimum_size=1000)

import os
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/datasets/{dataset_name}")
def get_dataset(dataset_name: str):
    try:
        if dataset_name == 'df1':
            df = df1
        elif dataset_name == 'df2':
            df = df2
        else:
            raise HTTPException(status_code=404, detail="Dataset not found")

        # Reset index to convert multi-index to columns
        df_reset = df.reset_index()

        # Flatten column names if they are MultiIndex
        if isinstance(df_reset.columns, pd.MultiIndex):
            df_reset.columns = ['_'.join(col).strip().replace(' ', '_') for col in df_reset.columns.values]
        else:
            df_reset.columns = [col.strip().replace(' ', '_') for col in df_reset.columns]

        # Convert DataFrame to JSON with appropriate orientation
        data_json = df_reset.to_json(orient='records', date_format='iso', force_ascii=False)

        return {"data": json.loads(data_json)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Modify the /query endpoint to handle exceptions
from openai import RateLimitError, OpenAIError

from fastapi.responses import JSONResponse

@app.post("/query")
def handle_query(request: QueryRequest):
    user_query = request.query
    state = {
        "next": None,
        "messages": [HumanMessage(content=user_query)],
        "sub_queries": [],
        "constructed_queries": [],
        "current_index": 0,
        "results": []
    }

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    try:
        answer = graph.invoke(state, config=config)
        final_message_content = answer["messages"][-1].content

        # Try to parse the content as JSON
        try:
            final_message = json.loads(final_message_content)
        except json.JSONDecodeError:
            final_message = final_message_content
        
        return {"response": final_message}
    
    except RateLimitError as e:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."},
        )
    except OpenAIError as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"OpenAI API error: {str(e)}"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"An error occurred: {str(e)}"},
        )