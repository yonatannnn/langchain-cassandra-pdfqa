# Document Loader Backend (Flask + LangChain + Cassandra + MongoDB)

Backend API to upload PDFs, index them into a Cassandra vector store (via CassIO + LangChain), and answer questions over the uploaded documents. Users are identified by `device_id` until full auth is added.

## Quickstart

1. Create and populate a `.env` file (see Environment Variables below).
2. Create a Python virtual environment and install dependencies:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the server:

```bash
python main.py
```

Server runs on `http://0.0.0.0:${PORT:-8000}`.

## Environment Variables

- `FLASK_ENV` (default `development`)
- `FLASK_DEBUG` (default `1`)
- `PORT` (default `8000`)
- `CORS_ORIGINS` (default `*`)
- `OPENAI_API_KEY` (required)
- `OPENAI_MODEL` (default `gpt-4o-mini`)
- `EMBEDDING_MODEL` (default `text-embedding-3-small`)
- `TEMPERATURE` (default `0.2`)
- `ASTRA_DB_APP_TOKEN` (required)
- `ASTRA_DB_ID` (required)
- `ASTRA_DB_KEYSPACE` (required if using a specific keyspace)
- `MONGODB_URI` (default `mongodb://localhost:27017`)
- `MONGODB_DB` (default `document_loader`)
- `UPLOAD_DIR` (default `./uploads`)
- `CHUNK_SIZE` (default `1000`)
- `CHUNK_OVERLAP` (default `200`)

## Endpoints

- `GET /` Health

- `POST /documents/upload`
  - form-data: `device_id` (string), `file` (pdf)
  - response: `{ doc_id, chunks_indexed }`

- `GET /documents?device_id=...`
  - list documents for device

- `DELETE /documents/{doc_id}?device_id=...`
  - soft-delete document metadata (indexed vectors remain but are filtered by `deleted=false`)

- `POST /qa/ask`
  - json: `{ device_id: string, question: string, doc_id?: string }`
  - response: `{ answer, sources: [{document_id, source, page}] }`

## Notes

- Vector store: DataStax Astra via CassIO `Cassandra` vector store, table `document_qa`.
- Filtering: retrieval is constrained by `device_id` and optional `doc_id`. Deleted documents are excluded.
- PDF parsing: `PyPDFLoader` + `RecursiveCharacterTextSplitter`.

## cURL Examples

```bash
# Upload a PDF
curl -X POST http://localhost:8000/documents/upload \
  -F device_id=example-device-1 \
  -F file=@/path/to/document.pdf

# List documents
curl "http://localhost:8000/documents?device_id=example-device-1"

# Ask a question (across all docs)
curl -X POST http://localhost:8000/qa/ask \
  -H 'Content-Type: application/json' \
  -d '{"device_id":"example-device-1","question":"What is the main topic?"}'

# Ask a question for a specific doc
curl -X POST http://localhost:8000/qa/ask \
  -H 'Content-Type: application/json' \
  -d '{"device_id":"example-device-1","doc_id":"<DOC_ID>","question":"Summarize section 2"}'
```
