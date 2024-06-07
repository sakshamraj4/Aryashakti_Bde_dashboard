import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta

# Set page configuration
st.set_page_config(page_title="ARYA SHAKTI", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for styling
st.markdown("""
    <style>
    .st-metric {
        background-color: #f5f5f5;
        border-radius: 5px;
        padding: 20px;
        margin: 10px;
    }
    .stSelectbox, .stRadio, .stDateInput {
        margin: 10px;
    }
    .stDataFrame {
        background-color: #ffffff;
        border-radius: 5px;
        padding: 20px;
        margin: 10px;
    }
    .dashboard-header {
        background-color: #007bff;
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Load CSV data
@st.cache_data
def load_data(filename):
    df = pd.read_csv(filename)
    # Convert 'Activity Date' column to datetime if it's not already
    if 'Activity Date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['Activity Date']):
        df['Activity Date'] = pd.to_datetime(df['Activity Date'])
    return df

# Function to get data for selected date range
# Function to get data for selected date range
def filter_date_range(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    return df[(df['Activity Date'] >= start_date) & (df['Activity Date'] <= end_date)]


# Function to calculate summary statistics
def calculate_summary(df):
    today = pd.to_datetime("today")
    last_month = today - pd.DateOffset(months=1)
    last_last_month = today - pd.DateOffset(months=2)
    last_week = today - pd.DateOffset(weeks=1)
    last_last_week = today - pd.DateOffset(weeks=2)
    last_day = today - pd.DateOffset(days=1)
    last_last_day = today - pd.DateOffset(days=2)

    summary = {
        "Current Month": df[df['Activity Date'].dt.to_period('M') == today.to_period('M')].shape[0],
        "Last Month": df[df['Activity Date'].dt.to_period('M') == last_month.to_period('M')].shape[0],
        "Last-to-Last Month": df[df['Activity Date'].dt.to_period('M') == last_last_month.to_period('M')].shape[0],
        "Current Week": df[df['Activity Date'].dt.to_period('W') == today.to_period('W')].shape[0],
        "Last Week": df[df['Activity Date'].dt.to_period('W') == last_week.to_period('W')].shape[0],
        "Last-to-Last Week": df[df['Activity Date'].dt.to_period('W') == last_last_week.to_period('W')].shape[0],
        "Current Day": df[df['Activity Date'].dt.date == today.date()].shape[0],
        "Last Day": df[df['Activity Date'].dt.date == last_day.date()].shape[0],
        "Last-to-Last Day": df[df['Activity Date'].dt.date == last_last_day.date()].shape[0]
    }
    
    best_month_period = df.groupby(df['Activity Date'].dt.to_period('M')).size().idxmax()
    best_month_count = df[df['Activity Date'].dt.to_period('M') == best_month_period].shape[0]
    best_month = f"{best_month_period.strftime('%B %Y')} ({best_month_count} meetings)"
    
    best_week_period = df.groupby(df['Activity Date'].dt.to_period('W')).size().idxmax()
    best_week_count = df[df['Activity Date'].dt.to_period('W') == best_week_period].shape[0]
    best_week = f"Week {best_week_period.week} ({best_week_count} meetings)"
    
    best_day_date = df.groupby(df['Activity Date'].dt.date).size().idxmax()
    best_day_count = df[df['Activity Date'].dt.date == best_day_date].shape[0]
    best_day = f"{best_day_date.strftime('%Y-%m-%d')} ({best_day_count} meetings)"
    
    best_bde = df['BDE Name'].mode()[0]
    best_bde_count = df[df['BDE Name'] == best_bde].shape[0]
    best_bde_info = f"{best_bde} ({best_bde_count} meetings)"

    comparison = {
        "Best Month": best_month,
        "Best Week": best_week,
        "Best Day": best_day,
        "Best BDE": best_bde_info
    }

    return summary, comparison

# Main function to run the app
def main():
    # Page title and description
    st.title('ARYASHAKTI')
    st.markdown('<div class="dashboard-header"><h2>BD SUBTASK DASHBOARD - ARYASHAKTI.</h2></div>', unsafe_allow_html=True)

    # Load the data
    filename = 'https://raw.githubusercontent.com/sakshamraj4/Aryashakti_Bde_dashboard/main/bd.csv'
    df = load_data(filename)

    # Sidebar options
    dashboard_options = ['Summary', 'Filter Data', 'BDE level Dashboard', 'FPO level Dashboard', 'Activity level Dashboard']
    selected_dashboard = st.sidebar.radio("Select Dashboard", dashboard_options)

    if selected_dashboard == 'Summary':
        # Calculate summary statistics
        summary, comparison = calculate_summary(df)

        # Display summary statistics
        st.subheader('Summary')
        
        # Display metrics in a visually appealing layout
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Month", summary['Current Month'])
        col2.metric("Last Month", summary['Last Month'])
        col3.metric("Last-to-Last Month", summary['Last-to-Last Month'])

        col4, col5, col6 = st.columns(3)
        col4.metric("Current Week", summary['Current Week'])
        col5.metric("Last Week", summary['Last Week'])
        col6.metric("Last-to-Last Week", summary['Last-to-Last Week'])

        col7, col8, col9 = st.columns(3)
        col7.metric("Current Day", summary['Current Day'])
        col8.metric("Last Day", summary['Last Day'])
        col9.metric("Last-to-Last Day", summary['Last-to-Last Day'])

        # Display best periods
        st.subheader('Best Periods')
        col10, col11, col12 = st.columns(3)
        col10.metric("Best Month", comparison['Best Month'])
        col11.metric("Best Week", comparison['Best Week'])
        col12.metric("Best Day", comparison['Best Day'])

        st.metric("Best BDE", comparison['Best BDE'])


    elif selected_dashboard == 'Filter Data':
        # Filter data by date, date range, or month and compare
        st.subheader('Filter Data')
        filter_type = st.radio('Filter Data By:', ('Date', 'Date Range', 'Month'))

        if filter_type == 'Date':
            selected_date = st.date_input('Select Date:')
            filtered_data = df[df['Activity Date'].dt.date == selected_date]
            compare_date = st.date_input('Compare with Date:')
            compare_data = df[df['Activity Date'].dt.date == compare_date]
        elif filter_type == 'Date Range':
            start_date = st.date_input('Select Start Date:')
            end_date = st.date_input('Select End Date:')
            filtered_data = filter_date_range(df, start_date, end_date)
            compare_start_date = st.date_input('Compare with Start Date:')
            compare_end_date = st.date_input('Compare with End Date:')
            compare_data = filter_date_range(df, compare_start_date, compare_end_date)
        else:
            selected_month = st.selectbox('Select Month:', sorted(df['Activity Date'].dt.month.unique()))
            filtered_data = df[df['Activity Date'].dt.month == selected_month]
            compare_month = st.selectbox('Compare with Month:', sorted(df['Activity Date'].dt.month.unique()))
            compare_data = df[df['Activity Date'].dt.month == compare_month]

        # Display filtered data
        st.subheader('Filtered Data')
        st.write(filtered_data)

        # Display comparison data
        st.subheader('Comparison Data')
        st.write(compare_data)

        # Visualizations based on user selection
        if filtered_data is not None and not filtered_data.empty:
            selected_columns = st.multiselect('Select Columns for Visualization:', filtered_data.columns)

            if selected_columns:
                st.subheader('Visualizations')
                for column in selected_columns:
                    # Histogram for numerical columns
                    if filtered_data[column].dtype != 'object':
                        fig, ax = plt.subplots()
                        sns.histplot(filtered_data[column], ax=ax)
                        ax.set_title(f'Histogram of {column}')
                        st.pyplot(fig)
                    # Bar chart for categorical columns
                    else:
                        fig, ax = plt.subplots()
                        sns.countplot(data=filtered_data, x=column, ax=ax)
                        ax.set_title(f'Count of {column}')
                        plt.xticks(rotation=45)
                        st.pyplot(fig)

        # Pie chart to show the number of meetings when comparing two date ranges, dates, or months
        if compare_data is not None and not compare_data.empty:
            if filter_type == 'Date' or filter_type == 'Date Range' or filter_type == 'Month':
                st.subheader('Comparison Pie Chart')
                fig, ax = plt.subplots()
                compare_data_count = compare_data.shape[0]
                labels = ['Filtered Data', 'Comparison Data']
                sizes = [filtered_data.shape[0], compare_data_count]
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                st.pyplot(fig)


    elif selected_dashboard == 'BDE level Dashboard':
        st.subheader('BDE Name Dashboard')
        selected_bde = st.selectbox('Select BDE Name:', df['BDE Name'].unique())
        bde_data = df[df['BDE Name'] == selected_bde]

        # Filter data by date, date range, or month
        filter_type_bde = st.radio('Filter Data By:', ('Date', 'Date Range', 'Month', 'All Dates'))

        if filter_type_bde == 'Date':
            selected_date_bde = st.date_input('Select Date:')
            bde_data_filtered = bde_data[bde_data['Activity Date'].dt.date == selected_date_bde]
        elif filter_type_bde == 'Date Range':
            start_date_bde = st.date_input('Select Start Date:')
            end_date_bde = st.date_input('Select End Date:')
            bde_data_filtered = filter_date_range(bde_data, start_date_bde, end_date_bde)
        elif filter_type_bde == 'Month':
            selected_month_bde = st.selectbox('Select Month:', sorted(bde_data['Activity Date'].dt.month.unique()))
            bde_data_filtered = bde_data[bde_data['Activity Date'].dt.month == selected_month_bde]
        else:
            bde_data_filtered = bde_data

        # Display BDE data
        st.subheader(f'Data for {selected_bde}')
        st.write(bde_data_filtered)

        # Visualizations for selected BDE
        selected_columns_bde = st.multiselect('Select Columns for Visualization:', bde_data_filtered.columns)

        if selected_columns_bde:
            st.subheader('BDE Visualizations')
            for column in selected_columns_bde:
                # Histogram for numerical columns
                if bde_data_filtered[column].dtype != 'object':
                    fig, ax = plt.subplots()
                    sns.histplot(bde_data_filtered[column], ax=ax)
                    ax.set_title(f'Histogram of {column} for {selected_bde}')
                    st.pyplot(fig)
                # Bar chart for categorical columns
                else:
                    fig, ax = plt.subplots()
                    sns.countplot(data=bde_data_filtered, x=column, ax=ax)
                    ax.set_title(f'Count of {column} for {selected_bde}')
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
                    
    elif selected_dashboard == 'FPO level Dashboard':
        st.subheader('FPO Name Dashboard')
        selected_fpo = st.selectbox('Select FPO Name:', df['FPO NAME'].unique())
        fpo_data = df[df['FPO NAME'] == selected_fpo]

        # Filter data by date, date range, or month
        filter_type_fpo = st.radio('Filter Data By:', ('Date', 'Date Range', 'Month', 'All Dates'))

        if filter_type_fpo == 'Date':
            selected_date_fpo = st.date_input('Select Date:')
            fpo_data_filtered = fpo_data[fpo_data['Activity Date'].dt.date == selected_date_fpo]
        elif filter_type_fpo == 'Date Range':
            start_date_fpo = st.date_input('Select Start Date:')
            end_date_fpo = st.date_input('Select End Date:')
            fpo_data_filtered = filter_date_range(fpo_data, start_date_fpo, end_date_fpo)
        elif filter_type_fpo == 'Month':
            selected_month_fpo = st.selectbox('Select Month:', sorted(fpo_data['Activity Date'].dt.month.unique()))
            fpo_data_filtered = fpo_data[fpo_data['Activity Date'].dt.month == selected_month_fpo]
        else:
            fpo_data_filtered = fpo_data

        # Display FPO data
        st.subheader(f'Data for {selected_fpo}')
        st.write(fpo_data_filtered)

        # Visualizations for selected FPO
        selected_columns_fpo = st.multiselect('Select Columns for Visualization:', fpo_data_filtered.columns)

        if selected_columns_fpo:
            st.subheader('FPO Visualizations')
            for column in selected_columns_fpo:
                # Histogram for numerical columns
                if fpo_data_filtered[column].dtype != 'object':
                    fig, ax = plt.subplots()
                    sns.histplot(fpo_data_filtered[column], ax=ax)
                    ax.set_title(f'Histogram of {column} for {selected_fpo}')
                    st.pyplot(fig)
                # Bar chart for categorical columns
                else:
                    fig, ax = plt.subplots()
                    sns.countplot(data=fpo_data_filtered, x=column, ax=ax)
                    ax.set_title(f'Count of {column} for {selected_fpo}')
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
                    
    elif selected_dashboard == 'Activity level Dashboard':
        st.subheader('Title of Activity Dashboard')
        selected_title = st.selectbox('Select Title of Activity:', df['Title of Activity'].unique())
        title_data = df[df['Title of Activity'] == selected_title]

        # Filter data by date, date range, or month
        filter_type_title = st.radio('Filter Data By:', ('Date', 'Date Range', 'Month', 'All Dates'))

        if filter_type_title == 'Date':
            selected_date_title = st.date_input('Select Date:')
            title_data_filtered = title_data[title_data['Activity Date'].dt.date == selected_date_title]
        elif filter_type_title == 'Date Range':
            start_date_title = st.date_input('Select Start Date:')
            end_date_title = st.date_input('Select End Date:')
            title_data_filtered = filter_date_range(title_data, start_date_title, end_date_title)
        elif filter_type_title == 'Month':
            selected_month_title = st.selectbox('Select Month:', sorted(title_data['Activity Date'].dt.month.unique()))
            title_data_filtered = title_data[title_data['Activity Date'].dt.month == selected_month_title]
        else:
            title_data_filtered = title_data

        # Display Title of Activity data
        st.subheader(f'Data for "{selected_title}"')
        st.write(title_data_filtered)

        # Visualizations for selected Title of Activity
        selected_columns_title = st.multiselect('Select Columns for Visualization:', title_data_filtered.columns)

        if selected_columns_title:
            st.subheader('Title of Activity Visualizations')
            for column in selected_columns_title:
                # Histogram for numerical columns
                if title_data_filtered[column].dtype != 'object':
                    fig, ax = plt.subplots()
                    sns.histplot(title_data_filtered[column], ax=ax)
                    ax.set_title(f'Histogram of {column} for "{selected_title}"')
                    st.pyplot(fig)
                # Bar chart for categorical columns
                else:
                    fig, ax = plt.subplots()
                    sns.countplot(data=title_data_filtered, x=column, ax=ax)
                    ax.set_title(f'Count of {column} for "{selected_title}"')
                    plt.xticks(rotation=45)
                    st.pyplot(fig)




if __name__ == '__main__':
    main()
