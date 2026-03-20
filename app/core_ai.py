import os
import chromadb
import fitz
from groq import Groq
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from crewai import Agent, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(..., description="Teks murni untuk dicari.")
    class Config:
        extra = "forbid"

class ChromaSearchTool(BaseTool):
    name: str = "pencarian_dokumen"
    description: str = "Hanya mencari teks di PDF lokal. Input wajib string murni."
    args_schema: type[BaseModel] = SearchInput

    def _run(self, query: str) -> str:
        # Pengecekan similarity (distance < 0.5 berarti cukup relevan)
        if collection is None:
            process_documents()
            
        # Perluas singkatan umum dengan kata kunci semantik agar embedding ChromaDB bisa mencocokkan makna definisi
        query_expanded = query.replace("DKV", "pengertian definisi Desain Komunikasi Visual")
            
        results = collection.query(
            query_texts=[query_expanded.strip()],
            n_results=8
        )
        
        if not results['documents'] or not results['documents'][0]:
            return "DATA_NOT_FOUND"
        
        formatted_results = []
        for doc, meta, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
            source = meta.get('source', 'Unknown')
            formatted_results.append(f"[File: {source}]\n{doc}")
            
        if not formatted_results:
            return "DATA_NOT_FOUND"
            
        return "\n\n---\n\n".join(formatted_results)

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = None

def process_documents():
    global collection
    collection = chroma_client.get_or_create_collection(name="librai")
    
    # Perbarui data setiap kali server restart untuk memastikan dokumen terbaru masuk
    try:
        chroma_client.delete_collection(name="librai")
        collection = chroma_client.create_collection(name="librai")
    except:
        collection = chroma_client.get_or_create_collection(name="librai")
    
    doc_dir = "./documents"
    if os.path.exists(doc_dir):
        for filename in os.listdir(doc_dir):
            if filename.endswith(".pdf"):
                filepath = os.path.join(doc_dir, filename)
                doc = fitz.open(filepath)
                text = ""
                for page in doc:
                    text += page.get_text()
                    
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500, 
                    chunk_overlap=100,
                    separators=["\n\n", "\n", ".", " "]
                )
                chunks = text_splitter.split_text(text)
                
                for i, chunk in enumerate(chunks):
                    collection.add(
                        documents=[chunk],
                        metadatas=[{"source": filename}],
                        ids=[f"{filename}-{i}"]
                    )

def ask_ai_fast(user_input):
    """
    Versi super cepat tanpa overhead agen CrewAI (ReAct loop). 
    Hanya butuh 1x Groq request.
    """
    # 1. Cari dokumen langsung ke ChromaDB (mirip tool)
    query_expanded = user_input.replace("DKV", "pengertian definisi Desain Komunikasi Visual")
    results = collection.query(
        query_texts=[query_expanded.strip()],
        n_results=8
    )
    
    context_text = "DATA_NOT_FOUND"
    if results['documents'] and results['documents'][0]:
        formatted_results = []
        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            source = meta.get('source', 'Unknown')
            formatted_results.append(f"[File: {source}]\n{doc}")
        if formatted_results:
            context_text = "\n\n---\n\n".join(formatted_results)
            
    # 2. Panggil LLM sekali saja via Groq API
    prompt = f"""Tugas kamu: Jawab pertanyaan berikut HANYA menggunakan info dari dokumen teks di bawah. 
Catatan: 'DKV' adalah akronim dari 'Desain Komunikasi Visual'.
Jika info tidak ada di teks, jawab 'Maaf, info tidak ditemukan'.
Sertakan juga nama file sumber dari label [File: ...]. DILARANG NGARANG.

Pertanyaan: '{user_input}'

Teks Dokumen Referensi:
{context_text}
"""
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Anda adalah asisten akademik yang menjawab akurat berdasarkan teks."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    return completion.choices[0].message.content


# Inisialisasi dokumen saat import agar database siap
if collection is None:
    process_documents()