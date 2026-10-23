# Employee Analysis - EDA Dashboard

An exploratory data analysis of an employee dataset, with an interactive Streamlit dashboard.

## Dataset

Employee data in csv format, uploaded through the sidebar.

## Required Columns

| Column                    | Description                           |
|---------------------------|---------------------------------------|
| Education                 | Highest formal education              |
| JoiningYear               | Year of joining                       |
| City                      | Job location                          |
| PaymentTier               | Payment tier 1-3 (3 = better pay)     |
| Age                       | Age of the employee                   |
| Gender                    | Gender of the employee                |
| EverBenched               | Whether the employee was ever benched |
| ExperienceInCurrentDomain | Experience in the current domain      |
| LeaveOrNot                | Whether the employee left the company |

## Dashboards

1) Data Overview
2) Employee Demographics
3) Workforce Structure
4) Workforce Structure
5) Resignation Analysis
6) Statistical Analysis
7) Data Dictionary

## Features

- Upload data in csv format
- Validate columns
- Checks for duplicates and missing values
- Dashboard selection
- Filter dashboards based on city, gender, age group, experience level and payment tier
- Clear all applied filters using a single click
- Data dictionary

## How to run

Requires Python *3.14*.

```bash
pip install -r requirements.txt
streamlit run app.py
```

### 1. Create a virtual environment and activate it

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Start Streamlit

```powershell
streamlit run app.py
```

The browser will open the dashboard on local address:

```text
http://localhost:8501
```

### 4. Upload dataset

Upload `Employee_Data.csv` using the sidebar.

## Project structure

```
.
├── app.py              # Streamlit dashboard
├── requirements.txt    # Python dependencies
├── Employee_Data.csv   # Dataset (upload via the sidebar)
└── EDA_Project.ipynb   # EDA notebook
```
