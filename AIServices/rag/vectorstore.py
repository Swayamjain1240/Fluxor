import os
from pathlib import Path

from pypdf import PdfReader

from langchain_core.documents import Document

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_chroma import Chroma

from rag.embeddings import (
    get_embedding_model
)


BASE_DIR = Path(
    __file__
).resolve().parent


DOCUMENTS_DIR = (
    BASE_DIR / "documents"
)


CHROMA_DIR = (
    BASE_DIR / "chroma_db"
)


COLLECTION_NAME = (
    "fluxor_astronomy"
)


def load_documents():

    documents = []


    if not DOCUMENTS_DIR.exists():

        DOCUMENTS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )


    for file_path in DOCUMENTS_DIR.iterdir():

        # Ignore README
        if file_path.name.lower() == "readme.md":
            continue


        # -------------------------
        # PDF
        # -------------------------

        if file_path.suffix.lower() == ".pdf":

            reader = PdfReader(
                str(file_path)
            )


            for page_number, page in enumerate(
                reader.pages
            ):

                text = (
                    page.extract_text()
                    or ""
                )


                if not text.strip():
                    continue


                documents.append(
                    Document(

                        page_content=text,

                        metadata={
                            "source":
                                file_path.name,

                            "page":
                                page_number + 1,

                            "type":
                                "pdf"
                        }
                    )
                )


        # -------------------------
        # TXT / Markdown
        # -------------------------

        elif file_path.suffix.lower() in [
            ".txt",
            ".md"
        ]:

            text = file_path.read_text(
                encoding="utf-8",
                errors="ignore"
            )


            if text.strip():

                documents.append(
                    Document(

                        page_content=text,

                        metadata={
                            "source":
                                file_path.name,

                            "type":
                                file_path.suffix[
                                    1:
                                ]
                        }
                    )
                )


    return documents


def split_documents(documents):

    splitter = (
        RecursiveCharacterTextSplitter(

            chunk_size=1000,

            chunk_overlap=200,

            add_start_index=True
        )
    )


    return splitter.split_documents(
        documents
    )


def get_vectorstore():

    embeddings = (
        get_embedding_model()
    )


    vectorstore = Chroma(

        collection_name=
            COLLECTION_NAME,

        embedding_function=
            embeddings,

        persist_directory=
            str(CHROMA_DIR)
    )


    return vectorstore


def build_vectorstore():

    documents = load_documents()


    if len(documents) == 0:

        raise ValueError(
            "No scientific documents found "
            "inside rag/documents/"
        )


    chunks = split_documents(
        documents
    )


    embeddings = (
        get_embedding_model()
    )


    # Rebuild clean database
    if CHROMA_DIR.exists():

        import shutil

        shutil.rmtree(
            CHROMA_DIR
        )


    vectorstore = Chroma.from_documents(

        documents=chunks,

        embedding=embeddings,

        collection_name=
            COLLECTION_NAME,

        persist_directory=
            str(CHROMA_DIR)
    )


    return {
        "documents":
            len(documents),

        "chunks":
            len(chunks),

        "path":
            str(CHROMA_DIR)
    }