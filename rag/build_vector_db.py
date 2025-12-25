from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


loader = CSVLoader(file_path="qna1.csv", encoding="utf-8")
docs = loader.load()

embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

persist_directory = '../database/vectordb'

vectordb = Chroma.from_documents(
    documents=docs,
    embedding=embedding_function,
    persist_directory=persist_directory
)