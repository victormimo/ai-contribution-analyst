from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.tools.retriever import create_retriever_tool
from app.agent.loader import load_commits

embeddings = OpenAIEmbeddings()

# tap_docs = load_tap_files()
docs = load_commits()

print("docs ", docs)

text_splitter = RecursiveCharacterTextSplitter()

documents = text_splitter.split_documents(docs)

vector = FAISS.from_documents(documents, embeddings)

retriever = vector.as_retriever()

github_retriver = create_retriever_tool(
    retriever,
    "commits_and_files_retriver",
    "Contains all repo files for the tap-cap-table repo and commit history from feb 2024 - Now.. Always use this tool for that type of question!",
)
