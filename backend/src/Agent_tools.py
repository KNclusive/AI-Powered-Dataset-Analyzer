import pandas as pd
from io import StringIO
from pathlib import Path
from langchain.agents import tool

fpath = Path(__file__).parent.parent

# Dataset loading and definition.
data_df = pd.read_excel(fpath.joinpath('data','Book2.xlsx'), header=[0,1], index_col=[0,1, 2]).fillna(0)
data_df.index.names = ['Category', 'Subcategory', 'Measure']
data_df.columns.names = ['MainCategory', 'Subcategory']

# Define the Schema Retrieval Agent Tools
@tool
def get_dataset_indexing_structure() -> str:
    """Provides detailed information about the dataset's indexing structure, including levels, unique values, and hierarchical relationships."""
    def format_level_info(index, is_row=True):
        index_type = "Row" if is_row else "Column"
        level_info = f"{index_type} Index Levels: {index.names}\n"
        level_info += f"Unique Values at Each {index_type} Level:\n"
        for i, name in enumerate(index.names):
            values = index.get_level_values(i).unique().tolist()
            level_info += f"  - Level {i} ({name}): {values}\n"
        return level_info

    row_index_info = format_level_info(data_df.index)
    column_index_info = format_level_info(data_df.columns, is_row=False)

    index_info = f"{row_index_info}\n{column_index_info}"
    return f"Index Information:\n{index_info}"

@tool
def get_dataset_info_tool() -> str:
    """Provides basic information about the dataset, including the structure, data types, and number of entries."""
    buffer = StringIO()
    data_df.info(buf=buffer)
    df_info = buffer.getvalue()
    return f"Dataset Information as follows: {df_info}"

@tool
def get_value_from_df(row_index: tuple, column_index: tuple) -> str:
    """
    Retrieves a specific value from the DataFrame 'df' based on provided row and column indices.
    
    Parameters:
    row_index (tuple): A 3-element tuple representing (main_category, subcategory, measure)
    column_index (tuple): A 2-element tuple representing (column_main_category, column_subcategory)
    
    Returns:
    str: The value at the specified indices, or an error message if indices are invalid.
    """
    try:
        value = data_df.loc[row_index, column_index]
        return f"Value at {row_index}, {column_index}: {value}"
    except KeyError as e:
        return f"Error: Invalid index. {e}"
    except Exception as e:
        return f"Error: {e}"