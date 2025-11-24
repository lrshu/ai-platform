# RAG Backend

## Constitution

- Code quality first: modular components, typed interfaces, comments only when needed.
- Comprehensive testing: integration tests cover indexing, retrieval, and chat flows.
- Consistent UX: CLI commands behave predictably and validate inputs.
- Performance focus: use batching and graph/vector hybrids to keep latency manageable.

## Getting Started

```bash
uv sync
uv run python main.py --help
```

## Indexing

To index a document, use the `index` command:

```bash
uv run python main.py indexing --name codex-gpt51 --file ../documents/华为基本法.pdf
```

## Search

To search information from the indexed document, use the `search` command:

```bash
uv run python main.py search --name codex-gpt51 --question "华为基本法的主要内容" --top-k 5 --expand_query true --rerank true --use_vector true --use_graph true
```

## Chat

To start a chat session with the indexed document, use the `chat` command:

```bash
uv run python main.py chat --name codex-gpt51 --question "华为基本法的主要内容"
```
