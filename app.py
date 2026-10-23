import streamlit as st
import pandas as pd
from pandas.errors import EmptyDataError
import plotly.express as px

REQUIRED_COLUMNS = [
    'Education',
    'JoiningYear',
    'City',
    'PaymentTier',
    'Age',
    'Gender',
    'EverBenched',
    'ExperienceInCurrentDomain',
    'LeaveOrNot'
]

NEW_COLUMN_NAMES = {
    'JoiningYear': 'Joining Year',
    'PaymentTier': 'Payment Tier',
    'EverBenched': 'Benched Status',
    'ExperienceInCurrentDomain': 'Experience in Current Domain',
    'LeaveOrNot': 'Employee Status'
}

CATEGORICAL_COLUMNS = ['Education','City','Payment Tier','Gender','Benched Status','Employee Status']

NUMERICAL_COLUMNS = ['Age','Experience in Current Domain','Joining Year']

COLUMN_DESCRIPTIONS = {
        'Education' : "Highest level of formal education obtained by the employee",
        'Joining Year' : "Year of joining the company",
        'City' : "Job location",
        'Payment Tier' : "Payment tier (1-3). 3 means better pay.",
        'Age' : "Age of the employee",
        'Gender' : "Gender of the employee",
        'Benched Status' : "Was the employee ever benched or not",
        'Experience in Current Domain' : "Work experience in the current domain",
        'Employee Status' : "Whether the employee left the company or not"
    }

st.set_page_config(page_title="Employee Analysis",
                   layout="wide")

st.title("Employee Analysis - EDA")

# ------------------------------------------------------------------------------ functions

def fn_load_data(uploaded_file):
    '''To load data from csv file to dataframe'''
    if not uploaded_file:
        st.info("Upload csv file")
        st.stop()
    try:
        df = pd.read_csv(uploaded_file)
    except EmptyDataError:
        st.error("Uploaded file is empty")
        st.stop()
    except Exception as e:
        st.error(f"{e}")
        st.stop()
    else:
        return df

def fn_validate_data(df):
    '''To validate data and missing columns'''
    if df.empty:
        st.error("No data found")
        st.stop()
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        st.error("Following columns are missing: " + ", ".join(missing_columns))
        st.stop()

def fn_add_description(column,description=None):
    '''To add description for columns'''
    COLUMN_DESCRIPTIONS[column] = description

def fn_data_cleaning(df):
    '''To clean data'''
    clean_employee_df = df.copy()

    # Renaming columns
    clean_employee_df = clean_employee_df.rename(columns=NEW_COLUMN_NAMES)

    # Duplicate records
    duplicate_records_count = clean_employee_df.duplicated().sum()
    duplicate_records_percentage = (duplicate_records_count / len(clean_employee_df) * 100).round(2)
    duplicate_records_details = {'No. of duplicate records':duplicate_records_count,
                                 'Percentage of duplicate records':duplicate_records_percentage,
                                 'Remarks':"Since there are no unique ID columns and duplicate rows can represent different employees, duplicates are not removed."}
    duplicate_records_details = pd.Series(duplicate_records_details)

    # Converting to numeric data type
    for column in NUMERICAL_COLUMNS:
        if column in clean_employee_df.columns:
            clean_employee_df[column] = pd.to_numeric(clean_employee_df[column],
                                                      errors="coerce")

    # Missing values
    missing_values_df = (clean_employee_df.isnull().sum()
                         .rename_axis('Columns')
                         .reset_index(name="No. of missing values"))
    missing_values_df['% of missing values'] = (missing_values_df['No. of missing values']
                                                / len(clean_employee_df) * 100).round(2)
    missing_values_df = missing_values_df.sort_values(by="% of missing values")

    # Updating values in existing columns
    clean_employee_df['Benched Status'] = (clean_employee_df["Benched Status"]
                                           .str
                                           .lower()
                                           .map({"no": "Never benched","yes": "Benched"}))
    clean_employee_df['Employee Status'] = (clean_employee_df['Employee Status']
                                            .map({0: "Active",1: "Resigned"}))
    clean_employee_df['Payment Tier'] = "Tier " + clean_employee_df['Payment Tier'].astype(str)

    # Adding new columns
    clean_employee_df['Age Group'] = pd.cut(clean_employee_df['Age'],
                                            bins=[21,25,30,35,40,50],
                                            labels=["21 - 25","26 - 30","31 - 35","36 - 40","41+"],
                                            include_lowest=True).astype(str)
    fn_add_description('Age Group',"Age groups of the employee based on their age (21-25,26-30,31-35,36-40 and 41+)")

    clean_employee_df['Experience Level'] = pd.cut(clean_employee_df['Experience in Current Domain'],
                                                   bins=[0,1,4,7],
                                                   labels=["Entry (0-1 years)",
                                                           "Intermediate (2-4 years)",
                                                           "Senior (5-7 years)"],
                                                   include_lowest=True).astype(str)
    fn_add_description('Experience Level', "Experience level of employees based on their experience in current domain - Entry(0-1 years), Intermediate (2-4 years), Senior (5-7 years)")

    return clean_employee_df,duplicate_records_details,missing_values_df

