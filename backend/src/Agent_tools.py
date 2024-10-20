import pandas as pd
from io import StringIO, BytesIO
from langchain.agents import tool
import boto3
import os

s3 = boto3.client('s3')
bucket_name = 'ai-powered-dataset-analyzer'

def load_dataset_from_s3(file_key):
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    data=obj['Body'].read()
    df = pd.read_excel(BytesIO(data), header=[0,1], index_col=[0,1,2]).fillna(0)
    df.index.names = ['Row Main-Category', 'Row Sub-Category', 'Value Type']
    df.columns.names = ['Column Main-Category', 'Column Sub-Category']
    return df

# Load datasets
df1 = load_dataset_from_s3('data/Dataset1.xlsx')
df2 = load_dataset_from_s3('data/Dataset2.xlsx')

@tool
def get_dataset_indexing_structure(data: str) -> str:
    """
    Provides a structured representation of the dataset's indexing structure in JSON format.

    Parameters:
    data (str): The name of the dataset to analyze ('df1' or 'df2').

    Returns:
    str: A JSON string containing:
        - 'row_index_levels': List of row index level names.
        - 'row_index_values': Dictionary mapping each row index level to its unique values.
        - 'column_index_levels': List of column index level names.
        - 'column_index_values': Dictionary mapping each column index level to its unique values.
    """
    import json
    df = df1 if data == 'df1' else df2

    row_index_levels = df.index.names
    row_index_values = {
        name: df.index.get_level_values(i).unique().tolist()
        for i, name in enumerate(df.index.names)
    }

    column_index_levels = df.columns.names
    column_index_values = {
        name: df.columns.get_level_values(i).unique().tolist()
        for i, name in enumerate(df.columns.names)
    }

    index_info = {
        'dataset': data,
        'row_index_levels': row_index_levels,
        'row_index_values': row_index_values,
        'column_index_levels': column_index_levels,
        'column_index_values': column_index_values,
    }
    return json.dumps(index_info, indent=2)

@tool
def get_dataset_info_tool(data: str) -> str:
    """
    Provides basic information about the dataset.

    This function uses pandas' info() method to gather and return details about
    the DataFrame's structure, including data types and non-null counts.

    Parameters:
    data (str): The name of the dataset to analyze ('df1' or 'df2').

    Returns:
    str: A string containing the DataFrame's info, including:
        - Number of rows and columns
        - Column names
        - Non-null counts for each column
        - Data types of each column
        - Memory usage
    """
    df = df1 if data == 'df1' else df2
    buffer = StringIO()
    df.info(buf=buffer)
    df_info = buffer.getvalue()
    return f"Dataset {data} Information:\n{df_info}"

@tool
def get_value_from_df(data: str, row_index: tuple, column_index: tuple) -> str:
    """
    Retrieves a specific value from the DataFrame based on provided row and column indices.

    This function safely accesses a value in a multi-index DataFrame using the given
    row and column indices. It handles potential errors and returns informative messages.

    Parameters:
    data (str): The name of the dataset to query ('df1' or 'df2').
    row_index (tuple): A 3-element tuple representing (Row Main Category, Row Sub-Category, Value Type).
    column_index (tuple): A 2-element tuple representing (Column Main Category, Column Sub-Category).

    Returns:
    str: A string containing either:
        - The value at the specified indices
        - An error message if the indices are invalid or another exception occurs
    """
    df = df1 if data == 'df1' else df2
    try:
        value = df.loc[row_index, column_index]
        return f"Value in {data} at {row_index}, {column_index}: {value}"
    except KeyError as e:
        return f"Error: Invalid index in {data}. {e}"
    except Exception as e:
        return f"Error in {data}: {e}"