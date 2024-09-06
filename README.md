<h1 align="center">OpenAI RAG Model</h1>
<div align="center">
  
  ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
  ![MicrosoftSQLServer](https://img.shields.io/badge/Microsoft%20SQL%20Server-CC2927?style=for-the-badge&logo=microsoft%20sql%20server&logoColor=white)
  ![ChatGPT](https://img.shields.io/badge/chatGPT-74aa9c?style=for-the-badge&logo=openai&logoColor=white)
  
</div>

<h2>Description:</h2>
<p>
This is a Retrieval-Augmented Generation (RAG) project using OpenAI's GPT-based models, coupled with a Microsoft SQL Server database. 
The core functionality revolves around generating text embeddings from large datasets, such as documents or website content, and storing those embeddings in a 
vector database for efficient retrieval. The project leverages OpenAI’s embeddings API to create vector representations of text chunks and stores them in SQL 
Server as binary data.

The main application of this project is to allow users to input queries, which are then transformed into embeddings and compared against the stored embeddings 
in the database. Based on similarity scores, the most relevant pieces of information are retrieved and used to generate a detailed response via OpenAI's GPT-4 model.
This project can be used for knowledge management, document retrieval, and other NLP-related applications.
</p>

<h2>How It Works:</h2>
<p>
RAG Models use "embeddings" or numerical representations of words in order to perform calculations on them to determine the similarity between the users prompt 
and information stored in the database. Documents (.md files in this case) are split up into "chunks" for easier processing, and then usng the OpenAI embeddings
API, these chunks are converted into vectors. These vectors are an array of floating point numbers, representing coordinates in a 1536-dimension space. These
vectors are converted into a binary blob in order to store it in the SQL server, and then inserted into the SQL database.

When the user starts the "main.py" file, the program retrieves all of the embeddings in the database, and converts it from binary back into vectors. When the user
types in a prompt, the users prompt is converted into an embedding. By converting the users prompt into an embedding, it can now be compared against the embeddings
from the database (the external information/documents) for similarity. By using the dot product, the program is able to find the distance between the prompt and 
each of the embeddings from the database. The "top_k" scores (in this case 3) are retrieved, and if the value of these scores is high enough, the text content of 
each embedding is added to the context of the ChatGPT message being created. The reason for the score "threshold" is so that documents are not used in unrelated 
prompts (ex. If my embeddings contain content on an instruction manual for a computer, and the prompt I ask is "how do I cook a lobster", the similarity scores will
all be very low, and I do not want to use the instruction manual as context for cooking a lobster). 

RAG Models are a flexible and scalable method of creating a custom ChatGPT model with information it might not have access to or have knowledge of by default.
</p>

<h2>Getting Set Up:</h2>

<p>In order to run this program, the following steps must be completed:</p>

1. Python must be installed and set up (built on 3.12)

2. Install the requirements.txt packages: ```pip install -r /path/to/requirements.txt```

1. Set up SQL server: ```python utils/setupDB.py```

2. Add .md files to the "data" folder (some webscraping scripts have already been created, but obviously will not apply to every website)

3. Run "openaiEmbeddings.py" to convert the .md files into embeddings and upload them into the DB

<h2>Running:</h2>

To run the program, execute ```python main.py```. To print out the "top_k" scores each input, run ```python main.py -s```

