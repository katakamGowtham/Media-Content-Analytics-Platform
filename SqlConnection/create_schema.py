from sqlalchemy import create_engine, text
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# MySQL connection details
MYSQL_USER =os.getenv('username')
MYSQL_PASSWORD =os.getenv('password')
MYSQL_HOST =os.getenv('host')
MYSQL_PORT = 3306
NEW_DATABASE =os.getenv('database')

try:
    print("🔄 Connecting to MySQL...")

    # Connect to MySQL (without specifying a database)
    engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}", echo=True)

    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {NEW_DATABASE}"))
        print(f"✅ Database '{NEW_DATABASE}' created or already exists!")

    # Connect to the new database
    engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{NEW_DATABASE}", echo=True)

    with engine.connect() as conn:
        print("✅ Connected to the new database!")

        # Creating tables based on the STAR SCHEMA
        create_table_queries = [
            """
            CREATE TABLE IF NOT EXISTS fact_content (
                headline_id INT PRIMARY KEY,
                headline TEXT NOT NULL,
                date_id INT,
                category_id INT,
                engagement_id INT,
                FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
                FOREIGN KEY (category_id) REFERENCES dim_content(category_id),
                FOREIGN KEY (engagement_id) REFERENCES dim_engagement(engagement_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS dim_engagement (
                engagement_id INT PRIMARY KEY,
                headline_id INT,
                date_id INT,
                views INT,
                likes INT,
                comments INT,
                engagement_rate FLOAT,
                FOREIGN KEY (headline_id) REFERENCES fact_content(headline_id),
                FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS dim_date (
                date_id INT PRIMARY KEY,
                publish_date DATE,
                day INT,
                month INT,
                year INT,
                week INT,
                day_of_week VARCHAR(20)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS dim_content (
                category_id INT PRIMARY KEY,
                grouped_category VARCHAR(255)
            );
            """
        ]

        for query in create_table_queries:
            conn.execute(text(query))

        print("✅ Star schema tables created successfully!")

except Exception as e:
    print(f"❌ Error: {e}")



