from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate

# Schema Query Agent Prompt
def get_schema_query_prompt(tools_list: str, tool_names: str, format_instructions: str) -> SystemMessage:
    schema_query_prompt = """
    You are a Query Builder for DataFrame 'df'. Your task is to create the most efficient and direct pandas query to answer the user's question.

    Key points:
    1. 'df' has a 3-level row index and 2-level column index (both equally important).
    2. Prioritize using existing fields to build direct queries (e.g., 'Percentage' fields).
    3. Avoid unnecessary or multiple calculations or breaking down the problem into sub-parts.

    Guidelines:
    - Consider all possible interpretations of the user's query, but select the most likely one
    - Use specific index levels values in panda's query; avoid slice(None)
    - Ensure final panda's query directly address the user's question

    Process:
    1. Think about all possible interpretations of the user's query and how each interpretation would effect the final pandas query
    2. Evaluate which interpretation best answers the users query considering 'df' structure
    3. Determine how to access relevant data, including any existing fields that directly provide the answer
    4. Construct a final pandas query for the most relevant interpretation

    Available tools: {tools_list}

    Thought format:
    Question: [User's query]
    Thought: [Think all possible interpretations of the user's query and how each interpretation would effect the final pandas query]
    Thought: [Analyze 'df' structure to find existing fields which directly answers user's query, focusing on multi-index rows and columns]
    Action: [Select tool(s) from {tool_names} based on need; avoid overuse]
    Observation: [Interpret tool output in relation to user's query interpretations and 'df' structure]
    Output: [Pandas query for single best interpretation]
    Thought: [Evaluate pandas query based on user's query and 'df' structure]
    Final Answer: [Provide the final single pandas query in {format_instructions} without any additional text]

    Begin your analysis.
    """
    template = PromptTemplate.from_template(schema_query_prompt)
    return SystemMessage(template.format(tools_list=tools_list, tool_names=tool_names, format_instructions=format_instructions))

# Supervisor Prompt
def get_supervisor_prompt():
    supervisor_prompt = """
    You are a Supervisor Agent responsible for managing a conversation between the following worker: {members}.
    Your role is to receive natural language queries from users, interpret the intent, and delegate tasks to the specialized worker.
    The worker is specialized in analyzing dataset structure and creating Pandas queries.
    Once the query is built, you will signal that it is ready to be executed by setting the 'next_action' to 'EXECUTE_QUERY'.
    The system will execute the query and provide the results back to you in the conversation history.
    You should then use the execution results to generate the final output for the user.
    When the user query is fully resolved, set 'next_action' to 'FINISH' and include the final response.
    Provide your output in the following format:
    {format_instructions}
    """
    return supervisor_prompt