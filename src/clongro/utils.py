# src/growclonego/utils.py
import polars as pl

def check_columns(df, req_cols = {}):
    # Check if the required columns are present
    missing_columns = req_cols - set(df.columns)

    # if columns are missing, raise an error
    if missing_columns:
            raise ValueError(f"Missing required column(s): {', '.join(missing_columns)}")
    return df


def check_sample_group(df):
        invalid_groups = (
                df.with_columns(
                        pl.col("sample_group").str.split(";"))
                        .explode("sample_group")
                        .group_by("sample_group")
                        .agg(pl.col("sample").n_unique().alias("n_samples"))
                        .filter(pl.col("n_samples") != 2)
                        )

        if invalid_groups.height > 0:
                raise ValueError(f"Invalid sample groups found:\n{invalid_groups} \nEnsure each sample_group maps to exactly 2 samples representing inital and final timepoints")