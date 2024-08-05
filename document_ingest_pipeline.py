from haystack.components.writers import DocumentWriter
from haystack.components.converters import MarkdownToDocument, PyPDFToDocument, TextFileToDocument
from haystack.components.preprocessors import DocumentSplitter, DocumentCleaner
from haystack.components.routers import FileTypeRouter
from haystack.components.joiners import DocumentJoiner
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.embedders.ollama import OllamaDocumentEmbedder
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
import os

'''Updating Environment variable to access the docker postgreSQL using this connection string env variable'''
os.environ['PG_CONN_STR']="postgresql://postgres:postgres@localhost:5432/postgres"


'''Database to store Document and embeddings'''
document_store =PgvectorDocumentStore(
    embedding_dimension=768,
    vector_function="cosine_similarity",
    recreate_table=True,
    search_strategy="hnsw",
)

'''File Router component to route different file to different components in pipeline'''
file_type_router = FileTypeRouter(mime_types=["text/plain", "application/pdf", "text/markdown"])

'''Txt file converter'''
text_file_converter = TextFileToDocument()

'''markdown file converter'''
markdown_converter = MarkdownToDocument()

'''#pdf file converter'''
pdf_converter = PyPDFToDocument()

'''component used to join document coming from different branches of pipeline'''
document_joiner = DocumentJoiner()

'''cleaner component is used to remove white spaces and make document readable'''
document_cleaner = DocumentCleaner()

'''splitter component is used to split large document into chunks''' 
document_splitter = DocumentSplitter(split_by="word", split_length=150, split_overlap=50)

'''OllamaDocumentEmbedder is used to create embedding for documents'''
document_embedder = OllamaDocumentEmbedder()

'''document_write is used to write the Document object into the DocumentStore'''
document_writer = DocumentWriter(document_store)

'''Initializing Indexing Pipeline'''
preprocessing_pipeline = Pipeline()

'''Adding components to the pipeline'''
preprocessing_pipeline.add_component(instance=file_type_router, name="file_type_router")
preprocessing_pipeline.add_component(instance=text_file_converter, name="text_file_converter")
preprocessing_pipeline.add_component(instance=markdown_converter, name="markdown_converter")
preprocessing_pipeline.add_component(instance=pdf_converter, name="pypdf_converter")
preprocessing_pipeline.add_component(instance=document_joiner, name="document_joiner")
preprocessing_pipeline.add_component(instance=document_cleaner, name="document_cleaner")
preprocessing_pipeline.add_component(instance=document_splitter, name="document_splitter")
preprocessing_pipeline.add_component(instance=document_embedder, name="document_embedder")
preprocessing_pipeline.add_component(instance=document_writer, name="document_writer")


'''Connecting FileRouter component to different Document Converters'''
preprocessing_pipeline.connect("file_type_router.text/plain", "text_file_converter.sources")
preprocessing_pipeline.connect("file_type_router.application/pdf", "pypdf_converter.sources")
preprocessing_pipeline.connect("file_type_router.text/markdown", "markdown_converter.sources")

'''Connecting different Document Converters Output to Document Joiner'''
preprocessing_pipeline.connect("text_file_converter", "document_joiner")
preprocessing_pipeline.connect("pypdf_converter", "document_joiner")
preprocessing_pipeline.connect("markdown_converter", "document_joiner")

'''Preproceesing all the document usign Cleaner,Splitter'''
preprocessing_pipeline.connect("document_joiner", "document_cleaner")
preprocessing_pipeline.connect("document_cleaner", "document_splitter")

'''Creating Embeddings for the chunks using DocumentEmbedder and finally writing document with embedding into Document Store'''
preprocessing_pipeline.connect("document_splitter", "document_embedder")
preprocessing_pipeline.connect("document_embedder", "document_writer")