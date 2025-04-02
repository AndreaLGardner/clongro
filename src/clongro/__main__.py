# src/clongro/main.py

import argparse
import polars as pl
#import numpy as np
from .core import load_data, load_metadata, load_bulk_growth_rates, est_growth#* # new_function

def main():
    parser = argparse.ArgumentParser(description="Process raw data file.")
    parser.add_argument('--data', type=str, help="Path to pycashier receipt outputs/barcode percent data file. Required columns: 'barcode', 'sample', 'percent.", required=True)
    parser.add_argument('--meta', type=str, help="Path to sample meta data file. Required columns: 'sample', 'time', 'sample_group'.", required=True)
    parser.add_argument('--growths', type=str, help="(optional) Path to file with bulk growth rates for each sample group. Required columns: 'sample_group', 'bulk_growth_rate'.", required=False)
    parser.add_argument('--pop-growth-rate', type=float, help="(optional, numeric) Average growth rate of population [1/hr]. Only use for single sample studies or when population growth rate should be the same for all sample groups.", required=False)
    parser.add_argument('--outs', type=str, help="(optional) Name of output file", required=False)
    parser.add_argument('--drop-empty', type=bool, default=True, help="Drop samples without growth rate estimates from outputs", required=False)
    args = parser.parse_args()
    try:
        df = load_data(args.data)
        time_meta = load_metadata(args.meta)

        if args.growths is None:
            print("\n")
            print("csv not provided for sample group growth rates...")
            print("\n")
            if args.pop_growth_rate is None:
                print("... Using *** R = 0 [1/hr] *** as bulk population growth rate for all sample groups. Resulting clonal growth rate estimates (`est_r_i_scaled`) will be unscaled.")
                print(f"... Assign '--pop-growth-rate' or provide a csv of sample_group growth rates using '--growths' for scaled estimates.")
                print("\n")
                # make 0's growth data frame
                pop_growths = pl.DataFrame({"sample_group":time_meta["sample_group"].unique()}).with_columns(pl.lit(0).cast(pl.Float64).alias("bulk_growth_rate_R"))
            else:
                print(f"... Using input of *** R = {args.pop_growth_rate} [1/hr] *** as bulk population growth rate for all sample groups.")
                print("\n")
                # make growth data frame from mean_pop_rate
                pop_growths = pl.DataFrame({"sample_group":time_meta["sample_group"].unique()}).with_columns(pl.lit(args.pop_growth_rate).cast(pl.Float64).alias("bulk_growth_rate_R"))
        else:
            print(f"Returning scaled growth rates for each sample group.")
            print("\n")
            # load growth rate csv
            pop_growths = load_bulk_growth_rates(args.growths)

        # run growth rate estimator
        outs = est_growth(df, time_meta, pop_growths)

        if args.drop_empty is True:
            outs = outs.drop_nulls().drop(["sample","time","timef"])

        # save outputs to csv
        if args.outs is None:
            outs.write_csv("outs/clongro_outs.csv")
            print("Outputs saved to 'outs/clongro_outs.csv'")
            print("\n")
        else:
            outs.write_csv("outs/" + args.outs + ".csv")
            print(f"Outputs saved to 'outs/{args.outs}.csv'")
            print("\n")

    except Exception as e:
        print(f"An error occurred: {e}")
        

if __name__ == '__main__':
    main()