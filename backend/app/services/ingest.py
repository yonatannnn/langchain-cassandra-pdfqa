import os
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from .vectorstore import get_vector_store


def ingest_pdf_to_vectorstore(file_path: str, device_id: str, document_id: str) -> int:
    loader = PyPDFLoader(file_path)
    pages = loader.load()

    for doc in pages:
        if not doc.metadata:
            doc.metadata = {}
        doc.metadata.update({
            "device_id": device_id,
            "document_id": document_id,
            "source": os.path.basename(file_path),
            "deleted": False,
        })

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(pages)

    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    return len(chunks)
