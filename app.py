"""
Streamlit web application for visualizing taxi data analysis.

This application loads taxi trip data, performs analyses, and displays results
including:
- Data summaries and information for three datasets.
- Bar plots of top taxi companies and top neighborhoods by drop-offs.
- Results of a hypothesis test (Levene and t-test) comparing trip durations
  on rainy vs. non-rainy Saturdays, along with a box plot.
- General conclusions derived from the original data analysis notebook.

The analysis functions are imported from `main_analysis.py`.
To run this application: `streamlit run app.py`
"""
import streamlit as st
import pandas as pd
from io import StringIO # Used for capturing pandas DataFrame.info() output

# Import functions from the main analysis script
import main_analysis

# Static text for the conclusions section, based on the original notebook
CONCLUSIONS_TEXT = """
## Conclusions

### 1. Top Taxi Companies and Neighborhoods:
- **Top Taxi Companies**: The analysis identified the leading taxi companies based on the number of trips. 
  Companies like 'Flash Cab', 'Taxi Affiliation Services', 'Medallion Leasing', etc., 
  were among the most frequent, indicating a significant market share.
- **Top Neighborhoods**: 'Loop', 'River North', 'Streeterville', 'West Loop', and 'O'Hare' 
  were the top 5 neighborhoods by the average number of drop-offs. This suggests high taxi 
  demand in these areas, likely due to business, entertainment, and transportation hubs.

### 2. Hypothesis Test: Trip Duration on Rainy vs. Non-Rainy Saturdays:
- **Levene Test for Variance Equality**: The Levene test was performed to check if the 
  variances of trip durations on rainy and non-rainy Saturdays were equal.
  - If Levene p-value < 0.05: Variances are considered unequal.
  - If Levene p-value >= 0.05: Variances are considered equal.
- **T-test for Mean Trip Duration**:
  - **Null Hypothesis (H0)**: The average trip duration on rainy Saturdays is the same as on non-rainy Saturdays.
  - **Alternative Hypothesis (H1)**: The average trip duration on rainy Saturdays is different from non-rainy Saturdays.
  - **Outcome**: Based on the t-statistic and p-value from the t-test (Welch's t-test if variances 
    were unequal, standard t-test if variances were equal):
    - If t-test p-value < 0.05: We reject H0 and conclude that there is a statistically 
      significant difference in average trip durations.
    - If t-test p-value >= 0.05: We fail to reject H0 and conclude that there is no 
      statistically significant difference.
- **Notebook Finding**: The original notebook found that the average duration of rides from 
  the Loop to O'Hare International Airport changes on rainy Saturdays. This application 
  allows for a re-evaluation with potentially different or updated data. The t-test results 
  (p-value) will determine if this difference is statistically significant for the loaded dataset.
"""

def display_df_info(df: pd.DataFrame, df_name: str):
    """
    Displays the `df.info()` output for a given DataFrame in Streamlit.

    Args:
        df (pd.DataFrame): The DataFrame to get information from.
        df_name (str): The name of the DataFrame, used in the subheader.
    """
    st.subheader(f"Data Information for {df_name}")
    # Capture df.info() output into a string buffer
    buffer = StringIO()
    df.info(buf=buffer)
    s = buffer.getvalue()
    # Display the captured info using st.text
    st.text(s)

