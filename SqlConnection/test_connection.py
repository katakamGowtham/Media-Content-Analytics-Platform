import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",      # Change if using a remote server
        user="root",           # Replace with your MySQL username
        password="Gowtham@#123",  # Replace with your MySQL password
        database="media_content"  # Ensure this database exists
    )
    if conn.is_connected():
        print("Connected to MySQL successfully!")
    conn.close()
except mysql.connector.Error as e:
    print("Error:", e)
