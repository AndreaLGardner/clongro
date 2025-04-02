# src/growclonego/core.py

import polars as pl

def load_data(file_path: str):
    """
    Loads barcode percent data from the given file path.

    Data must have named columns for
    'barcode', 'sample', and 'percent' (0-100%).

    Results of pycashier 'receipt' can be directly used here.

    Args:
        file_path (str): Path to the csv or tsv to load.
    
    Returns:
        pl.DataFrame: Loaded data as a polars DataFrame.
    """
    try:
        sep = '\t' if file_path.endswith('.tsv') else ','
        df = pl.read_csv(file_path, separator=sep)

        # Check if the required columns are present
        required_columns = {'barcode', 'sample', 'percent'}
        missing_columns = required_columns - set(df.columns)

        # if columns are missing, raise an error
        if missing_columns:
                raise ValueError(f"Missing required column(s): {', '.join(missing_columns)}")
        return df
    # if file path is bad, raise an error
    except Exception as e:
        raise ValueError(f"Error file not found at {file_path}: {e}")


def load_metadata(file_path: str):
    """
    Loads sample metadata from the given file path.

    Data must have named columns for
    'sample', 'time' in hours, and 'sample_group'.


    Args:
        file_path (str): Path to the csv or tsv to load.
    
    Returns:
        pl.DataFrame: Loaded metadata as a polars DataFrame.
    """
    try:
        sep = '\t' if file_path.endswith('.tsv') else ','
        df = pl.read_csv(file_path, separator=sep)

        # Check if the required columns are present
        required_columns = {'sample', 'time', 'sample_group'}
        missing_columns = required_columns - set(df.columns)

        # if columns are missing, raise an error
        if missing_columns:
                raise ValueError(f"Missing required column(s): {', '.join(missing_columns)}")
        return df
    # if file path is bad, raise an error
    except Exception as e:
        raise ValueError(f"Error file not found at {file_path}: {e}")
    

def load_bulk_growth_rates(file_path: str):
    """
    Loads bulk popultion growth rates from the given file path.

    Data must have named columns for
    'sample_group' and 'bulk_growth_rate_R' in inverse hours [1/h].

    Groups in 'sample_group' must match those in the sample metadata.

    The mean population growth rate (`bulk_growth_rate_R`) [1/h] can be estimated from
    cell counting, live-cell imaging, or other methods. 

    Providing this file is optional, but it will allow for true estimates of 
    clonal growth rates within each sample group population.


    Args:
        file_path (str): Path to the csv or tsv to load.
    
    Returns:
        pl.DataFrame: Loaded growth rate data as a polars DataFrame.
    """
    try:
        sep = '\t' if file_path.endswith('.tsv') else ','
        df = pl.read_csv(file_path, separator=sep)

        # Check if the required columns are present
        required_columns = {'sample_group', 'bulk_growth_rate_R'}
        missing_columns = required_columns - set(df.columns)

        # if columns are missing, raise an error
        if missing_columns:
                raise ValueError(f"Missing required column(s): {', '.join(missing_columns)}")
        return df
    # if file path is bad, raise an error
    except Exception as e:
        raise ValueError(f"Error file not found at {file_path}: {e}")


def est_growth(df, time_meta, pop_growths):
    """
    Estimates exponential growth rate for each barcoded clone in each sample group.

    Args:
        df (pl.DataFrame): DataFrame containing barcode percent data. Data must have named columns for 'barcode', 'sample', and 'percent' (0-100%).

        time_meta (pl.DataFrame): DataFrame containing sample metadata. Data must have named columns for 'sample', 'time' in hours, and 'sample_group'.
        Sample names in 'sample' must match those in `df['sample']`.

        pop_growths (pl.DataFrame): DataFrame containing bulk population growth rates [1/hr] for each sample_group. 
        Data must have named columns for 'sample_group' and 'bulk_growth_rate_R' [1/hr].
        Group names in 'sample_group' must match those in `time_meta`.

    Groups in 'sample_group' must match those in the sample metadata.
    
    Returns:
        pl.DataFrame: Loaded growth rate data as a polars DataFrame.
    """
    # if one sample is part of multiple groups, add a new row in the time meta data that sample
    # for each sample_group it is part of
    time_meta = time_meta.with_columns(pl.col("sample_group").str.split(",")).explode("sample_group")
    

    # using polars, select columns for barcode, sample, and percent, then join to time_meta
    df = df.select(["barcode","sample","percent"]).join(time_meta, on="sample", how="left")

    # rename percent to percent_i to indicate initial percent for each clone
    df = df.rename({"percent": "percent_i"})

    # sort data based on time, and then barcode
    df = df.sort(["time"])
    df = df.sort(["barcode"])
    df = df.sort(["sample_group"])

    # # create new column of final percent by shifting percent column up by one for each barcode in each group
    df = df.with_columns(
        pl.col("percent_i").shift(-1).over(["barcode","sample_group"]).alias("percentf_i"),
        pl.col("time").shift(-1).over(["barcode","sample_group"]).alias("timef")
    )

    # create a new column mapping the time interval
    df = df.with_columns(
        interval = df['time'] + '_' + df['timef'],
        duration_h = (df['timef']-df['time'])
        )

    # cannot estimate growth from final timepoint, remove these rows
    df = df.filter(pl.col("time") != pl.col("time").max())

    # compute unscaled growth rate using equations for exponential growth
    df = df.with_columns(
        (
            (1/pl.col("duration_h")) # 1/t
            *((pl.col("percentf_i")/pl.col("percent_i")).log()) # log(final_i/initial_i)
        ).alias("est_r_i"), 
    )

    # join bulk growth rates to the data by sample_group
    df = df.join(pop_growths, on="sample_group", how="left")

    # # scale estimated growth rate based on bulk population growth rate
    df = df.with_columns(
        est_r_i_scaled = df['bulk_growth_rate_R'] + df['est_r_i']
    )

    return df   