def reset_all_filters():
    '''To clear all selections and reset to "All"'''
    for key in select_keys:
        st.session_state[key] = "All"

# ------------------------------------------------------------------------------ side bar

# Uploading csv file
UPLOADED_FILE = st.sidebar.file_uploader("Upload csv file",type="csv")

# Loading data into dataframe
employee_df = fn_load_data(UPLOADED_FILE)

# Validating data
fn_validate_data(employee_df)

# Cleaning data
clean_employee_df,duplicate_records_details,missing_values_df = fn_data_cleaning(employee_df)

# Dashboard selection
page = st.sidebar.radio(
    "Dashboards",
    [
        "Data Overview",
        "Employee Demographics",
        "Workforce Structure",
        "Resignation Analysis",
        "Statistical Analysis",
        "Data Dictionary"
    ]
)

# Values for each selection
city = ["All"] + sorted(clean_employee_df['City'].unique())
payment_tier = ["All"] + sorted(clean_employee_df['Payment Tier'].unique())
gender = ["All"] + sorted(clean_employee_df['Gender'].unique())
age_group = ["All"] + sorted(clean_employee_df['Age Group'].unique())
experience_level = ["All"] + sorted(clean_employee_df['Experience Level'].unique())

# Filters
selected_city = st.sidebar.selectbox(label="City",options=city,key="city_key")
selected_gender = st.sidebar.selectbox(label="Gender",options=gender,key="gender_key")
selected_age_group = st.sidebar.selectbox(label="Age group",options=age_group,key="age_group_key")
selected_experience_level = st.sidebar.selectbox(label="Experience level",options=experience_level,key="experience_level_key")
selected_payment_tier = st.sidebar.selectbox(label="Payment tier",options=payment_tier,key="payment_tier_key")

# Filter keys
select_keys = ["city_key","gender_key","age_group_key","experience_level_key","payment_tier_key"]

# Button to clear all selections
st.sidebar.button("Clear selections",on_click=reset_all_filters)

# ------------------------------------------------------------------------------ filtered data

# Filtering dataframe for selections
filtered_employee_df = clean_employee_df.copy()
if selected_city != "All":
    filtered_employee_df = filtered_employee_df[filtered_employee_df["City"] == selected_city]
if selected_gender != "All":
    filtered_employee_df = filtered_employee_df[filtered_employee_df["Gender"] == selected_gender]
if selected_age_group != "All":
    filtered_employee_df = filtered_employee_df[filtered_employee_df["Age Group"] == selected_age_group]
if selected_experience_level != "All":
    filtered_employee_df = filtered_employee_df[filtered_employee_df["Experience Level"] == selected_experience_level]
if selected_payment_tier != "All":
    filtered_employee_df = filtered_employee_df[filtered_employee_df["Payment Tier"] == selected_payment_tier]

# ------------------------------------------------------------------------------ custom colors

# Colours to depict gender,benching status and employee status
custom_colors_gender = {"Male":"blue","Female":"pink"}
custom_colors_benched_status = {"Benched":"orange","Never benched":"blue"}
custom_colors_employee_status = {"Active":"green","Resigned":"darkred"}

# ------------------------------------------------------------------------------ metrics bar

