import pandas as pd
from typing import List


def min_max_normalize_columns(df: pd.DataFrame,
                              columns_to_normalize: List[str]) -> pd.DataFrame:
    """
    Perform min-max normalization on a subset of columns in a pandas DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.
        columns_to_normalize (List[str]): A list of column names to normalize.

    Returns:
        pd.DataFrame:
                    A new DataFrame with the specified columns normalized to
                    the range [0, 1]. The original DataFrame is not modified.
                    Columns not in `columns_to_normalize` are included in the
                    returned DataFrame, unchanged.
    """
    # Create a copy to avoid modifying the original DataFrame in place.
    df_normalized = df.copy()

    for col in columns_to_normalize:
        if col not in df_normalized.columns:
            print(f"Warning: Column '{col}' not found in DataFrame. Skipping.")
            continue  # Skip to the next column in the loop

        # Calculate min and max for the current column
        col_min = df_normalized[col].min()
        col_max = df_normalized[col].max()

        # Check if the column has the same min and max value
        if col_max - col_min == 0:
            print(
                f"Warning: Column '{col}' has the same min and max value."
                "Setting all values to 0."
            )
            df_normalized[col] = 0.0  # Avoid division by zero, set all to 0.0
        else:
            # Apply min-max normalization
            df_normalized[col] = (
                (df_normalized[col] - col_min) / (col_max - col_min)
            )

    return df_normalized


if __name__ == '__main__':
    # Example usage:
    data = {'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50],
            'C': [100, 5, 100, 5, 100],
            'D': [0, 0, 0, 0, 0],  # Example with constant values
            'E': [1, 2, 3, 4, 5]}
    df = pd.DataFrame(data)

    columns_to_normalize = ['A', 'B', 'C', 'D', 'F']  # Include 'F' to test
    # error handling

    df_normalized = min_max_normalize_columns(df, columns_to_normalize)

    print("Original DataFrame:")
    print(df)
    print("\nNormalized DataFrame:")
    print(df_normalized)

    # Example 2:  Test with a DataFrame that already has some values between 0
    # and 1
    data2 = {'A': [0.1, 0.2, 0.5, 0.8, 1.0],
             'B': [10, 20, 30, 40, 50],
             'C': [0, 5, 10, 15, 20]}
    df2 = pd.DataFrame(data2)
    columns_to_normalize_2 = ['A', 'B', 'C']
    df2_normalized = min_max_normalize_columns(df2, columns_to_normalize_2)
    print("\nOriginal DataFrame 2:")
    print(df2)
    print("\nNormalized DataFrame 2:")
    print(df2_normalized)
