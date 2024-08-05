from haystack_integrations.components.embedders.ollama import OllamaTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.generators.ollama import OllamaGenerator
from haystack import Pipeline
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever
import os

os.environ['PG_CONN_STR']="postgresql://postgres:postgres@localhost:5432/postgres"


'''Initializing the Document Store for the RAG pipeline'''
document_store= PgvectorDocumentStore(
    embedding_dimension=768,
    vector_function="cosine_similarity",
    recreate_table=True,
    search_strategy="hnsw",
)



'''Prompt Template for the LLM'''

template = """
Answer the questions based on the given context.

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{ question }}
Answer:
"""

'''initializing Rag Pipeline'''
rag_pipeline = Pipeline()
rag_pipeline.add_component("embedder", OllamaTextEmbedder(url="http://localhost:11434/api/embeddings",timeout=200))
rag_pipeline.add_component("retriever", PgvectorEmbeddingRetriever(document_store=document_store))
rag_pipeline.add_component("prompt_builder", PromptBuilder(template=template))
rag_pipeline.add_component(
    "llm",
    OllamaGenerator(model="phi3",url="http://localhost:11434/api/generate",timeout=300),
)

'''Connecting the pipeline components'''
rag_pipeline.connect("embedder.embedding", "retriever.query_embedding")
rag_pipeline.connect("retriever", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "llm")