if page not in ["Data Overview","Statistical Analysis","Data Dictionary"]:

    total_employees = filtered_employee_df.shape[0]
    benched_rate = (((filtered_employee_df['Benched Status'] == "Benched").sum().item()
                    / total_employees)
                    * 100)
    resignation_rate = (((filtered_employee_df['Employee Status'] == "Resigned").sum().item()
                         / total_employees)
                        * 100)
    average_age = filtered_employee_df['Age'].mean()
    average_experience = filtered_employee_df['Experience in Current Domain'].mean()

    col_total,col_resigned,col_benched = st.columns(3,border=True)

    # Metric - total employees
    with col_total:
        st.metric(label="Total employees",value=total_employees)
    # Metric - resignation rate
    with col_resigned:
        st.metric(label="Resignation rate",value=f"{resignation_rate:.0f}%")
    # Metric - benched rate
    with col_benched:
        st.metric(label="Benched rate",value=f"{benched_rate:.0f}%")

# ------------------------------------------------------------------------------ page 1

if page == "Data Overview":
    st.subheader("Data Overview")

# Row and column count comparison of raw and cleaned data
    col_raw,col_cleaned = st.columns(2,border=True,width=2000)
    with col_raw:
        st.write("#### Before cleaning:")
        col_rows,col_columns = st.columns(2,border=True,width=1000)
        with col_rows:
            st.metric(label="No. of rows",value=employee_df.shape[0])
        with col_columns:
            st.metric(label="No. of columns",value=employee_df.shape[1])
    with col_cleaned:
        st.write("#### After cleaning:")
        col_rows,col_columns = st.columns(2,border=True,width=1000)
        with col_rows:
            st.metric(label="No. of rows",value=clean_employee_df.shape[0])
        with col_columns:
            st.metric(label="No. of columns",value=clean_employee_df.shape[1])

# Details of duplicated records
    with st.expander("Duplicates"):
        col_count,col_percentage = st.columns(2,border=True,width=2000)
        with col_count:
            st.metric(label="No. of duplicate records",
                      value=duplicate_records_details["No. of duplicate records"])
        with col_percentage:
            st.metric(label="Percentage of duplicate records",
                      value=f"{duplicate_records_details['Percentage of duplicate records']:.0f}%")
        st.write("### Remarks:")
        st.write(duplicate_records_details["Remarks"])

# Details of missing data
    with st.expander("Missing values"):
        st.dataframe(missing_values_df,hide_index=True)

# Preview of cleaned data
    with st.expander("Cleaned data preview"):
        st.dataframe(clean_employee_df.head(),hide_index=True)

# ------------------------------------------------------------------------------ page 2

