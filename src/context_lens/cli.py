import click
import uvicorn
from .web import app

@click.group()
def cli():
    pass

@cli.command()
@click.option('--port', default=8000)
def serve(port):
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == '__main__':
    cli()