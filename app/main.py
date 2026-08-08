import streamlit as st
# from dotenv import load_dotenv
import os # Make sure os is imported

# Load variables from .env file
# load_dotenv()

# --- DEBUGGING STEP ---
# Check if the API key was loaded successfully
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("🔴 ERROR: GEMINI_API_KEY not found!")
    st.info("Please make sure you have a .env file in the same directory as main.py with the line: GEMINI_API_KEY='your_api_key'")
    st.stop() # Stop the app if the key is missing
# --- END DEBUGGING STEP ---

# If the script continues, it means the key was found.
# We only import the rest of our app if the key exists.
from langchain_utils import invoke_chain

st.title("Langchain NL2SQL Chatbot") # Update title to reflect Gemini usage
# --- TEMPORARY DATABASE POPULATION STEP ---
try:
    import pymysql
    import os
    import streamlit as st
    # Connect to the database using your Streamlit secrets
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST") or st.secrets.get("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER") or st.secrets.get("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD") or st.secrets.get("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB") or st.secrets.get("MYSQL_DB"),
        port=int(os.getenv("MYSQL_PORT") or st.secrets.get("MYSQL_PORT", 11205))
    )
    with conn.cursor() as cursor:
        # Create all the tables the LLM expects to see
        queries = [
            "CREATE TABLE IF NOT EXISTS customers (customerNumber INT PRIMARY KEY, customerName VARCHAR(50), country VARCHAR(50), creditLimit INT)",
            "CREATE TABLE IF NOT EXISTS payments (customerNumber INT, amount INT, paymentDate DATE)",
            "CREATE TABLE IF NOT EXISTS products (productCode VARCHAR(50) PRIMARY KEY, productName VARCHAR(50), productLine VARCHAR(50), quantityInStock INT, buyPrice INT, MSRP INT)",
            "CREATE TABLE IF NOT EXISTS orders (orderNumber INT PRIMARY KEY, orderDate DATE, status VARCHAR(50), customerNumber INT)",
            "CREATE TABLE IF NOT EXISTS orderdetails (orderNumber INT, productCode VARCHAR(50), quantityOrdered INT, priceEach INT)",
            "CREATE TABLE IF NOT EXISTS productlines (productLine VARCHAR(50) PRIMARY KEY, textDescription VARCHAR(255))",
            "CREATE TABLE IF NOT EXISTS offices (officeCode VARCHAR(50) PRIMARY KEY, city VARCHAR(50), country VARCHAR(50))"
        ]
        for q in queries:
            cursor.execute(q)
        conn.commit()
    conn.close()
except Exception as e:
    st.sidebar.error(f"Database init status: {e}")
# ------------------------------------------
# Remove OpenAI API key setting and client initialization
# client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

# Remove setting a default OpenAI model
# if "openai_model" not in st.session_state:
#     st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    # print("Creating session state")
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.spinner("Generating response..."):
        with st.chat_message("assistant"):
            # Directly use invoke_chain which is now Gemini-configured
            response = invoke_chain(prompt,st.session_state.messages)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
