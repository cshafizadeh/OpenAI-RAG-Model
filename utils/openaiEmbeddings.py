import openai
import pyodbc
import os
import struct
from dotenv import load_dotenv

# DESCRIPTION:
# This program takes all .md files inside of the "data" folder and splits the content
# inside the file into "chunks". Each chunk is then converted into an embedding using
# OpenAI's embeddings API. The embedding is then converted into binary for easy storage
# and then inserted into the database. If the chunk is found to already exist in the 
# database, then the insertion will be skipped (to avoid duplicate entries).


# Load environment variables (including OpenAI API key)
load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]

# Connect to VectorDB (modify connection string as needed)
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"  # Replace with your server name
    "DATABASE=VectorDB;"  # Replace with your actual database name
    "Trusted_Connection=yes;"  # Use Windows Authentication
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()


# Function to generate embeddings for a text chunk
def generate_embedding(text, model="text-embedding-3-small"):
    response = openai.embeddings.create(input=text, model=model)
    return response.data[0].embedding


# Function to split the content into smaller chunks
def split_content(content: str, chunk_size=2000):
    # Split by sentences (or any method you prefer)
    sentences = content.split(". ")
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


# Function to check if a text chunk already exists in the database
def chunk_exists(text_chunk):
    # Use LIKE for comparison instead of =
    cursor.execute("SELECT COUNT(*) FROM vectortable WHERE CAST(text AS NVARCHAR(MAX)) LIKE ?", text_chunk)
    count = cursor.fetchone()[0]
    return count > 0


# Function to upload text and embeddings to the database
def upload_to_vectordb(text_chunk, embedding):
    # Convert the embedding to binary
    binary_embedding = struct.pack(f'{len(embedding)}f', *embedding)
    # Insert into the database
    cursor.execute(
        "INSERT INTO vectortable (text, vector) VALUES (?, ?)",
        text_chunk,
        binary_embedding
    )
    conn.commit()


# Main function to process all .md files in the "data" folder
def process_md_files(folder_path):
    # Iterate through all .md files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            filepath = os.path.join(folder_path, filename)
            # Read the content of the .md file
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
            # Split the content into chunks
            chunks = split_content(content)
            # Generate embeddings and upload to the database
            for chunk in chunks:
                if chunk_exists(chunk):
                    print(f"Chunk already exists in the database, skipping: {chunk[:30]}...")
                    continue
                embedding = generate_embedding(chunk)
                upload_to_vectordb(chunk, embedding)
                print(f"Uploaded chunk from {filename} to VectorDB.")


if __name__ == "__main__":
    # Path to the folder containing .md files
    folder_path = "data"
    # Process all .md files and upload to VectorDB
    process_md_files(folder_path)