elif page == "Employee Demographics":
    st.subheader("Employee Demographics")

    col_education,col_city = st.columns(2,gap=100)

    # Employee distribution by highest formal education
    with col_education:
        employees_by_education_df = (filtered_employee_df['Education']
                                     .value_counts()
                                     .rename_axis("Highest Formal Education")
                                     .reset_index(name="No. of Employees")
                                     .sort_values("No. of Employees",ascending=False))
        fig = px.bar(data_frame=employees_by_education_df,
                     x="Highest Formal Education",
                     y="No. of Employees",
                     title="Employees by highest formal education",
                     text_auto=True,
                     height=390
                     )
        fig.update_traces(textposition="outside",
                          cliponaxis=False,
                          width=0.5)
        fig.update_layout(margin=dict(t=40))
        fig.update_yaxes(showticklabels=False,
                         showgrid=False,
                         title=None)
        fig.update_xaxes(title=None)
        st.plotly_chart(fig)

    # Employee distribution by city
    with col_city:
        employees_by_city_df = (filtered_employee_df['City']
                                .value_counts()
                                .rename_axis("City")
                                .reset_index(name="No. of Employees"))
        fig = px.bar(data_frame=employees_by_city_df,
                     x="City",
                     y="No. of Employees",
                     title="Employees by city",
                     text_auto=True,
                     height=390
                     )
        fig.update_traces(textposition="outside",
                          cliponaxis=False,
                          width=0.5)
        fig.update_layout(margin=dict(t=40))
        fig.update_yaxes(showticklabels=False,
                         showgrid=False,
                         title=None)
        fig.update_xaxes(title=None)
        st.plotly_chart(fig)

    col_gender,col_age_group = st.columns(2,gap=100)

    # Employee distribution by gender
    with col_gender:
        employees_by_gender_df = (filtered_employee_df['Gender']
                                  .value_counts()
                                  .rename_axis("Gender")
                                  .reset_index(name="No. of Employees"))
        fig = px.pie(data_frame=employees_by_gender_df,
                     names="Gender",
                     values="No. of Employees",
                     title="Employees by gender",
                     color="Gender",
                     color_discrete_map=custom_colors_gender,
                     height=390)
        fig.update_traces(textposition="inside",
                          texttemplate="%{label}<br>%{percent:.0%}")
        fig.update_layout(showlegend=False,
                          margin=dict(t=40))
        st.plotly_chart(fig)

    # Employee distribution by age group
    with col_age_group:
        employees_by_age_group_df = (filtered_employee_df['Age Group']
                                     .value_counts()
                                     .rename_axis("Age Group")
                                     .reset_index(name="No. of Employees")
                                     .sort_values(by="Age Group"))
        fig = px.bar(data_frame=employees_by_age_group_df,
                     x="Age Group",
                     y="No. of Employees",
                     title="Employees by age group",
                     text_auto=True,
                     height=390
                     )
        fig.update_traces(textposition="outside",
                          cliponaxis=False,
                          width=0.5)
        fig.update_layout(margin=dict(t=40))
        fig.update_yaxes(showticklabels=False,
                         showgrid=False,
                         title=None)
        fig.update_xaxes(title=None)
        st.plotly_chart(fig)

# ------------------------------------------------------------------------------ page 3

elif page == "Workforce Structure":
    st.subheader("Workforce Structure")

    col_payment_tier,col_experience_level = st.columns(2,gap=100)

    # Employee distribution by payment tier
    with col_payment_tier:
        employees_by_payment_tier_df = (filtered_employee_df['Payment Tier']
                                        .value_counts()
                                        .rename_axis("Payment Tier")
                                        .reset_index(name="No. of Employees")
                                        .sort_values(by="Payment Tier"))
        fig = px.bar(data_frame=employees_by_payment_tier_df,
                     x="Payment Tier",
                     y="No. of Employees",
                     title="Employees by payment tier",
                     text_auto=True,
                     height=390
                     )
        fig.update_traces(textposition="outside",
                          cliponaxis=False,
                          width=0.5)
        fig.update_layout(margin=dict(t=40))
        fig.update_yaxes(showticklabels=False,
                         showgrid=False,
                         title=None)
        fig.update_xaxes(title=None)
        st.plotly_chart(fig)

    # Employee distribution by experience level
    with col_experience_level:
        employees_by_experience_level_df = (filtered_employee_df['Experience Level']
                                            .value_counts()
                                            .rename_axis("Experience Level")
                                            .reset_index(name="No. of Employees")
                                            .sort_values(by="Experience Level"))
        fig = px.bar(data_frame=employees_by_experience_level_df,
                     x="Experience Level",
                     y="No. of Employees",
                     title="Employees by experience level",
                     text_auto=True,
                     height=390
                     )
        fig.update_traces(textposition="outside",
                          cliponaxis=False,
                          width=0.5)
        fig.update_layout(margin=dict(t=40))
        fig.update_yaxes(showticklabels=False,
                         showgrid=False,
                         title=None)
        fig.update_xaxes(title=None)
        st.plotly_chart(fig)

    # Employee distribution by joining year
    employees_by_joining_year_df = (filtered_employee_df['Joining Year']
                                    .value_counts()
                                    .rename_axis("Joining Year")
                                    .reset_index(name="No. of Employees")
                                    .sort_values(by="Joining Year"))
    fig = px.line(data_frame=employees_by_joining_year_df,
                  x="Joining Year",
                  y="No. of Employees",
                  title="Employees by joining year",
                  markers=True,
                  height=300)
    fig.update_layout(margin=dict(t=40))
    fig.update_xaxes(type="category")
    fig.update_yaxes(showgrid=False,
                     title=None,
                     rangemode="tozero")
    st.plotly_chart(fig,width="stretch")

    col_status,col_benching = st.columns(2,gap=100)

    # Employee distribution by employee status
    with col_status:
        employees_by_employee_status_df = (filtered_employee_df['Employee Status']
                                           .value_counts()
                                           .rename_axis("Employee Status")
                                           .reset_index(name="No. of Employees"))
        fig = px.pie(data_frame=employees_by_employee_status_df,
                     names="Employee Status",
                     values="No. of Employees",
                     title="Employees by status",
                     color="Employee Status",
                     color_discrete_map=custom_colors_employee_status,
                     height=390)
        fig.update_traces(textposition="inside",
                          texttemplate="%{label}<br>%{percent:.0%}")
        fig.update_layout(showlegend=False,
                          margin=dict(t=40))
        st.plotly_chart(fig)

    # Employee distribution by benched status
    with col_benching:
        employees_by_benched_status_df = (filtered_employee_df['Benched Status']
                                          .value_counts()
                                          .rename_axis("Benched Status")
                                          .reset_index(name="No. of Employees"))
        fig = px.pie(data_frame=employees_by_benched_status_df,
                     names="Benched Status",
                     values="No. of Employees",
                     title="Employees by benched status",
                     color="Benched Status",
                     color_discrete_map=custom_colors_benched_status,
                     height=390)
        fig.update_traces(textposition="inside",
                          texttemplate="%{label}<br>%{percent:.0%}")
        fig.update_layout(showlegend=False,
                          margin=dict(t=40))
        st.plotly_chart(fig)

