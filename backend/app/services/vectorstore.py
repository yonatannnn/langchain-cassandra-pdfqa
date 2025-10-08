import os
import cassio
from typing import Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.cassandra import Cassandra


_vector_store: Optional[Cassandra] = None


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_vector_store() -> Cassandra:
    global _vector_store
    if _vector_store is not None:
        return _vector_store

    # Validate required configuration up front for clearer errors
    openai_key = _require_env("OPENAI_API_KEY")
    astra_token = _require_env("ASTRA_DB_APP_TOKEN")
    astra_db_id = _require_env("ASTRA_DB_ID")
    keyspace = _require_env("ASTRA_DB_KEYSPACE")

    cassio.init(
        token=astra_token,
        database_id=astra_db_id,
        keyspace=keyspace,
    )

    embeddings = OpenAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        openai_api_key=openai_key,
    )

    table_name = os.getenv("ASTRA_TABLE_NAME", "document_qa")

    _vector_store = Cassandra(
        embedding=embeddings,
        table_name=table_name,
        session=None,
        keyspace=keyspace,
    )
    return _vector_store
