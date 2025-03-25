import mysql.connector
# Establishing the connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Jasper@1007"
)

# Creating a cursor object
cursor = conn.cursor()

# Creating a new database
cursor.execute("CREATE DATABASE IF NOT EXISTS media_content;")

print("Database Connected successfully!")

# Selecting the database
cursor.execute("USE media_content;")