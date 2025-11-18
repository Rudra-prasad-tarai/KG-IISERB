#!/usr/bin/env python3

"""
build_index_gpu.py
------------------

Builds a FAISS vector index using GPU embeddings.

Usage:
    python3 build_index_gpu.py --cleaned_dir ./cleaned_html --output faiss_index

Notes:
 - Uses BAAI/bge-large-en   (best open-source embedding model)
 - Runs embedding on GPU (cuda)
 - FAISS index is stored on CPU for compatibility
"""

import os
import argparse
import torch
from tqdm import tqdm

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


# -------------------------------------------------------
# Load cleaned .txt files
# -------------------------------------------------------
def load_cleaned_text(cleaned_dir):
    docs = []
    for fname in os.listdir(cleaned_dir):
        if fname.endswith(".txt"):
            path = os.path.join(cleaned_dir, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    docs.append({"text": f.read(), "source": fname})
            except Exception as e:
                print(f"[WARN] Failed to read {fname}: {e}")
    return docs


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cleaned_dir", default="./cleaned_html")
    parser.add_argument("--output", default="faiss_index")
    args = parser.parse_args()

    cleaned_dir = args.cleaned_dir
    output_index = args.output

    if not os.path.exists(cleaned_dir):
        raise ValueError(f"Cleaned directory not found: {cleaned_dir}")

    print(f"\n[INFO] Loading cleaned text from: {cleaned_dir}")
    raw_docs = load_cleaned_text(cleaned_dir)

    if len(raw_docs) == 0:
        raise ValueError("No .txt files found in cleaned_html directory!")

    print(f"[INFO] Found {len(raw_docs)} files.")

    # -------------------------------------------------------
    # Chunk text
    # -------------------------------------------------------
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    texts, metas = [], []
    print("\n[INFO] Splitting into chunks...")
    for doc in tqdm(raw_docs):
        chunks = splitter.split_text(doc["text"])
        for ch in chunks:
            texts.append(ch)
            metas.append({"source": doc["source"]})

    print(f"[INFO] Total chunks: {len(texts)}")

    # -------------------------------------------------------
    # GPU check
    # -------------------------------------------------------
    if not torch.cuda.is_available():
        print("\n[WARN] CUDA GPU NOT found, embeddings will run on CPU!")
        device = "cpu"
    else:
        print(f"\n[INFO] Using GPU: {torch.cuda.get_device_name(0)}")
        device = "cuda"

    # -------------------------------------------------------
    # Load GPU embeddings
    # -------------------------------------------------------
    print("\n[INFO] Loading embedding model (bge-large-en)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en",
        model_kwargs={"device": device},
        encode_kwargs={"normalize_embeddings": True}
    )

    # -------------------------------------------------------
    # Build FAISS index
    # -------------------------------------------------------
    print("\n[INFO] Creating FAISS index...")
    db = FAISS.from_texts(texts, embeddings, metadatas=metas)

    # -------------------------------------------------------
    # Save FAISS index
    # -------------------------------------------------------
    print(f"[INFO] Saving FAISS index → {output_index}")
    db.save_local(output_index)

    print("\n[OK] Index build complete!")
    print("[OK] You can now query using query_index.py")


if __name__ == "__main__":
    main()
