import streamlit as st
import pymysql
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# --------------------- MySQL Connection ---------------------
def get_connection():
    return pymysql.connect(
        host=os.getenv('host'),
        user=os.getenv('username'),
        password=os.getenv('password'),
        database=os.getenv('database')
    )

def run_query(query):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
    conn.close()
    return df

# --------------------- Page Layout ---------------------
st.set_page_config(page_title="Media Analytics Dashboard", layout="wide")

st.title("📊 Media Content Analytics Dashboard")

# Tabs 
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Content Insights", "Engagement Trends", "Category Analysis", "Run Custom Query"])

# --------------------- TAB 1: Overview ---------------------
with tab1:
    st.subheader("📌 Overview of Media Analytics")

    st.write("""
    The **Media Content Analytics Platform** provides valuable insights into media content performance 
    by analyzing engagement metrics from YouTube and news sources. This dashboard helps track content 
    popularity, identify high-engagement categories, and optimize content strategy based on data-driven 
    decision-making.
    """)

    st.markdown("""
    **Key Features of the Dashboard:**  
    - 📊 **Analyze Content Performance:** Track views, likes, comments, and engagement trends.  
    - 🔍 **Discover Popular Categories:** Identify the best-performing topics and content types.  
    - 📅 **Time-Based Analysis:** Understand engagement trends across different time periods.  
    - 📈 **Interactive Insights:** Filter data dynamically and execute custom SQL queries.  
    """)

    col1, col2, col3 = st.columns(3)

    # Total Unique Headlines
    total_headlines = run_query("SELECT COUNT(DISTINCT headline) FROM fact_content;").iloc[0, 0]
    total_headlines = int(total_headlines) if total_headlines is not None else 0

    # Total Views
    total_views = run_query("SELECT SUM(views) FROM dim_engagement;").iloc[0, 0]
    total_views = int(total_views) if total_views is not None else 0

    # Average Engagement Rate (Multiply by 100 for percentage)
    avg_engagement = run_query("SELECT AVG(engagement_rate) FROM dim_engagement;").iloc[0, 0]
    avg_engagement = float(avg_engagement) * 100 if avg_engagement is not None else 0

    col1.metric("Total Unique Headlines", f"{total_headlines:,}")
    col2.metric("Total Views", f"{total_views:,}")
    col3.metric("Avg. Engagement Rate (%)", f"{round(avg_engagement, 2)}%")

    st.write("""
    📌 **Why Use This Dashboard?**  
    - Helps content creators and marketers optimize strategies.  
    - Provides in-depth analysis of user engagement patterns.  
    - Assists in making data-driven decisions for better content reach.  
    """)


# --------------------- TAB 2: Content Insights ---------------------
with tab2:
    st.subheader("🔥 Top Performing Content")

    df = pd.DataFrame()

    insight_type = st.radio(
        "Choose Analysis Type:",
        ["Most Viewed Content", "Most Viewed Content based on headline","Most Liked Content based on headline", "Most Commented Content based on headline", "Highest Engagement Rate"]
    )

    if insight_type == "Most Viewed Content":
        df = run_query("""
        SELECT DISTINCT c.grouped_category, SUM(e.views) AS total_views
        FROM fact_content f
        JOIN dim_engagement e ON f.engagement_id = e.engagement_id
        JOIN dim_content c ON f.category_id = c.category_id
        GROUP BY c.grouped_category
        ORDER BY total_views DESC;
        """)

    elif insight_type == "Most Viewed Content based on headline":
        df = run_query("""
            SELECT DISTINCT f.headline, e.views
            FROM fact_content f
            JOIN dim_engagement e ON f.engagement_id = e.engagement_id
            ORDER BY e.views DESC
            LIMIT 100;
        """)

    
    elif insight_type == "Most Liked Content based on headline":
        df = run_query("""
            SELECT DISTINCT f.headline, e.likes
            FROM fact_content f
            JOIN dim_engagement e ON f.engagement_id = e.engagement_id
            ORDER BY e.likes DESC
            LIMIT 100;
        """)
    
    elif insight_type == "Most Commented Content based on headline":
        df = run_query("""
            SELECT DISTINCT f.headline, e.comments
            FROM fact_content f
            JOIN dim_engagement e ON f.engagement_id = e.engagement_id
            ORDER BY e.comments DESC
            LIMIT 100;
        """)
    
    elif insight_type == "Highest Engagement Rate":
        df = run_query("""
            SELECT DISTINCT f.headline, e.engagement_rate
            FROM fact_content f
            JOIN dim_engagement e ON f.engagement_id = e.engagement_id
            WHERE e.engagement_rate > 0.05
            ORDER BY e.engagement_rate DESC
            LIMIT 100;
        """)

    st.dataframe(df)


