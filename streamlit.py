import streamlit as st
import pandas as pd
from mysql.connector import Error

import mysql.connector

DB_CONFIG = dict(host="localhost", user="root", password="", database="project2")

def run_query(query):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute(query)
        rows = cur.fetchall()
        df = pd.DataFrame(rows)
        cur.close()
        conn.close()
        return df
    except Error as e:
        st.error(f"DB error: {e}")
        return pd.DataFrame()

st.set_page_config(page_title="Country Debt SQL Explorer", layout="wide")
st.title("Country Debt — SQL Queries")

query_options = [
    "1. Retrieve all distinct country names",
    "2. Count the total number of countries available",
    "3. Find the total number of indicators present",
    "4. Display the first 10 records of the dataset",
    "5. Calculate the total global debt",
    "6. List all unique indicator names",
    "7. Find the number of records for each country",
    "8. Display all records where debt is greater than 1 billion USD",
    "9. Find the minimum, maximum, and average debt values",
    "10. Count total number of records in the dataset",
    "11. Find the country with the lowest total debt",
    "12. Calculate total debt for each country and indicator combination",
    "13. Count how many indicators each country has",
    "14. Display countries whose total debt is above the global average",
    "15. Rank countries based on total debt (highest to lowest)",
    "16. Top 5 indicators contributing most to global debt",
    "17. Percentage contribution of each country to total global debt",
    "18. Top 3 countries for each indicator based on debt",
    "19. Difference between maximum and minimum debt for each country",
    "20. Create a view for the top 10 countries with highest debt",
    "21. Categorize countries into High/Medium/Low Debt",
    "22. Calculate cumulative debt per country with window functions",
    "23. Indicators where average debt is higher than overall average debt",
    "24. Countries contributing more than 5% of global debt",
    "25. Most dominant indicator for each country",
    "26. Find the total debt for each country",
    "27. Display the top 10 countries with the highest total debt",
    "28. Find the average debt per country",
    "29. Calculate total debt for each indicator",
    "30. Identify the indicator contributing the highest total debt",
]