# ------------------------------------------------------------------------------ page 4

elif page == "Resignation Analysis":
    st.subheader("Resignation Analysis")

    col_experience_level,col_payment_tier,col_benched_status = st.columns([3,2,2],gap=100)

    # Resignation rate by experience level
    with (col_experience_level):
        resignations_by_experience_level = (pd.crosstab(index=filtered_employee_df['Experience Level'],
                                                        columns=filtered_employee_df['Employee Status'],
                                                        margins=True,
                                                        margins_name="Total")
                                            ).drop(labels="Total").drop(columns="Active").reset_index().sort_index(ascending=True)
        resignations_by_experience_level['Rate'] = (resignations_by_experience_level['Resigned']
                                                    / resignations_by_experience_level['Total']) * 100
        fig = px.bar(data_frame=resignations_by_experience_level,
                     x="Experience Level",
                     y="Rate",
                     title="Resignation rate by experience level",
                     text_auto=True,
                     custom_data=['Resigned','Total'],
                     height=390)
        fig.update_traces(textposition="outside",
                          cliponaxis=False,
                          width=0.5,
                          texttemplate="%{y:.0f}%",
                          hovertemplate=
                          '''<b>%{x}</b>
                          <br>Resignation rate: %{y:.0f}%
                          <br>Resigned: %{customdata[0]}
                          <br>Total employees: %{customdata[1]}
                          <extra></extra>''')
        fig.update_layout(margin=dict(t=40))
        fig.update_yaxes(showticklabels=False,
                         showgrid=False,
                         title=None)
        fig.update_xaxes(title=None)
        st.plotly_chart(fig)

    # Resignation rate by payment tier
    with col_payment_tier:
        resignations_by_payment_tier = (pd.crosstab(index=filtered_employee_df['Payment Tier'],
                                                    columns=filtered_employee_df['Employee Status'],
                                                    margins=True,
                                                    margins_name="Total")
                                        ).drop(labels="Total").drop(columns="Active").reset_index().sort_index(ascending=True)
        resignations_by_payment_tier['Rate'] = (resignations_by_payment_tier['Resigned']
                                                / resignations_by_payment_tier['Total']) * 100
        fig = px.bar(data_frame=resignations_by_payment_tier,
                     x="Payment Tier",
                     y="Rate",
                     title="Resignation rate by payment tier",
                     text_auto=True,
                     custom_data=['Resigned','Total'],
                     height=390)
        fig.update_traces(textposition="outside",
                          cliponaxis=False,
                          width=0.8,
                          texttemplate="%{y:.0f}%",
                          hovertemplate=
                          '''<b>%{x}</b>
                          <br>Resignation rate: %{y:.0f}%
                          <br>Resigned: %{customdata[0]}
                          <br>Total employees: %{customdata[1]}
                          <extra></extra>''')
        fig.update_layout(margin=dict(t=40))
        fig.update_yaxes(showticklabels=False,
                         showgrid=False,
                         title=None)
        fig.update_xaxes(title=None)
        st.plotly_chart(fig)

    # Resignation rate by benched status
    with col_benched_status:
        resignations_by_benched_status = (pd.crosstab(index=filtered_employee_df['Benched Status'],
                                                      columns=filtered_employee_df['Employee Status'],
                                                      margins=True,
                                                      margins_name="Total")
                                          ).drop(labels="Total").drop(columns="Active").reset_index()
        resignations_by_benched_status['Rate'] = (resignations_by_benched_status['Resigned']
                                                  / resignations_by_benched_status['Total']) * 100
        resignations_by_benched_status = resignations_by_benched_status.sort_values(by="Rate",ascending=False)
        fig = px.bar(data_frame=resignations_by_benched_status,
                     x="Benched Status",
                     y="Rate",
                     title="Resignation rate by benched status",
                     text_auto=True,
                     custom_data=['Resigned','Total'],
                     height=390)
        fig.update_traces(textposition="outside",
                          cliponaxis=False,
                          width=0.5,
                          texttemplate="%{y:.0f}%",
                          hovertemplate=
                          '''<b>%{x}</b>
                          <br>Resignation rate: %{y:.0f}%
                          <br>Resigned: %{customdata[0]}
                          <br>Total employees: %{customdata[1]}
                          <extra></extra>''')
        fig.update_layout(margin=dict(t=40))
        fig.update_yaxes(showticklabels=False,
                         showgrid=False,
                         title=None)
        fig.update_xaxes(title=None)
        st.plotly_chart(fig)

    st.divider()

    col_gender,col_city,col_education = st.columns(3,gap=100)

    # Resignation rate by gender
    with col_gender:
        resignations_by_gender = (pd.crosstab(index=filtered_employee_df['Gender'],
                                              columns=filtered_employee_df['Employee Status'],
                                              margins=True,
                                              margins_name="Total")
                                  ).drop(labels="Total").drop(columns="Active").reset_index()
        resignations_by_gender['Rate'] = (resignations_by_gender['Resigned']
                                          / resignations_by_gender['Total']) * 100
        resignations_by_gender = resignations_by_gender.sort_values(by="Rate",ascending=False)
        fig = px.bar(data_frame=resignations_by_gender,
                     x="Gender",
                     y="Rate",
                     title="Resignation rate by gender",
                     text_auto=True,
                     custom_data=['Resigned','Total'],
                     height=390)
        fig.update_traces(textposition="outside",
                          cliponaxis=False,
                          width=0.5,
                          texttemplate="%{y:.0f}%",
                          hovertemplate=
                          '''<b>%{x}</b>
                          <br>Resignation rate: %{y:.0f}%
                          <br>Resigned: %{customdata[0]}
                          <br>Total employees: %{customdata[1]}
                          <extra></extra>''')
        fig.update_layout(margin=dict(t=40))
        fig.update_yaxes(showticklabels=False,
                         showgrid=False,
                         title=None)
        fig.update_xaxes(title=None)
        st.plotly_chart(fig)

    # Resignation rate by city
    with col_city:
        resignations_by_city = (pd.crosstab(index=filtered_employee_df['City'],
                                            columns=filtered_employee_df['Employee Status'],
                                            margins=True,
                                            margins_name="Total")
                                ).drop(labels="Total").drop(columns="Active").reset_index()
        resignations_by_city['Rate'] = (resignations_by_city['Resigned']
                                        / resignations_by_city['Total']) * 100
        resignations_by_city = resignations_by_city.sort_values(by="Rate",ascending=False)
        fig = px.bar(data_frame=resignations_by_city,
                     x="City",
                     y="Rate",
                     title="Resignation rate by city",
                     text_auto=True,
                     custom_data=['Resigned','Total'],
                     height=390)
        fig.update_traces(textposition="outside",
                          cliponaxis=False,
                          width=0.5,
                          texttemplate="%{y:.0f}%",
                          hovertemplate=
                          '''<b>%{x}</b>
                          <br>Resignation rate: %{y:.0f}%
                          <br>Resigned: %{customdata[0]}
                          <br>Total employees: %{customdata[1]}
                          <extra></extra>''')
        fig.update_layout(margin=dict(t=40))
        fig.update_yaxes(showticklabels=False,
                         showgrid=False,
                         title=None)
        fig.update_xaxes(title=None)
        st.plotly_chart(fig)

    # Resignation rate by education
    with col_education:
        resignations_by_education = (pd.crosstab(index=filtered_employee_df['Education'],
                                                 columns=filtered_employee_df['Employee Status'],
                                                 margins=True,
                                                 margins_name="Total")
                                     ).drop(labels="Total").drop(columns="Active").reset_index()
        resignations_by_education['Rate'] = (resignations_by_education['Resigned']
                                             / resignations_by_education['Total']) * 100
        resignations_by_education = resignations_by_education.sort_values(by="Rate",ascending=False)
        fig = px.bar(data_frame=resignations_by_education,
                     x="Education",
                     y="Rate",
                     title="Resignation rate by education",
                     text_auto=True,
                     custom_data=['Resigned','Total'],
                     height=390)
        fig.update_traces(textposition="outside",
                          cliponaxis=False,
                          width=0.5,
                          texttemplate="%{y:.0f}%",
                          hovertemplate=
                          '''<b>%{x}</b>
                          <br>Resignation rate: %{y:.0f}%
                          <br>Resigned: %{customdata[0]}
                          <br>Total employees: %{customdata[1]}
                          <extra></extra>''')
        fig.update_layout(margin=dict(t=40))
        fig.update_yaxes(showticklabels=False,
                         showgrid=False,
                         title=None)
        fig.update_xaxes(title=None)
        st.plotly_chart(fig)

