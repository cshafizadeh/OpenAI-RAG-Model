import os
import struct
import pyodbc
import openai
import argparse
from openai import OpenAI
from typing import List, Tuple
from dotenv import load_dotenv

# DESCRIPTION:
# This is a RAG model that uses OpenAI and embeddings to create a custom ChatGPT model based on 
# documents/information stored in a database in the form of vectors. When the user types in a 
# prompt, the prompt is converted into a vector. This vector is then compared to the vectors stored
# in the database, allowing for a similarity "score" to be calculated between the prompt and 
# information stored in the db. The program grabs the "top_k" most relevant documents, and if the
# score is high enough for these documents, then the information is added to the context given to
# the OpenAI message before being sent to the model. This allows for relevant custom information to
# be used in answering question in a ChatGPT chat.

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI()

# Database connection (modify with your actual connection details)
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"  # Replace with your server name
    "DATABASE=VectorDB;"  # Replace with your actual database name
    "Trusted_Connection=yes;"  # Use Windows Authentication
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()


# Retrieve embeddings from the database
def get_embeddings_from_db() -> List[Tuple[str, List[float]]]:
    cursor.execute("SELECT text, vector FROM vectortable")
    results = cursor.fetchall()
    embeddings = []
    for row in results:
        text = row[0]
        binary_blob = row[1]
        # Unpack the binary blob back into a list of floats
        num_floats = len(binary_blob) // struct.calcsize('f')
        embedding = struct.unpack(f'{num_floats}f', binary_blob)
        embeddings.append((text, embedding))
    return embeddings


# Function to calculate dot product
def dot_product(vector1: List[float], vector2: List[float]) -> float:
    return sum(a * b for a, b in zip(vector1, vector2))


# Function to create embedding out of user input
def generate_embedding_for_query(query: str, model="text-embedding-3-small") -> List[float]:
    # Get the embedding for the query
    response = openai.embeddings.create(input=query, model=model)
    return response.data[0].embedding


# Calculates distance between embeddings and retrieves the "top_k" closest stored embeddings
def get_most_relevant_texts(query_embedding, stored_embeddings, top_k=3) -> List[Tuple[str, float]]:
    scores = []
    for text, embedding in stored_embeddings:
        score = dot_product(query_embedding, embedding)
        scores.append((text, score))
    # Sort by score in descending order (highest similarity first)
    scores.sort(key=lambda x: x[1], reverse=True)
    # Return the top_k most relevant texts and their scores
    return scores[:top_k]


# Use found embeddings to generate response with chatgpt
def generate_chatgpt_response(query: str, stored_embeddings, show_scores=False, model="text-embedding-3-small", score_threshold=0.5, top_k=3):
    # Generate the embedding for the input query
    query_embedding = generate_embedding_for_query(query, model=model)
    # Retrieve the most relevant texts from the database
    relevant_texts_with_scores = get_most_relevant_texts(query_embedding, stored_embeddings, top_k)
    # Show the top_k scores if the flag is enabled
    if show_scores:
        print(f"\nTop {top_k} relevant scores for the query:\n")
        for text, score in relevant_texts_with_scores:
            print(f"Score: {score:.4f}, Text snippet: {text[:50]}...")
    # Filter out results below the score threshold
    high_score_texts = [(text, score) for text, score in relevant_texts_with_scores if score >= score_threshold]
    if not high_score_texts:
        # No relevant data in the DB above the threshold, respond without DB context
        no_data_response = "I could not find relevant data in the database. Here's what I can tell you based on my knowledge:"
        chatgpt_response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{no_data_response} {query}"}
            ],
            stream=True
        )
        # Stream chunks as they arrive
        for chunk in chatgpt_response:
            chunk_text = chunk.choices[0].delta.content
            print(chunk_text, end="", flush=True)  # Print chunk as it arrives
        print("\n")  # Newline after complete response
        return
    # Extract texts and sources for the prompt
    relevant_texts = [text for text, _ in high_score_texts]
    # Construct a prompt that includes the relevant texts and sources
    prompt = f"The user asked: {query}\n\nHere is some context that might help:\n"
    prompt += "\n".join(relevant_texts)
    prompt += "\n\nNow, generate a response based on the above context."
    # Generate a response using ChatGPT
    chatgpt_response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )
    # Stream chunks as they arrive
    for chunk in chatgpt_response:
        chunk_text = chunk.choices[0].delta.content
        print(chunk_text, end="", flush=True)  # Print chunk as it arrives
    print("\n")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Chatbot with optional score display")
    parser.add_argument("-s", "--show-scores", action="store_true", help="Show the top_k scores for each prompt")
    args = parser.parse_args()
    # Fetch embeddings from the database
    stored_embeddings = get_embeddings_from_db()
    while True:
        prompt = input("Prompt: ")
        if prompt.lower() in ["quit", "exit"]:
            break
        elif prompt.lower() == "help":
            print("Help (Coming Soon)")
        else:
            if prompt is not None and prompt != "":
                # Generate the response using ChatGPT and relevant information from database
                generate_chatgpt_response(prompt, stored_embeddings, show_scores=args.show_scores)


if __name__ == "__main__":
    main()