query_map = {
    "1. Retrieve all distinct country names": 
                """SELECT DISTINCT `Country Name` FROM project2.Country_Debt ORDER BY `Country Name`;""",
    "2. Count the total number of countries available":
                """SELECT COUNT(DISTINCT `Country Name`) AS Total_Countries FROM project2.Country_Debt;""",
    "3. Find the total number of indicators present": 
                """SELECT COUNT(DISTINCT `Series Code`) AS Total_Indicators FROM project2.Country_Debt;""",
    "4. Display the first 10 records of the dataset": 
                """SELECT * FROM project2.Country_Debt LIMIT 10;""",
    "5. Calculate the total global debt": 
                """SELECT SUM(`Value`) AS Total_Global_Debt FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL;""",
    "6. List all unique indicator names": 
                """SELECT DISTINCT `Series Name` FROM project2.Country_Debt ORDER BY `Series Name`;""",
    "7. Find the number of records for each country": 
                """SELECT `Country Name`, COUNT(*) AS Record_Count FROM project2.Country_Debt 
                GROUP BY `Country Name` 
                ORDER BY Record_Count DESC;""",
    "8. Display all records where debt is greater than 1 billion USD": 
                """SELECT * FROM project2.Country_Debt WHERE `Value` > 1000000000;""",
    "9. Find the minimum, maximum, and average debt values": 
                """SELECT MIN(`Value`) AS Min_Debt, MAX(`Value`) AS Max_Debt, AVG(`Value`) AS Avg_Debt FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL;""",
    "10. Count total number of records in the dataset": 
                """SELECT COUNT(*) AS Total_Records FROM project2.Country_Debt;""",
    "11. Find the country with the lowest total debt": 
                """SELECT `Country Name`, SUM(`Value`) AS Total_Debt FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL GROUP BY `Country Name` ORDER BY Total_Debt ASC LIMIT 1;""",
    "12. Calculate total debt for each country and indicator combination": 
                """SELECT `Country Name`, `Series Code`, SUM(`Value`) AS Total_Debt FROM project2.Country_Debt
                WHERE `Value` IS NOT NULL GROUP BY `Country Name`, `Series Code` ORDER BY Total_Debt DESC;""",
    "13. Count how many indicators each country has": 
                """SELECT `Country Name`, COUNT(DISTINCT `Series Code`) AS Indicator_Count FROM project2.Country_Debt 
                GROUP BY `Country Name` ORDER BY Indicator_Count DESC;""",
    "14. Display countries whose total debt is above the global average": 
                """SELECT `Country Name`, SUM(`Value`) AS Total_Debt FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL 
                GROUP BY `Country Name` HAVING SUM(`Value`) > (SELECT AVG(total_debt) FROM (SELECT SUM(`Value`) AS total_debt FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL 
                GROUP BY `Country Name`) AS avg_table) 
                ORDER BY Total_Debt DESC;""",
    "15. Rank countries based on total debt (highest to lowest)": 
                """SELECT `Country Name`, SUM(`Value`) AS Total_Debt FROM project2.Country_Debt
                WHERE `Value` IS NOT NULL
                GROUP BY `Country Name` 
                ORDER BY Total_Debt DESC;""",
    "16. Top 5 indicators contributing most to global debt": 
                """SELECT `Series Name`, SUM(`Value`) AS Total_Debt FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL 
                GROUP BY `Series Name` 
                ORDER BY Total_Debt DESC LIMIT 5;""",
    "17. Percentage contribution of each country to total global debt": 
                """SELECT `Country Name`, SUM(`Value`) AS Total_Debt, SUM(`Value`)/global.Global_Total*100 AS Percent_Global FROM project2.Country_Debt, (SELECT SUM(`Value`) AS Global_Total FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL) AS global 
                WHERE `Value` IS NOT NULL 
                GROUP BY `Country Name` 
                ORDER BY Percent_Global DESC;""",
    "18. Top 3 countries for each indicator based on debt": 
                """SELECT `Series Name`, `Country Name`, Total_Debt FROM (SELECT `Series Name`, `Country Name`, SUM(`Value`) AS Total_Debt, ROW_NUMBER() OVER (PARTITION BY `Series Name` ORDER BY SUM(`Value`) DESC) AS rn FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL GROUP BY `Series Name`, `Country Name`) AS ranked 
                WHERE rn <= 3 ORDER BY `Series Name`, Total_Debt DESC;""",
    "19. Difference between maximum and minimum debt for each country": 
                """SELECT `Country Name`, MAX(`Value`) - MIN(`Value`) AS Debt_Difference FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL 
                GROUP BY `Country Name` 
                ORDER BY Debt_Difference DESC;""",
    "20. Create a view for the top 10 countries with highest debt": 
                """CREATE OR REPLACE VIEW project2.top_10_countries_debt AS SELECT `Country Name`, SUM(`Value`) AS Total_Debt FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL 
                GROUP BY `Country Name` 
                ORDER BY Total_Debt DESC LIMIT 10;""",
    "21. Categorize countries into High/Medium/Low Debt": 
                """SELECT `Country Name`, SUM(`Value`) AS Total_Debt, CASE WHEN SUM(`Value`) > 1000000000000 THEN 'High Debt' WHEN SUM(`Value`) > 100000000000 THEN 'Medium Debt' ELSE 'Low Debt' END AS Debt_Category FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL 
                GROUP BY `Country Name` 
                ORDER BY Total_Debt DESC;""",
    "22. Calculate cumulative debt per country with window functions": 
                """SELECT `Country Name`, `Series Name`, Total_Debt, SUM(Total_Debt) OVER (PARTITION BY `Country Name` ORDER BY Total_Debt DESC) AS Cumulative_Debt FROM (SELECT `Country Name`, `Series Name`, SUM(`Value`) AS Total_Debt FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL 
                GROUP BY `Country Name`, `Series Name`) AS country_indicator 
                ORDER BY `Country Name`, Cumulative_Debt DESC;""",
    "23. Indicators where average debt is higher than overall average debt": 
                """SELECT `Series Name`, AVG(`Value`) AS Avg_Debt FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL 
                GROUP BY `Series Name` HAVING AVG(`Value`) > (SELECT AVG(`Value`) FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL) 
                ORDER BY Avg_Debt DESC;""",
    "24. Countries contributing more than 5% of global debt": 
                """SELECT `Country Name`, SUM(`Value`) AS Country_Debt, ROUND((SUM(`Value`) / (SELECT SUM(`Value`) FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL)) * 100, 2) AS Debt_Percentage FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL 
                GROUP BY `Country Name` HAVING Debt_Percentage > 5 ORDER BY Debt_Percentage DESC;""",
    "25. Most dominant indicator for each country": 
                """SELECT `Country Name`, `Series Name`, Total_Debt FROM (SELECT `Country Name`, `Series Name`, SUM(`Value`) AS Total_Debt, ROW_NUMBER() OVER (PARTITION BY `Country Name` ORDER BY SUM(`Value`) DESC) AS rn FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL
                GROUP BY `Country Name`, `Series Name`) AS ranked 
                WHERE rn = 1 ORDER BY Total_Debt DESC;""",
    "26. Find the total debt for each country": 
                """SELECT `Country Name`, SUM(`Value`) AS Total_Debt FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL 
                GROUP BY `Country Name` 
                ORDER BY Total_Debt DESC;""",
    "27. Display the top 10 countries with the highest total debt": 
                """SELECT `Country Name`, SUM(`Value`) AS Total_Debt FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL 
                GROUP BY `Country Name` 
                ORDER BY Total_Debt DESC 
                LIMIT 10;""",
    "28. Find the average debt per country": 
                """SELECT `Country Name`, AVG(`Value`) AS Avg_Debt FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL 
                GROUP BY `Country Name` 
                ORDER BY Avg_Debt DESC;""",
    "29. Calculate total debt for each indicator": 
                """SELECT `Series Name`, SUM(`Value`) AS Total_Debt FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL 
                GROUP BY `Series Name` 
                ORDER BY Total_Debt DESC;""",
    "30. Identify the indicator contributing the highest total debt": 
                """SELECT `Series Name`, SUM(`Value`) AS Total_Debt FROM project2.Country_Debt 
                WHERE `Value` IS NOT NULL 
                GROUP BY `Series Name` 
                ORDER BY Total_Debt DESC 
                LIMIT 1;""",
}

