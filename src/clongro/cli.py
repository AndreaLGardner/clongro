"""Console script for clongro."""
import clongro

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for clongro."""
    console.print("Replace this message by putting your code into "
               "clongro.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    


if __name__ == "__main__":
    app()
