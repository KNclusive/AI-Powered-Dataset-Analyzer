import pandas as pd
from io import StringIO
from langchain.agents import tool

# Dataset loading and definition.
data_df = pd.read_excel('Book2.xlsx', header=[0,1], index_col=[0,1, 2]).fillna(0)
data_df.index.names = ['Category', 'Subcategory', 'Measure']
data_df.columns.names = ['MainCategory', 'Subcategory']

# Define the Schema Retrieval Agent Tools
@tool
def get_dataset_indexing_structure():
    """Provides the information about the indexing structure of the datset and the values used for indexing"""
    index_info = (f"Index levels: {data_df.index.names}\n"
                  f"Index values: {[data_df.index.get_level_values(i).unique().tolist() for i in range(data_df.index.nlevels)]}\n"
                  f"Column levels: {data_df.columns.names}\n"
                  f"Column values: {[data_df.columns.get_level_values(i).unique().tolist() for i in range(data_df.columns.nlevels)]}")
    return f"Index Information as follows: {index_info}"

@tool
def get_dataset_info_tool():
    """Provides basic information about the dataset, including the structure, data types, and number of entries."""
    buffer = StringIO()
    data_df.info(buf=buffer)
    df_info = buffer.getvalue()
    return f"Dataset Information as follows: {df_info}"