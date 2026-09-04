import click

from .api.client import fetch
from demo.db.pg import PgRepo


@click.command()
def main() -> None:
    click.echo(fetch() + PgRepo().get("x"))


if __name__ == "__main__":
    main()
