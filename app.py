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
from langchain_experimental.data_anonymizer import PresidioAnonymizer
from presidio_anonymizer.entities import OperatorConfig
from langchain_core.prompts import PromptTemplate

prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an assistant that helps users with their medical analysis. The following context may contain sensitive information. Ensure that your response does not include any Personally Identifiable Information (PII) such as names, phone numbers, email addresses.

Context: {context}
Query: {question}

Provide a safe and anonymized response that answers the query while respecting privacy guidelines.
"""
)
anonymizer = PresidioAnonymizer(analyzed_fields=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS"],
    operators={
        "PERSON": OperatorConfig("redact", {}),
        "PHONE_NUMBER": OperatorConfig("redact", {}),
        "EMAIL_ADDRESS": OperatorConfig("redact", {}),
    })
llm = Ollama(model="llama3.1")
app = Flask(__name__)
CORS(app)


# Function to anonymize PII from the extracted text
def anonymize_pii(text):
    return anonymizer.anonymize(text)


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
    chain_type_kwargs={"prompt": prompt_template}
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
