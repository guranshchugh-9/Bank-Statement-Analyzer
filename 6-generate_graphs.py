import os
import pandas as pd
import matplotlib.pyplot as plt

# Define directories
OUTPUT_FOLDER = "processed_files/"
INPUT_FILE = os.path.join(OUTPUT_FOLDER, "categorized_bank_statement.csv")

# Ensure categorized bank statement exists
if not os.path.exists(INPUT_FILE):
    print("Error: Categorized bank statement file not found!")
    exit()

# Load the categorized bank statement
df = pd.read_csv(INPUT_FILE)

# Convert 'Date' column to datetime if it exists
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M')  # Extract month-year
else:
    print("Error: 'Date' column missing in the dataset!")
    exit()

# Group by Month for income and expenses
monthly_summary = df.groupby('Month').agg({
    'Deposit Amt.': 'sum',
    'Withdrawal Amt.': 'sum'
}).reset_index()

# Graph 1: Monthly Income vs Expenses (Line Chart)
plt.figure(figsize=(10, 6))
plt.plot(monthly_summary['Month'].astype(str), monthly_summary['Deposit Amt.'], label='Income', marker='o', color='blue')
plt.plot(monthly_summary['Month'].astype(str), monthly_summary['Withdrawal Amt.'], label='Expenses', marker='o', color='red')
plt.title('Monthly Income vs Monthly Expenses')
plt.xlabel('Month')
plt.ylabel('Amount (₹)')
plt.legend()
plt.grid()
plt.xticks(rotation=45)
plt.tight_layout()
graph_path1 = os.path.join(OUTPUT_FOLDER, "monthly_income_vs_expenses.png")
plt.savefig(graph_path1)
plt.close()

# Graph 2: Monthly Savings (Bar Chart)
monthly_summary['Savings'] = monthly_summary['Deposit Amt.'] - monthly_summary['Withdrawal Amt.']
plt.figure(figsize=(10, 6))
plt.bar(monthly_summary['Month'].astype(str), monthly_summary['Savings'], color='green')
plt.title('Monthly Savings')
plt.xlabel('Month')
plt.ylabel('Savings (₹)')
plt.xticks(rotation=45)
plt.tight_layout()
graph_path2 = os.path.join(OUTPUT_FOLDER, "monthly_savings.png")
plt.savefig(graph_path2)
plt.close()

# Graph 3: Expenses by Category (Pie Chart)
expense_categories = df[df['Withdrawal Amt.'] > 0].groupby('Category')['Withdrawal Amt.'].sum()
plt.figure(figsize=(8, 8))
plt.pie(expense_categories, labels=expense_categories.index, autopct='%1.1f%%', startangle=140)
plt.title('Expenses by Category')
plt.tight_layout()
graph_path3 = os.path.join(OUTPUT_FOLDER, "expenses_by_category.png")
plt.savefig(graph_path3)
plt.close()

print(f"Graphs saved successfully:\n{graph_path1}\n{graph_path2}\n{graph_path3}")
