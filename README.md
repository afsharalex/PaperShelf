# PaperShelf

PaperShelf is a Retrieval-Augmented Generation (RAG) application that stores embeddings of academic papers (PDFs) in a vector database and allows querying about the papers using LangGraph.

## Features

- **PDF Processing**: Extract text and metadata from academic papers
- **Embedding Generation**: Generate embeddings for paper content using sentence transformers
- **Vector Database**: Store and retrieve embeddings efficiently using ChromaDB
- **RAG Querying**: Query papers using natural language and get AI-generated responses
- **API Interface**: Interact with the system through a RESTful API

## Architecture

PaperShelf is built with a modular architecture:

```
papershelf/
├── ingest/            # PDF processing and embedding generation
│   ├── pdf_processor.py
│   └── embedding_generator.py
├── db/                # Vector database operations
│   └── vector_store.py
├── query/             # RAG querying using LangGraph
│   └── rag_engine.py
├── api/               # FastAPI endpoints
│   └── app.py
├── utils/             # Utility functions and configuration
│   └── config.py
└── main.py            # Application entry point
```

## Installation

### Prerequisites

- Option 1: Docker and Docker Compose (recommended)
- Option 2: Python 3.12 or higher and Poetry

### Setup with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/papershelf.git
   cd papershelf
   ```

2. Create a `.env` file in the project root with your configuration (or use the provided `.env.example`):
   ```
   # API settings
   API_HOST=0.0.0.0
   API_PORT=8000

   # Database settings
   DB_PERSIST_DIRECTORY=./chroma_db

   # Embedding settings
   EMBEDDING_MODEL=all-MiniLM-L6-v2

   # LLM settings
   LLM_MODEL=gpt-3.5-turbo
   LLM_TEMPERATURE=0.0
   LLM_MAX_TOKENS=500

   # PDF processing settings
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=200

   # OpenAI API settings (required for RAG)
   OPENAI_API_KEY=your_openai_api_key
   ```

3. Start the application using Docker Compose:
   ```bash
   # For development (with hot reloading)
   docker-compose up

   # For production
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Setup with Python and Poetry

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/papershelf.git
   cd papershelf
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Create a `.env` file in the project root with your configuration (same as above).

## Usage

### Web Interface

PaperShelf provides a simple web interface for uploading PDF files. Once the server is running, you can access the web interface by navigating to http://localhost:8000 in your web browser. The interface allows you to:

1. Select a PDF file from your computer
2. Upload the file to the PaperShelf system
3. View the processing results, including the document ID, title, author, and page count

### Running the API Server

#### Using Poetry

Start the API server:

```bash
poetry run papershelf
```

The server will be available at http://localhost:8000 (or the host/port specified in your .env file).

#### Using the Development Script

For convenience, a development script is provided that simplifies running the server with various options:

```bash
# Run with default settings (host: 0.0.0.0, port: 8000)
./scripts/run_dev.sh

# Run on a specific host and port
./scripts/run_dev.sh --host 127.0.0.1 --port 9000

# Run with auto-reload for development
./scripts/run_dev.sh --reload

# Combine options
./scripts/run_dev.sh --host 127.0.0.1 --port 9000 --reload
```

The script will automatically check for a `.env` file and create one from `.env.example` if it doesn't exist.

### API Endpoints

> **Note:** A web interface for uploading papers is available at http://localhost:8000

#### Upload a Paper

```bash
curl -X POST -F "file=@path/to/your/paper.pdf" http://localhost:8000/upload
```

#### Query Papers

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "What are the main findings of the paper?", "top_k": 5}' \
  http://localhost:8000/query
```

#### Get Database Statistics

```bash
curl http://localhost:8000/stats
```

### Python Client Example

```python
import requests
import json

# Upload a paper
with open('path/to/paper.pdf', 'rb') as f:
    response = requests.post('http://localhost:8000/upload', files={'file': f})
    print(json.dumps(response.json(), indent=2))

# Query the paper
query = {
    "query": "What methodology was used in this paper?",
    "top_k": 3
}
response = requests.post('http://localhost:8000/query', json=query)
print(json.dumps(response.json(), indent=2))
```

## Docker Usage

PaperShelf provides Docker configurations for both development and production environments.

### Development Environment

The development environment is configured with hot reloading, which means changes to the code will be automatically reflected without restarting the container.

```bash
# Start the development environment
docker-compose up

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the containers
docker-compose down
```

### Production Environment

The production environment is optimized for performance and security:

```bash
# Start the production environment
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop the containers
docker-compose -f docker-compose.prod.yml down
```

### Environment Variables

You can configure the application by setting environment variables in the `.env.docker` file. The Docker Compose files are configured to use this file for environment variables.

```bash
# Copy the example file
cp .env.docker .env.docker.local

