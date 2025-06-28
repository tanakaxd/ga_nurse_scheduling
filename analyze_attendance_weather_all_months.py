import pandas as pd
from scipy.stats import chi2_contingency
from datetime import datetime
import numpy as np
from pathlib import Path

# Define the months to process (202411 to 202506)
months = [
    '202411', '202412', '202501', '202502', '202503', 
    '202504', '202505', '202506'
]

# Initialize an empty list to store shift data
shift_dfs = []

# Load and process each shift table
base_path = "/home/ttnk0/projects/ga_nurse_scheduling/data/OB/岡田眼科{YYYYMM}シフト表 - シート1.csv"
for month in months:
    file_path = base_path.format(YYYYMM=month)
    if Path(file_path).exists():
        # Load shift table with utf-8 encoding
        df = pd.read_csv(file_path, encoding='utf-8')
        # Assign dates starting from the first day of the month
        start_date = datetime.strptime(month, '%Y%m').date()
        df['Date'] = pd.date_range(start=start_date, periods=len(df), freq='D')
        df['Day_of_week'] = df['曜日']
        # Determine attendance: 1 for present (not "休"), 0 for absent ("休")
        df['Oba_Attendance'] = df['大場'].apply(lambda x: 0 if x == '休' else 1)
        shift_dfs.append(df[['Date', 'Day_of_week', 'Oba_Attendance']])
    else:
        print(f"Warning: File {file_path} not found. Skipping.")

# Concatenate all shift data
if shift_dfs:
    shift_df = pd.concat(shift_dfs, ignore_index=True)
else:
    raise FileNotFoundError("No shift table files were found.")

print("Shift Data Date Range:", shift_df['Date'].min(), "to", shift_df['Date'].max())
print("Shift Unique Dates:", len(shift_df['Date'].unique()))

# Load weather data
weather_file = "/home/ttnk0/projects/ga_nurse_scheduling/data/weather_data.csv"
try:
    # Skip the first 4 rows (metadata) and assign column names
    weather_df = pd.read_csv(weather_file, skiprows=4, names=['年月日時', '天気', '品質情報', '均質番号'], encoding='utf-8')
except UnicodeDecodeError:
    print("UTF-8 encoding failed. Trying shift-jis encoding...")
    weather_df = pd.read_csv(weather_file, skiprows=4, names=['年月日時', '天気', '品質情報', '均質番号'], encoding='shift-jis')

# Print column names to diagnose issue
print("Weather Data Columns:", weather_df.columns.tolist())

# Process weather data: Parse date-time and filter for 6:00-10:00
try:
    weather_df['DateTime'] = pd.to_datetime(weather_df['年月日時'])
except KeyError as e:
    print(f"Error: Column '年月日時' not found in weather data. Available columns: {weather_df.columns.tolist()}")
    raise

weather_df['Date'] = weather_df['DateTime'].dt.date
weather_df['Hour'] = weather_df['DateTime'].dt.hour

# Filter for 6:00-10:00 (temporarily removing quality filters for debugging)
weather_df = weather_df[weather_df['Hour'].between(6, 10)]

# Convert weather column to numeric, handling non-numeric values
weather_df['天気'] = pd.to_numeric(weather_df['天気'], errors='coerce')

# Determine rainy days: Any weather code >= 10 from 6:00-10:00
rainy_days = weather_df.groupby('Date').apply(
    lambda x: 1 if (x['天気'] >= 10).any() else 0,
    include_groups=False
).reset_index().rename(columns={0: 'Rainy'})

# Convert Date to datetime64[ns] for consistent merging
rainy_days['Date'] = pd.to_datetime(rainy_days['Date'])

print("Weather Unique Dates:", len(rainy_days['Date'].unique()))

# Merge shift and weather data
merged_df = pd.merge(
    shift_df,
    rainy_days,
    on='Date',
    how='inner'
)

# Check if merged data is empty
if merged_df.empty:
    print("Shift Dates:", sorted(shift_df['Date'].unique()))
    print("Weather Dates:", sorted(rainy_days['Date'].unique()))
    raise ValueError("No overlapping dates between shift and weather data.")

merged_df.to_csv("merged_df.csv")

# Create contingency table
contingency_table = pd.crosstab(
    merged_df['Oba_Attendance'],
    merged_df['Rainy'],
    rownames=['Attendance (0=Absent, 1=Present)'],
    colnames=['Weather (0=Non-Rainy, 1=Rainy)']
)

# Perform chi-squared test
chi2, p, dof, expected = chi2_contingency(contingency_table)

# Print results
print("\nContingency Table:")
print(contingency_table)
print("\nChi-Squared Test Results:")
print(f"Chi-Squared Statistic: {chi2:.4f}")
print(f"P-value: {p:.4f}")
print(f"Degrees of Freedom: {dof}")
print("\nExpected Frequencies:")
print(pd.DataFrame(expected, index=contingency_table.index, columns=contingency_table.columns))
print("\nInterpretation:")
if p < 0.05:
    print("There is a statistically significant association between Oba's attendance and rainy days (p < 0.05).")
else:
    print("There is no statistically significant association between Oba's attendance and rainy days (p >= 0.05).")

# Warn if expected frequencies are low
if (expected < 5).any():
    print("\nWarning: Some expected frequencies are less than 5, which may affect the reliability of the chi-squared test.")