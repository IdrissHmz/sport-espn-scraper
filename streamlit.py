import streamlit as st
import pandas as pd

# Example DataFrame (replace with your actual DataFrame)
data = {
    "id": [1, 2, 3, 4, 5],
    "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
    "age": [25, 30, 35, 40, 45],
    "city": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
}
df = pd.read_csv('cached_players.csv')

# Streamlit App
st.title("DataFrame Query App")

# Sidebar for user input
st.sidebar.header("Query Options")
query = st.sidebar.text_area("Write your query (e.g., df[df['age'] > 30]):", "df")

# Execute query button
if st.sidebar.button("Execute Query"):
    try:
        # Execute the query on the DataFrame
        result = eval(query)  # Use eval to run the query on the DataFrame
        
        # Check if the result is a DataFrame
        if isinstance(result, pd.DataFrame):
            # Display the results
            st.subheader("Query Results")
            st.write(result)

            # Downloadable CSV option
            csv = result.to_csv(index=False)
            st.download_button(
                label="Download results as CSV",
                data=csv,
                file_name="query_results.csv",
                mime="text/csv",
            )
        else:
            st.error("The result of the query is not a DataFrame.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