# --------------------- TAB 3: Engagement Trends ---------------------
with tab3:
    st.subheader("📈 Engagement Analytics")

    df = run_query("""
        SELECT DISTINCT f.headline, e.views, e.likes, e.comments, e.engagement_rate
        FROM fact_content f
        JOIN dim_engagement e ON f.engagement_id = e.engagement_id
        ORDER BY e.engagement_rate DESC
        LIMIT 50;
    """)

    fig = px.scatter(df, x="views", y="engagement_rate", size="likes", color="comments", title="Engagement Rate vs Views")
    st.plotly_chart(fig)

# --------------------- TAB 4: Category Analysis ---------------------
with tab4:
    st.subheader("📌 Category Trends")

    category_list = run_query("SELECT DISTINCT grouped_category FROM dim_content;")["grouped_category"].tolist()
    selected_category = st.selectbox("Select Category:", ["All"] + category_list)

    query = """
        SELECT DISTINCT c.grouped_category, SUM(e.views) AS total_views, SUM(e.likes) AS total_likes
        FROM fact_content f
        JOIN dim_content c ON f.category_id = c.category_id
        JOIN dim_engagement e ON f.engagement_id = e.engagement_id
    """
    
    if selected_category != "All":
        query += f" WHERE c.grouped_category = '{selected_category}'"
    
    query += " GROUP BY c.grouped_category ORDER BY total_views DESC;"
    
    df = run_query(query)

    # Existing Pie Chart: Category-Wise Views Distribution
    fig = px.pie(df, names="grouped_category", values="total_views", title="Category-Wise Views Distribution")
    st.plotly_chart(fig)

    # Existing Bar Chart: Number of Posts Per Category
    st.subheader("📊 Number of Posts Per Category")
    df_count = run_query("""
        SELECT c.grouped_category, COUNT(*) AS post_count
        FROM fact_content f
        JOIN dim_content c ON f.category_id = c.category_id
        GROUP BY c.grouped_category;
    """)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(y=df_count["grouped_category"], x=df_count["post_count"], palette="viridis", ax=ax)
    ax.set_xlabel("Number of Posts")
    ax.set_ylabel("Category")
    ax.set_title("Content Count per Category")
    st.pyplot(fig)

    df_trends = run_query("""
    SELECT c.grouped_category, d.month, d.year, 
           SUM(e.views) AS total_views, SUM(e.likes) AS total_likes
    FROM fact_content f
    JOIN dim_content c ON f.category_id = c.category_id
    JOIN dim_engagement e ON f.engagement_id = e.engagement_id
    JOIN dim_date d ON f.date_id = d.date_id
    GROUP BY c.grouped_category, d.year, d.month
    ORDER BY d.year, d.month, c.grouped_category;
""")

# Convert month to string for better plotting
df_trends['month'] = df_trends['month'].astype(str)

# Sidebar Filter for Categories
selected_categories = st.multiselect("Select Categories", df_trends["grouped_category"].unique(), default=df_trends["grouped_category"].unique())

# Filter data based on selection
df_filtered = df_trends[df_trends["grouped_category"].isin(selected_categories)]

st.subheader("📈 Category Engagement Trends Over Time")

# --- Views Over Time ---
st.write("### 📊 Category-Wise Views Over Time")
fig, ax = plt.subplots(figsize=(12, 5))
sns.lineplot(data=df_filtered, x="month", y="total_views", hue="grouped_category", marker="o", ax=ax)
ax.set_ylabel("Total Views")
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))  # Format numbers with commas
ax.set_yscale("linear")  # Ensure normal scale
st.pyplot(fig)

# --- Likes Over Time ---
st.write("### ❤️ Category-Wise Likes Over Time")
fig, ax = plt.subplots(figsize=(12, 5))
sns.lineplot(data=df_filtered, x="month", y="total_likes", hue="grouped_category", marker="o", ax=ax)
ax.set_ylabel("Total Likes")
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))  # Format numbers with commas
ax.set_yscale("linear")  # Ensure normal scale
st.pyplot(fig)
   


# --------------------- TAB 5: Run Custom Query ---------------------
with tab5:
    st.subheader("📝 Execute Your SQL Query")

    user_query = st.text_area("Enter your SQL query:", "SELECT DISTINCT headline, views FROM fact_content JOIN dim_engagement ON fact_content.engagement_id = dim_engagement.engagement_id ORDER BY views DESC LIMIT 5;")

    if st.button("Run Query"):
        try:
            df = run_query(user_query)
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error: {e}")

# --------------------- Footer ---------------------
st.markdown("🔹 **Media Content Dashboard | Powered by MySQL & Streamlit**")





