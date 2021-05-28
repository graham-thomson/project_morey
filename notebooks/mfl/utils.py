import re
import pandas as pd
import numpy as np


def clean_column_name(col_name):
    return "".join(re.findall(r"\w+", col_name.replace(" ", "_"))).lower()


def convert_height_to_inches(height):
    if pd.isna(height):
        return height
    return (np.array(re.findall(r"\d+", height), dtype=int) * np.array([12, 1])).sum()


def convert_weight_to_lbs(weight):
    if pd.isna(weight):
        return weight
    return np.array(re.findall(r"\d+", weight), dtype=int).sum()


def parse_digits_to_num(col_name: str, num_type: str = "float"):
    if pd.isna(col_name):
        return col_name
    nums = "".join(re.findall(r"\d+", col_name))
    return float(nums) if num_type == "float" else int(nums)