# Edit the file with your settings
nano .env.docker.local

# Use the local file for Docker Compose
docker-compose --env-file .env.docker.local up
```

The following variables are available:

| Variable | Description | Default |
|----------|-------------|---------|
| API_HOST | Host to bind the API server | 0.0.0.0 |
| API_PORT | Port for the API server | 8000 |
| DB_PERSIST_DIRECTORY | Directory for the vector database | /app/data/chroma_db |
| EMBEDDING_MODEL | Model for generating embeddings | all-MiniLM-L6-v2 |
| LLM_MODEL | LLM model for RAG | gpt-3.5-turbo |
| LLM_TEMPERATURE | Temperature for the LLM | 0.0 |
| LLM_MAX_TOKENS | Maximum tokens for LLM responses | 500 |
| CHUNK_SIZE | Size of text chunks for processing | 1000 |
| CHUNK_OVERLAP | Overlap between consecutive chunks | 200 |
| OPENAI_API_KEY | OpenAI API key for RAG functionality | - |

### Data Persistence

- **Development**: Data is stored in the `./data/chroma_db` directory on your host machine.
- **Production**: Data is stored in a Docker volume named `papershelf_data`.

### Docker Helper Script

A helper script is provided to simplify Docker operations:

```bash
# Start the development environment
./scripts/docker.sh dev

# Build and start the development environment
./scripts/docker.sh dev-build

# Start the production environment
./scripts/docker.sh prod

# Build and start the production environment
./scripts/docker.sh prod-build

# Stop the running containers
./scripts/docker.sh stop

# View logs
./scripts/docker.sh logs

# Show help message
./scripts/docker.sh help
```

### Building Custom Images

If you need to build custom Docker images:

```bash
# Build development image
docker build -t papershelf:dev -f Dockerfile.dev .

# Build production image
docker build -t papershelf:latest .
```

## Development

### Testing

PaperShelf uses pytest for testing. The test suite includes unit tests for all major components and integration tests for the API endpoints.

#### Running Tests

Run the entire test suite:

```bash
poetry run pytest
```

Run tests for a specific module:

```bash
poetry run pytest tests/ingest/
```

Run tests with verbose output:

```bash
poetry run pytest -v
```

Run tests with coverage reporting:

```bash
poetry run pytest --cov=papershelf
```

Generate an HTML coverage report:

```bash
poetry run pytest --cov=papershelf --cov-report=html
```
This will create a `htmlcov` directory with an HTML report that you can open in your browser.

#### Using the Test Script

For convenience, a test script is provided that simplifies running tests with various options:

```bash
# Run all tests
./scripts/run_tests.sh

# Run tests with verbose output
./scripts/run_tests.sh --verbose

# Run tests with coverage reporting
./scripts/run_tests.sh --coverage

# Generate HTML coverage report
./scripts/run_tests.sh --html

# Run a specific test or test directory
./scripts/run_tests.sh --test tests/ingest/

# Combine options
./scripts/run_tests.sh --verbose --html --test tests/api/test_api.py
```

#### Test Coverage

The tests cover the following components:

- **PDF Processing**: Tests for extracting text and metadata from PDFs
- **Embedding Generation**: Tests for generating embeddings from text
- **Vector Database**: Tests for storing and retrieving embeddings
- **RAG Engine**: Tests for querying and generating responses
- **API Endpoints**: Tests for the FastAPI application

#### Adding New Tests

To add new tests:

1. Create a test file in the appropriate directory under `tests/`
2. Use the existing fixtures in `tests/conftest.py` or create new ones
3. Follow the pytest naming conventions (test files should start with `test_` and test functions should start with `test_`)
4. Use mocks for external dependencies to ensure tests are fast and reliable

### Code Formatting

```bash
poetry run black .
poetry run isort .
```

### Type Checking

```bash
poetry run mypy .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [LangChain](https://github.com/langchain-ai/langchain) - Framework for building LLM applications
- [LangGraph](https://github.com/langchain-ai/langgraph) - Framework for building stateful, multi-actor applications with LLMs
- [ChromaDB](https://github.com/chroma-core/chroma) - Open-source embedding database
- [Sentence Transformers](https://github.com/UKPLab/sentence-transformers) - Sentence embedding models
- [FastAPI](https://github.com/tiangolo/fastapi) - Modern, fast web framework for building APIs