selected_query = st.selectbox("Choose a query", query_options)

query_text = query_map[selected_query]
df = run_query(query_text)

if selected_query == "1. Retrieve all distinct country names":
    st.dataframe(df)
elif selected_query == "2. Count the total number of countries available":
    if not df.empty:
        st.metric("Total Countries", int(df.at[0, "Total_Countries"]))
    else:
        st.write(df)
elif selected_query == "3. Find the total number of indicators present":
    if not df.empty:
        st.metric("Total Indicators", int(df.at[0, "Total_Indicators"]))
    else:
        st.write(df)
elif selected_query == "4. Display the first 10 records of the dataset":
    st.dataframe(df)
elif selected_query == "5. Calculate the total global debt":
    if not df.empty and pd.notna(df.at[0, "Total_Global_Debt"]):
        total = float(df.at[0, "Total_Global_Debt"])
        st.metric("Total Global Debt (USD)", f"${total:,.2f}")
    else:
        st.write("No data available for total global debt.")
elif selected_query == "6. List all unique indicator names":
    st.dataframe(df)
elif selected_query == "7. Find the number of records for each country":
    st.dataframe(df)
elif selected_query == "8. Display all records where debt is greater than 1 billion USD":
    st.dataframe(df)
elif selected_query == "9. Find the minimum, maximum, and average debt values":
    if not df.empty:
        st.metric("Minimum Debt", f"${float(df.at[0, 'Min_Debt']):,.2f}")
        st.metric("Maximum Debt", f"${float(df.at[0, 'Max_Debt']):,.2f}")
        st.metric("Average Debt", f"${float(df.at[0, 'Avg_Debt']):,.2f}")
    else:
        st.write(df)
elif selected_query == "10. Count total number of records in the dataset":
    if not df.empty:
        st.metric("Total Records", int(df.at[0, "Total_Records"]))
    else:
        st.write(df)
elif selected_query == "11. Find the country with the lowest total debt":
    st.dataframe(df)
elif selected_query == "12. Calculate total debt for each country and indicator combination":
    st.dataframe(df)
elif selected_query == "13. Count how many indicators each country has":
    st.dataframe(df)
elif selected_query == "14. Display countries whose total debt is above the global average":
    st.dataframe(df)
elif selected_query == "15. Rank countries based on total debt (highest to lowest)":
    st.dataframe(df)
elif selected_query == "16. Top 5 indicators contributing most to global debt":
    st.dataframe(df)
elif selected_query == "17. Percentage contribution of each country to total global debt":
    st.dataframe(df)
elif selected_query == "18. Top 3 countries for each indicator based on debt":
    st.dataframe(df)
elif selected_query == "19. Difference between maximum and minimum debt for each country":
    st.dataframe(df)
elif selected_query == "20. Create a view for the top 10 countries with highest debt":
    if df.empty:
        st.success("View `project2.top_10_countries_debt` created or already exists.")
    else:
        st.dataframe(df)
elif selected_query == "21. Categorize countries into High/Medium/Low Debt":
    st.dataframe(df)
elif selected_query == "22. Calculate cumulative debt per country with window functions":
    st.dataframe(df)
elif selected_query == "23. Indicators where average debt is higher than overall average debt":
    st.dataframe(df)
elif selected_query == "24. Countries contributing more than 5% of global debt":
    st.dataframe(df)
elif selected_query == "25. Most dominant indicator for each country":
    st.dataframe(df)
elif selected_query == "26. Find the total debt for each country":
    st.dataframe(df)
elif selected_query == "27. Display the top 10 countries with the highest total debt":
    st.dataframe(df)
elif selected_query == "28. Find the average debt per country":
    st.dataframe(df)
elif selected_query == "29. Calculate total debt for each indicator":
    st.dataframe(df)
elif selected_query == "30. Identify the indicator contributing the highest total debt":
    st.dataframe(df)