def main():
    """
    Main function to run the Streamlit application.
    Sets up the UI, loads data, performs analyses, and displays results.
    """
    st.set_page_config(layout="wide") # Use wide layout for better content display
    st.title("Taxi Data Analysis Dashboard")

    # --- Data Loading Section ---
    # Load data using the function from main_analysis.py
    # This assumes CSV files are in the same directory or path is correctly handled.
    # Future enhancement could include st.file_uploader for dynamic file input.
    df, df0, df1 = main_analysis.load_data()

    # --- Data Summaries Section ---
    st.header("I. Data Summaries & Information")
    
    # Display summary for the first dataset (Taxi Company Trips)
    if df is not None:
        st.subheader("1.1 Taxi Company Trips Data (Source: SQL Result 01)")
        st.dataframe(df.head()) # Show the first few rows
        st.write("Descriptive Statistics:", df.describe()) # Show basic stats
        display_df_info(df, "Taxi Company Trips Data") # Show df.info()
    else:
        st.error("Failed to load Taxi Company Trips Data ('moved_project_sql_result_01.csv'). Please check file availability.")

    # Display summary for the second dataset (Neighborhood Dropoffs)
    if df0 is not None:
        st.subheader("1.2 Neighborhood Dropoffs Data (Source: SQL Result 04)")
        st.dataframe(df0.head())
        st.write("Descriptive Statistics:", df0.describe())
        display_df_info(df0, "Neighborhood Dropoffs Data")
    else:
        st.error("Failed to load Neighborhood Dropoffs Data ('moved_project_sql_result_04.csv'). Please check file availability.")

    # Display summary for the third dataset (Loop to O'Hare Trips)
    if df1 is not None:
        st.subheader("1.3 Loop to O'Hare Trip Data (Source: SQL Result 07)")
        st.dataframe(df1.head())
        st.write("Descriptive Statistics:", df1.describe())
        display_df_info(df1, "Loop to O'Hare Trip Data")
    else:
        st.error("Failed to load Loop to O'Hare Trip Data ('moved_project_sql_result_07.csv'). Please check file availability.")

    # --- Data Analyses Section ---
    st.header("II. Data Analyses & Visualizations")

    # Analysis 1: Top Companies and Neighborhoods
    st.subheader("2.1 Top Taxi Companies and Drop-off Neighborhoods")
    if df is not None and df0 is not None:
        # Call analysis function to get figure objects
        fig_companies, fig_neighborhoods = main_analysis.analyze_top_companies_and_neighborhoods(df, df0)
        
        if fig_companies:
            st.pyplot(fig_companies) # Display the companies bar plot
        else:
            st.warning("Could not generate the top companies plot.")
        
        if fig_neighborhoods:
            st.pyplot(fig_neighborhoods) # Display the neighborhoods bar plot
        else:
            st.warning("Could not generate the top neighborhoods plot.")
    else:
        st.warning("Skipping Top Companies and Neighborhoods analysis due to missing data from SQL Result 01 or 04.")

    # Analysis 2: Trip Duration Hypothesis Test
    st.subheader("2.2 Trip Duration Hypothesis Test: Rainy vs. Non-Rainy Saturdays")
    if df1 is not None:
        # Call analysis function to get statistical results and figure
        results = main_analysis.analyze_trip_duration_hypothesis(df1)
        
        if results and all(r is not None for r in results):
            levene_stat, levene_p, t_stat, p_value, fig_boxplot = results
            
            st.markdown("Investigating if average trip duration differs on rainy vs. non-rainy Saturdays.")
            
            # Display Levene test results using columns for layout
            st.markdown("**Levene Test for Homogeneity of Variances:**")
            col1, col2 = st.columns(2)
            col1.metric("Levene Statistic", f"{levene_stat:.4f}")
            col2.metric("Levene P-value", f"{levene_p:.4f}")
            if levene_p < 0.05:
                st.caption("Levene test p-value < 0.05: Variances are likely unequal. Welch's t-test is appropriate.")
            else:
                st.caption("Levene test p-value >= 0.05: Variances are likely equal. Student's t-test is appropriate.")

            # Display T-test results
            st.markdown("**T-test for Equality of Means:**")
            col3, col4 = st.columns(2)
            col3.metric("T-test Statistic", f"{t_stat:.4f}")
            col4.metric("T-test P-value", f"{p_value:.4f}")

            # Interpret T-test result
            alpha = 0.05 # Significance level
            if p_value < alpha:
                st.success(f"**Conclusion**: Since the t-test p-value ({p_value:.4f}) is less than {alpha}, "
                           "we **reject the null hypothesis**. There is a statistically significant "
                           "difference in average trip durations between rainy and non-rainy Saturdays.")
            else:
                st.info(f"**Conclusion**: Since the t-test p-value ({p_value:.4f}) is greater than or "
                        f"equal to {alpha}, we **fail to reject the null hypothesis**. There is no "
                        "statistically significant difference in average trip durations between "
                        "rainy and non-rainy Saturdays.")

            if fig_boxplot:
                st.pyplot(fig_boxplot) # Display the box plot
            else:
                st.warning("Could not generate the trip duration boxplot.")
        else:
            # This message appears if analysis function returned None (e.g. not enough data)
            st.warning("Could not perform trip duration hypothesis test. This might be due to insufficient data "
                       "after filtering (e.g., no rainy Saturdays or too few samples in one group).")
    else:
        st.warning("Skipping Trip Duration Hypothesis Test analysis due to missing data from SQL Result 07.")

    # --- Overall Conclusions Section ---
    st.header("III. Overall Conclusions from Notebook")
    # Display the static conclusions text
    st.markdown(CONCLUSIONS_TEXT)
    
    # --- Footer or Testing Instructions (as a comment for the report) ---
    # To manually test this Streamlit application:
    # 1. Ensure `main_analysis.py` is in the same directory.
    # 2. Ensure the required CSV files ('moved_project_sql_result_01.csv', 
    #    'moved_project_sql_result_04.csv', 'moved_project_sql_result_07.csv') 
    #    are present in the same directory.
    # 3. Run the command `streamlit run app.py` in your terminal.
    # 4. Verify that all sections (Data Summaries, Analyses, Conclusions) load correctly.
    # 5. Check that plots are displayed and statistical results are shown.
    # 6. Test with missing files to observe error messages.

if __name__ == "__main__":
    main()
