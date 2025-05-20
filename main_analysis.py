"""
Main data analysis script for taxi trip data.

This script performs several analyses:
1. Loads data from three CSV files.
2. Analyzes top taxi companies by trip volume.
3. Analyzes top neighborhoods by drop-off volume.
4. Performs a hypothesis test on trip durations on rainy vs. non-rainy Saturdays.

The functions in this script are designed to be callable by other scripts,
such as a Streamlit web application, and return figures or statistical results.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def load_data():
    """
    Loads the three specified CSV files into pandas DataFrames.

    The files are:
    - 'moved_project_sql_result_01.csv': Taxi company trips data.
    - 'moved_project_sql_result_04.csv': Neighborhood dropoffs data.
    - 'moved_project_sql_result_07.csv': Loop to O'Hare trip data, with 'start_ts' parsed as datetime.
    
    Returns:
        tuple: A tuple containing three pandas DataFrames (df, df0, df1).
               Each element can be None if the corresponding file is not found.
    """
    df, df0, df1 = None, None, None
    try:
        df = pd.read_csv('moved_project_sql_result_01.csv')
    except FileNotFoundError:
        print("Error: 'moved_project_sql_result_01.csv' not found.")
    
    try:
        df0 = pd.read_csv('moved_project_sql_result_04.csv')
    except FileNotFoundError:
        print("Error: 'moved_project_sql_result_04.csv' not found.")
        
    try:
        # Parse 'start_ts' as datetime objects during loading for df1
        df1 = pd.read_csv('moved_project_sql_result_07.csv', parse_dates=['start_ts'])
    except FileNotFoundError:
        print("Error: 'moved_project_sql_result_07.csv' not found.")
        
    return df, df0, df1

def analyze_top_companies_and_neighborhoods(df, df0):
    """
    Analyzes top taxi companies and top neighborhoods, generating bar plots.

    Args:
        df (pd.DataFrame): DataFrame containing taxi company trip data 
                           (e.g., from 'moved_project_sql_result_01.csv').
                           Expected columns: 'company_name', 'trips_amount'.
        df0 (pd.DataFrame): DataFrame containing neighborhood dropoff data
                            (e.g., from 'moved_project_sql_result_04.csv').
                            Expected columns: 'dropoff_location_name', 'average_trips'.

    Returns:
        tuple: A tuple containing two matplotlib Figure objects:
               (fig_companies, fig_neighborhoods).
               `fig_companies` is the bar plot of top 10 taxi companies.
               `fig_neighborhoods` is the bar plot of top 10 neighborhoods.
               Figures are closed after creation to prevent direct display.
    """
    # Analysis 1: Top 10 Taxi Companies by Number of Trips
    top_companies = df.sort_values(by='trips_amount', ascending=False).head(10)
    plt.figure(figsize=(10, 6)) # New figure for this plot
    plt.bar(top_companies['company_name'], top_companies['trips_amount'])
    plt.xlabel("Company Name")
    plt.ylabel("Number of Trips")
    plt.title("Top 10 Taxi Companies by Number of Trips")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    fig_companies = plt.gcf() # Get current figure
    # plt.show() # Removed for Streamlit

    # Top 10 Neighborhoods
    top_neighborhoods = df0.sort_values(by='average_trips', ascending=False).head(10)
    plt.figure(figsize=(10, 6)) # Create a new figure
    plt.bar(top_neighborhoods['dropoff_location_name'], top_neighborhoods['average_trips'])
    plt.xlabel("Neighborhood")
    plt.ylabel("Average Number of Finalizations")
    plt.title("Top 10 Neighborhoods by Average Number of Finalizations")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    fig_neighborhoods = plt.gcf() # Get current figure
    # plt.show() # Removed for Streamlit
    
    plt.close(fig_companies) # Close to prevent display in main script if not intended
    plt.close(fig_neighborhoods) # Close to prevent display in main script if not intended

    return fig_companies, fig_neighborhoods

def analyze_trip_duration_hypothesis(df1):
    """Performs hypothesis test for trip duration on rainy vs. non-rainy Saturdays."""
    # Ensure df1 is a copy if it's a slice from a larger DataFrame (not strictly necessary here as it's a parameter)
    # df1 = df1.copy() 

    # Extract day of the week and filter for Saturdays
    # Use .loc to avoid SettingWithCopyWarning when adding 'day_of_week'
    df1_copy = df1.copy()
    df1_copy.loc[:, 'day_of_week'] = df1_copy['start_ts'].dt.day_name()
    saturdays_df = df1_copy[df1_copy['day_of_week'] == 'Saturday'].copy() # Use .copy() to ensure it's a new DataFrame

    # Create 'is_rainy' column using .loc
    saturdays_df.loc[:, 'is_rainy'] = saturdays_df['weather_conditions'].str.contains('Bad', case=False, na=False)

    # Separate rainy and non-rainy Saturdays, ensuring they are copies
    rainy_saturdays = saturdays_df[saturdays_df['is_rainy'] == True].copy()
    non_rainy_saturdays = saturdays_df[saturdays_df['is_rainy'] == False].copy()

    # Add 'weather_type' for plotting (optional, but good practice if used for sns.boxplot hue)
    rainy_saturdays.loc[:, 'weather_type'] = 'Rainy'
    non_rainy_saturdays.loc[:, 'weather_type'] = 'Non-Rainy'
    
    # Combine back for easier boxplot if using 'weather_type' (or use original saturdays_df and 'weather_conditions')
    # For this specific boxplot, the original 'weather_conditions' column in saturdays_df is sufficient.
    # If we wanted a hue based on 'weather_type', we might concat:
    # plot_df = pd.concat([rainy_saturdays, non_rainy_saturdays])


    # Check if there's enough data for the test
    if rainy_saturdays.empty or non_rainy_saturdays.empty:
        print("Not enough data for one or both conditions (rainy/non-rainy Saturdays) to perform the hypothesis test.")
        return None, None, None, None, None # Return None for all expected values
    if len(rainy_saturdays['duration_seconds']) < 2 or len(non_rainy_saturdays['duration_seconds']) < 2:
        print("Not enough data points in one or both groups for statistical tests.")
        return None, None, None, None, None # Return None for all expected values

    # Perform Levene test for homogeneity of variances
    levene_stat, levene_p = stats.levene(
        rainy_saturdays['duration_seconds'],
        non_rainy_saturdays['duration_seconds']
    )
    print(f"Levene Test Statistic: {levene_stat}, P-value: {levene_p}")

    # Determine equal_var based on Levene test result
    alpha = 0.05
    if levene_p < alpha:
        print("Levene test indicates unequal variances.")
        equal_var_flag = False
    else:
        print("Levene test indicates equal variances.")
        equal_var_flag = True

    # Perform t-test
    t_stat, p_value = stats.ttest_ind(
        rainy_saturdays['duration_seconds'], 
        non_rainy_saturdays['duration_seconds'], 
        equal_var=equal_var_flag 
    )

    print(f"T-statistic: {t_stat}")
    print(f"P-value: {p_value}")

    # Generate box plot
    plt.figure(figsize=(8, 6))
    # Using 'weather_conditions' directly from saturdays_df as it already distinguishes 'Good' and 'Bad'
    sns.boxplot(x='weather_conditions', y='duration_seconds', data=saturdays_df) 
    plt.title('Trip Duration on Rainy vs. Non-Rainy Saturdays')
    plt.xlabel('Weather Conditions (Good vs. Bad)')
    plt.ylabel('Trip Duration (seconds)')
    fig_boxplot = plt.gcf()
    # plt.show() # Removed for Streamlit
    plt.close(fig_boxplot) # Close to prevent display in main script if not intended
    
    return levene_stat, levene_p, t_stat, p_value, fig_boxplot

if __name__ == "__main__":
    # Load data
    df, df0, df1 = load_data()

    # Analyze top companies and neighborhoods
    if df is not None and df0 is not None:
        fig_companies, fig_neighborhoods = analyze_top_companies_and_neighborhoods(df, df0)
        if fig_companies and fig_neighborhoods: # Check if figures were created
            # In a script context, you might want to show them:
            # fig_companies.show() # Or plt.show() if you manage active figures carefully
            # fig_neighborhoods.show()
            print("Company and neighborhood plots generated.") 
            # To actually display, you'd need plt.figure(fig_companies.number) then plt.show()
            # or pass them around to a display manager. For simplicity, we'll just confirm generation.
    else:
        print("Skipping analysis of top companies and neighborhoods due to missing data.")

    # Analyze trip duration hypothesis
    if df1 is not None:
        results = analyze_trip_duration_hypothesis(df1)
        if results and all(r is not None for r in results): # Check if results and all its items are not None
            levene_stat, levene_p, t_stat, p_value, fig_boxplot = results
            print(f"Levene: stat={levene_stat}, p={levene_p}")
            print(f"T-test: stat={t_stat}, p={p_value}")
            # fig_boxplot.show() # Similar to above, for script context
            print("Trip duration hypothesis plot generated.")
    else:
        print("Skipping trip duration hypothesis analysis due to missing data.")
    print("Script execution finished.")
