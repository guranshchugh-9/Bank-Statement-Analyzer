import os
import pandas as pd

# Define directories
OUTPUT_FOLDER = "processed_files/"
INPUT_FILE = os.path.join(OUTPUT_FOLDER, "categorized_bank_statement.csv")
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "financial_summary.txt")

# Ensure the categorized bank statement exists
if not os.path.exists(INPUT_FILE):
    print("Error: Categorized bank statement file not found!")
    exit()

# Load the CSV
df = pd.read_csv(INPUT_FILE)

# Ensure required columns exist
required_columns = {'Date', 'Deposit Amt.', 'Withdrawal Amt.', 'Closing Balance'}
if not required_columns.issubset(df.columns):
    print("Error: Missing required columns in the dataset!")
    exit()

# Convert amount columns to numeric safely
def convert_amount(col):
    return pd.to_numeric(col.astype(str).str.replace(',', ''), errors='coerce').fillna(0)

df['Withdrawal Amt.'] = convert_amount(df['Withdrawal Amt.'])
df['Deposit Amt.'] = convert_amount(df['Deposit Amt.'])
df['Closing Balance'] = convert_amount(df['Closing Balance'])

# Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Calculate financial summary
expenditure = df['Withdrawal Amt.'].sum()
income = df['Deposit Amt.'].sum()
savings = income - expenditure

# Extract month-year for grouping
df['Month'] = df['Date'].dt.to_period('M')

# Calculate average monthly balance
monthly_avg_balance = df.groupby('Month')['Closing Balance'].mean().mean()

# Calculate average monthly expenses
expenditure_avg_balance = df.groupby('Month')['Withdrawal Amt.'].sum().mean()

# Format financial summary
summary = f"""
Income: ₹{income:,.2f}\n
Expenditure: ₹{expenditure:,.2f}\n
Savings: ₹{savings:,.2f}\n
Average Monthly Balance: ₹{monthly_avg_balance:,.2f}\n
Savings to Income Ratio: {((savings / income) * 100) if income != 0 else 0:.2f}%\n
Average Monthly Expenses: ₹{expenditure_avg_balance:,.2f}
"""

# Print and save results
print(summary)

with open(OUTPUT_FILE, "w") as f:
    f.write(summary)

print(f"Financial summary saved to: {OUTPUT_FILE}")
