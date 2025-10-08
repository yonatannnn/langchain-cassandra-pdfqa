import os
from flask import Blueprint, request, jsonify
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from ..services.vectorstore import get_vector_store

qa_bp = Blueprint("qa", __name__)


def build_retriever(device_id: str, document_id: str | None):
    vector_store = get_vector_store()
    metadata_filter = {"device_id": device_id, "deleted": False}
    if document_id:
        metadata_filter["document_id"] = document_id
    # Cassandra vector store supports metadata filtering via search_kwargs
    retriever = vector_store.as_retriever(search_kwargs={"k": 6, "filter": metadata_filter})
    return retriever


DEFAULT_PROMPT = PromptTemplate.from_template(
    """
You are a helpful assistant answering questions strictly using the provided context.
If the answer is not in the context, say you don't know.

Question: {question}

Context:
{context}

Answer concisely.
"""
)


@qa_bp.post("/ask")
def ask():
    payload = request.get_json(silent=True) or {}
    device_id = payload.get("device_id")
    question = payload.get("question")
    document_id = payload.get("doc_id")

    if not device_id:
        return jsonify({"error": "device_id is required"}), 400
    if not question:
        return jsonify({"error": "question is required"}), 400

    retriever = build_retriever(device_id, document_id)

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=float(os.getenv("TEMPERATURE", "0.2")),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={
            "prompt": DEFAULT_PROMPT,
        },
        return_source_documents=True,
    )

    result = chain.invoke({"query": question})
    answer = result.get("result", "")

    sources = []
    for doc in result.get("source_documents", [])[:3]:
        meta = doc.metadata or {}
        sources.append({
            "document_id": meta.get("document_id"),
            "source": meta.get("source"),
            "page": meta.get("page"),
        })

    return jsonify({"answer": answer, "sources": sources})
