import pandas as pd
import dask.dataframe as dd
import streamlit as st
import re

df: dd.DataFrame = dd.read_parquet("jobinfo.parquet")
df = df.compute()


