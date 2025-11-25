import typer
from .rag_backend import orchestration

app = typer.Typer()

@app.command()
def indexing(name: str = typer.Option(..., help="The name of the knowledge base."),
             file: str = typer.Option(..., help="The path to the PDF file to index.")):
    """
    Indexes a new PDF document into a specified knowledge base.
    """
    orchestration.index(name, file)

@app.command()
def search(name: str = typer.Option(..., help="The name of the knowledge base."),
           question: str = typer.Option(..., help="The question to ask."),
           expand_query: bool = typer.Option(True, help="Enable/disable query expansion."),
           rerank: bool = typer.Option(True, help="Enable/disable result re-ranking.")):
    """
    Performs a retrieval query against a knowledge base and returns the raw text chunks.
    """
    orchestration.search(name, question, {"expand_query": expand_query, "rerank": rerank})

@app.command()
def chat(name: str = typer.Option(..., help="The name of the knowledge base."),
         question: str = typer.Option(..., help="The question to ask."),
         expand_query: bool = typer.Option(True, help="Enable/disable query expansion."),
         rerank: bool = typer.Option(True, help="Enable/disable result re-ranking.")):
    """
    Performs a conversational query against a knowledge base and returns a generated answer.
    """
    orchestration.chat(name, question, {"expand_query": expand_query, "rerank": rerank})

if __name__ == "__main__":
    app()
