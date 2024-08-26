import re
import os
import PyPDF2
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.documents import Document
from langchain_community.llms import Ollama
from flask import Flask, request, jsonify
from flask_cors import CORS

llm = Ollama(model="llama3.1")
app = Flask(__name__)
CORS(app)


# Function to anonymize PII from the extracted text
def anonymize_pii(text):
    # Replace any patterns that resemble personal information
    # text = re.sub(r'\b(?:\d{1,2}/\d{1,2}/\d{2,4}|\d{4}[-/]\d{2}[-/]\d{2})\b', '[REDACTED DATE]', text)  # Date of birth
    # text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[REDACTED PHONE]', text)  # Phone numbers
    # text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED EMAIL]', text)  # Emails
    # text = re.sub(r'\b\d{4}\b', '[REDACTED YEAR]', text)  # Years
    # text = re.sub(r'\b[A-Z][a-z]+\b', '[REDACTED NAME]', text)  # Names (very basic)
    return text


# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return anonymize_pii(text)


# Extracting text from all PDFs in a directory
pdf_dir = "./data/"
documents = []

for filename in os.listdir(pdf_dir):
    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(os.path.join(pdf_dir, filename))
        documents.append(Document(page_content=text))

# Step 1: Create embeddings for the documents
embedding_model = OllamaEmbeddings(model="llama3.1")
docsearch = FAISS.from_documents(documents, embedding_model)

# Step 3: Create a RetrievalQA chain using the local LLM
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=docsearch.as_retriever(),
    return_source_documents=True,
)

# # Step 4: Define a query
# query = "Show me any information about the medical data that was collected."

# # Step 5: Run the query
# result = qa_chain({ "query": query })
# print(result)


@app.route("/query", methods=["POST"])
def query():
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"error": "No query provided"}), 400

    result = qa_chain({"query": query})
    return jsonify({"result": result["result"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
