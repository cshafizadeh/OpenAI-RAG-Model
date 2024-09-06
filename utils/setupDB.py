import pyodbc

# Database connection string
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"  # Replace with your server name
    "DATABASE=master;"   # Connect to the master database first to create the new database
    "Trusted_Connection=yes;"  # Use Windows Authentication
)

# Connect to the SQL Server
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Create the VectorDB database if it doesn't exist
cursor.execute("IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'VectorDB') BEGIN CREATE DATABASE VectorDB; END")
conn.commit()

# Connect to the new VectorDB database
conn_str_vectordb = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"  # Replace with your server name
    "DATABASE=VectorDB;"  # Now connect to the newly created database
    "Trusted_Connection=yes;"  # Use Windows Authentication
)

conn_vectordb = pyodbc.connect(conn_str_vectordb)
cursor_vectordb = conn_vectordb.cursor()

# Create the vectortable if it doesn't exist
cursor_vectordb.execute("""
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[vectortable]') AND type in (N'U'))
BEGIN
    CREATE TABLE vectortable (
        text TEXT NOT NULL,
        vector VARBINARY(MAX) NOT NULL
    );
END
""")
conn_vectordb.commit()

print("Database and table setup complete.")

# Close connections
cursor.close()
conn.close()
cursor_vectordb.close()
conn_vectordb.close()
