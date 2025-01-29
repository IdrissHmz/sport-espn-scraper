import streamlit as st
import cx_Oracle

def connect_to_oracle():
    """Establishes a connection to the Oracle XE database."""
    ip = 'localhost'
    port = 1521
    SID = 'XE'
    dsn_tns = cx_Oracle.makedsn(ip, port, service_name=SID)
    role = cx_Oracle.SYSDBA  # Use SYSDBA or SYSOPER

    try:
        connection = cx_Oracle.connect(
            user="sys", password='abcd',
            dsn=dsn_tns,  # Replace with your Oracle XE DSN
            mode=role
        )
        return connection
    except cx_Oracle.Error as error:
        st.error(f"Error connecting to Oracle XE database: {error}")
        return None

def execute_oracle_query(connection, query):
    """Executes a query using a defined function in Oracle XE."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            return results
    except cx_Oracle.Error as error:
        st.error(f"Error executing query: {error}")
        return None

# def connect():
#     """Establishes a connection to the Oracle XE database."""
#     try:
#         connection = cx_Oracle.connect(
#             user="sys",
#             password="abcd",
#             dsn="localhost/XEPDB1"  # Replace with your Oracle XE DSN
#         )
#         return connection
#     except cx_Oracle.Error as error:
#         st.error(f"Error connecting to Oracle XE database: {error}")
#         return None

def call_search_soccer_data_proc(connection, search_string):
    """Calls the search_soccer_data_proc procedure."""
    try:
        with connection.cursor() as cursor:
            result_cursor = cursor.var(cx_Oracle.CURSOR)
            cursor.callproc("search_soccer_data_proc", [search_string, result_cursor])
            results = result_cursor.getvalue().fetchall()
            return results
    except cx_Oracle.Error as error:
        st.error(f"Error executing procedure search_soccer_data_proc: {error}")
        return None

def call_filtered_search_proc(connection, league, club, year, height_range, weight_range, age_range, goals_range):
    """Calls an Oracle procedure with the filters as parameters."""
    try:
        with connection.cursor() as cursor:
            result_cursor = cursor.var(cx_Oracle.CURSOR)
            cursor.callproc(
                "filtered_search_proc",  # Replace with your actual procedure name
                [league, club, year, height_range[0], height_range[1], weight_range[0], weight_range[1], age_range[0], age_range[1], goals_range[0], goals_range[1], result_cursor]
            )
            results = result_cursor.getvalue().fetchall()
            return results
    except cx_Oracle.Error as error:
        st.error(f"Error executing procedure filtered_search_proc: {error}")
        return None


def main():

    conn = connect_to_oracle()
    
    # Set the app title
    st.title("Search App")

    # Sidebar filters section
    st.sidebar.header("Filters")

    # Section for Leagues
    st.sidebar.subheader("Leagues")
    league = st.sidebar.selectbox("Select League", ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"])

    # Section for Clubs
    st.sidebar.subheader("Clubs")
    clubs = {
        "Premier League": ["Manchester United", "Liverpool", "Chelsea"],
        "La Liga": ["Barcelona", "Real Madrid", "Atletico Madrid"],
        "Bundesliga": ["Bayern Munich", "Borussia Dortmund", "RB Leipzig"],
        "Serie A": ["Juventus", "Inter Milan", "AC Milan"],
        "Ligue 1": ["Paris Saint-Germain", "Lyon", "Marseille"]
    }
    club = st.sidebar.selectbox("Select Club", clubs.get(league, []))

    # Section for Players
    st.sidebar.subheader("Players")
    year = st.sidebar.slider("Year", 2000, 2024, 2022)
    height = st.sidebar.slider("Height (cm)", 150, 210, (170, 190))
    weight = st.sidebar.slider("Weight (kg)", 50, 120, (70, 90))
    age = st.sidebar.slider("Age", 16, 40, (20, 30))
    goals = st.sidebar.slider("Goals", 0, 50, (10, 30))

    
    # Text input in the middle
    query = st.text_input("Enter your search query:", "", key="search_query")

    # Wider scrollable result section
    st.markdown("### Results")
    #st.text_area("Results will appear here:", "", height=300, key="results_area", help="Scrollable and wider result area")

    ## Logic to display results based on the input (placeholder logic)
    # if query:
    #     # Connect to the Oracle XE database
    #     connection = connect_to_oracle()
    #     if connection:
    #         results = call_search_soccer_data_proc(connection, query)
    #         if results:
    #             formatted_results = "\n".join([str(row) for row in results])
    #             st.text_area("Results", formatted_results, height=300, help="Scrollable and wider result area")
    #         connection.close()
    
    # # Logic to call the Oracle procedure and display results based on filters
    # if st.button("Search with Filters"):
    #     connection = connect_to_oracle()
    #     if connection:
    #         results = call_filtered_search_proc(connection, league, club, year, height, weight, age, goals)
    #         if results:
    #             formatted_results = "\n".join([str(row) for row in results])
    #             st.text_area("Results", formatted_results, height=300, help="Scrollable and wider result area")
    #         connection.close()
if __name__ == "__main__":
    main()