# ------------------------------------------------------------------------------ page 5

elif page == "Statistical Analysis":
    st.subheader("Statistical Analysis")

    average_age = filtered_employee_df['Age'].mean()
    average_experience = filtered_employee_df['Experience in Current Domain'].mean()

    col_avg_age,col_avg_experience = st.columns(2,border=True)
    # Metircs - average age
    with col_avg_age:
        st.metric(label="Average age",value=f"{average_age:.0f}")
    # Metrics - average experience in current domain
    with col_avg_experience:
        st.metric(label="Average experience in current domain",value=f"{average_experience:.0f} years")

    col_age,col_experience = st.columns(2,gap=100)

    # Age distribution
    with col_age:
        fig = px.histogram(data_frame=filtered_employee_df,
                           x='Age',
                           title="Age Distribution",
                           height=390,
                           width=500)
        fig.update_layout(margin=dict(t=40),
                          xaxis=dict(tickmode='linear',
                                     dtick=1))
        fig.update_yaxes(title=None,
                         showgrid=False)
        fig.update_xaxes(title=None)
        fig.update_traces(marker_line_color='lightblue',
                          marker_line_width=1)
        st.plotly_chart(fig,width="stretch")

    # Experience distribution
    with col_experience:
        fig = px.histogram(data_frame=filtered_employee_df,
                           x='Experience in Current Domain',
                           title="Experience Distribution",
                           height=390,
                           width=500)
        fig.update_layout(margin=dict(t=40),
                          xaxis=dict(tickmode='linear',
                                     dtick=1))
        fig.update_yaxes(title=None,
                         showgrid=False)
        fig.update_xaxes(title=None)
        fig.update_traces(marker_line_color='lightblue',
                          marker_line_width=1)
        st.plotly_chart(fig,width="stretch")

# ------------------------------------------------------------------------------ page 6

elif page == "Data Dictionary":
    st.subheader("Data Dictionary")
    columns_df = pd.DataFrame(index=clean_employee_df.columns).reset_index(names="Columns")
    columns_df['Data Type'] = [str(clean_employee_df[column].dtype) for column in columns_df['Columns']]
    columns_df['Desciption'] = [COLUMN_DESCRIPTIONS[column] for column in columns_df['Columns']]
    # st.dataframe(columns_df,hide_index=True,height="content")
    st.table(data=columns_df,width="content")

# ------------------------------------------------------------------------------ complete