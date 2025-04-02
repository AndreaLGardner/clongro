# src/growclonego/main.py

import typer
import polars as pl
from .core import load_data, load_metadata, load_bulk_growth_rates, est_growth

def main(
    data: str = typer.Option(..., help="Path to pycashier receipt outputs/barcode percent data file. Required columns: 'barcode', 'sample', 'percent."),
    meta: str = typer.Option(..., help="Path to sample meta data file. Required columns: 'sample', 'time', 'sample_group'."),
    growths: str = typer.Option(None, help="(optional) Path to file with bulk growth rates for each sample group. Required columns: 'sample_group', 'bulk_growth_rate'."),
    pop_growth_rate: float = typer.Option(None, help="(optional, numeric) Average growth rate of population [1/hr]. Only use for single sample studies or when population growth rate should be the same for all sample groups."),
    outs: str = typer.Option(None, help="(optional) Name of output file")
):
    try:
        df = load_data(data)
        time_meta = load_metadata(meta)

        if growths is None:
            typer.echo("\n")
            typer.echo("csv not provided for sample group growth rates...")
            typer.echo("\n")
            if pop_growth_rate is None:
                typer.echo("... Using *** R = 0 [1/hr] *** as bulk population growth rate for all sample groups. Resulting clonal growth rate estimates (`est_r_i_scaled`) will be unscaled.")
                typer.echo("... Assign '--pop-growth-rate' or provide a csv of sample_group growth rates using '--growths' for scaled estimates.")
                typer.echo("\n")
                pop_growths = pl.DataFrame({"sample_group": time_meta["sample_group"].unique()}).with_columns(
                    pl.lit(0).cast(pl.Float64).alias("bulk_growth_rate_R")
                )
            else:
                typer.echo(f"... Using input of *** R = {pop_growth_rate} [1/hr] *** as bulk population growth rate for all sample groups.")
                typer.echo("\n")
                pop_growths = pl.DataFrame({"sample_group": time_meta["sample_group"].unique()}).with_columns(
                    pl.lit(pop_growth_rate).cast(pl.Float64).alias("bulk_growth_rate_R")
                )
        else:
            typer.echo("Returning scaled growth rates for each sample group.")
            typer.echo("\n")
            pop_growths = load_bulk_growth_rates(growths)

        outs_df = est_growth(df, time_meta, pop_growths)

        output_path = f"outs/{outs if outs else 'clongro_outs'}.csv"
        outs_df.write_csv(output_path)
        typer.echo(f"Outputs saved to '{output_path}'")
        typer.echo("\n")

    except Exception as e:
        typer.echo(f"An error occurred: {e}", err=True)

if __name__ == "__main__":
    typer.run(main)
