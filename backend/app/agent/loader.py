
# strategies to test
# 1. One Retriver
# 2. One Retriver for each

import os
from typing import List
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders import DirectoryLoader, WebBaseLoader


def load_commits():
    try:
        loader = DirectoryLoader(
            "./",
            glob="**/*.txt",
            # use_multithreading=True,
            show_progress=True,
            loader_cls=TextLoader,
        )

        docs = loader.load()

        print(f"{len(docs)} documents were loaded")
        return docs
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

docs = load_commits()

