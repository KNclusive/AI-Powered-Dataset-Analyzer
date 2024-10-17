import pandas as pd
from io import StringIO
from pathlib import Path
from langchain.agents import tool

fpath = Path(__file__).parent.parent.parent

# Dataset loading and definition.
df2 = pd.read_excel(fpath.joinpath('data','Dataset_1.xlsx'), header=[0,1], index_col=[0,1, 2]).fillna(0)
df1 = pd.read_excel(fpath.joinpath('data','Dataset_2.xlsx'), header=[0,1], index_col=[0,1, 2]).fillna(0)
# data_df.index.names = ['Category', 'Subcategory', 'Measure']
# data_df.columns.names = ['MainCategory', 'Subcategory']
@tool
def get_dataset_indexing_structure(data: pd.DataFrame) -> str:
    """
    Provides detailed information about the dataset's indexing structure.

    This function analyzes both row and column indices of the given DataFrame,
    including their levels, unique values, and hierarchical relationships.

    Parameters:
    data (pd.DataFrame): The input DataFrame to analyze.

    Returns:
    str: A formatted string containing:
        - Number of levels in row and column indices
        - Names of each index level
        - List of unique values for each level in both row and column indices
    """
    def format_level_info(index, is_row=True):
        index_type = "Row" if is_row else "Column"
        level_info = f"{index_type} Index Levels: {index.names}\n"
        level_info += f"Unique Values at Each {index_type} Level:\n"
        for i, name in enumerate(index.names):
            values = index.get_level_values(i).unique().tolist()
            level_info += f"  - Level {i} ({name}): {values}\n"
        return level_info

    row_index_info = format_level_info(data.index)
    column_index_info = format_level_info(data.columns, is_row=False)

    index_info = f"{row_index_info}\n{column_index_info}"
    return f"Index Information:\n{index_info}"

@tool
def get_dataset_info_tool(data: pd.DataFrame) -> str:
    """
    Provides basic information about the dataset.

    This function uses pandas' info() method to gather and return details about
    the DataFrame's structure, including data types and non-null counts.

    Parameters:
    data (pd.DataFrame): The input DataFrame to analyze.

    Returns:
    str: A string containing the DataFrame's info, including:
        - Number of rows and columns
        - Column names
        - Non-null counts for each column
        - Data types of each column
        - Memory usage
    """
    buffer = StringIO()
    data.info(buf=buffer)
    df_info = buffer.getvalue()
    return f"Dataset Information as follows: {df_info}"

@tool
def get_value_from_df(data: pd.DataFrame, row_index: tuple, column_index: tuple) -> str:
    """
    Retrieves a specific value from the DataFrame based on provided row and column indices.

    This function safely accesses a value in a multi-index DataFrame using the given
    row and column indices. It handles potential errors and returns informative messages.

    Parameters:
    data (pd.DataFrame): The input DataFrame to query.
    row_index (tuple): A 3-element tuple representing (Row Main Category, Row Sub-Category, Measure Type).
    column_index (tuple): A 2-element tuple representing (Column Main Category, Column Sub-Category).

    Returns:
    str: A string containing either:
        - The value at the specified indices
        - An error message if the indices are invalid or another exception occurs
    """
    try:
        value = data.loc[row_index, column_index]
        return f"Value at {row_index}, {column_index}: {value}"
    except KeyError as e:
        return f"Error: Invalid index. {e}"
    except Exception as e:
        return f"Error: {e}"