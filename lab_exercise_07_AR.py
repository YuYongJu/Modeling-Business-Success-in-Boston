# LAB EXERCISE 07

import pandas as pd
import math

# 1)

def compute_zscore(nums):
    """Compute z-score for a list of numbers using 
    sample standard deviation

    Parameters: nums (list): list of numbers
    Returns: zscore (lst): list of floats that are z-scores
    for each value in nums"""
    mean = sum(nums) / len(nums)
    n = len(nums)

    var = sum((x - mean)**2 for x in nums) / (n - 1)
    sd = math.sqrt(var)

    zscore = [(x - mean) / sd for x in nums]

    return zscore

# 2)
def compute_mms(nums):
    """Computes Min-Max scaling for a list of numbers
    to a range between 0 and 1
    
    Parameters: nums (list): list of numbers
    Returns: scaled (list): list of scaled min-max numbers"""
    x_min = min(nums)
    x_max = max(nums)

    scaled = [(x - x_min)/ (x_max - x_min) for x in nums]
    
    return scaled

# 3)
def remove_cols_with_missing(df):
    """Takes a pandas dataframe object and returns a new 
    dataframe after removing columns containing any missing values"""
    return df.dropna(axis=1)

def remove_rows_with_missing(df):
    """Takes a pandas dataframe object and returns a new 
    dataframe after removing rows containing any missing values"""
    return df.dropna(axis=0)

def main():
    nums = [1, 2, 3, 4, 5]

    # 1)
    print("z-score: ", compute_zscore(nums))

    # 2)
    print("min-max: ", compute_mms(nums))

if __name__ == '__main__':
    main()
