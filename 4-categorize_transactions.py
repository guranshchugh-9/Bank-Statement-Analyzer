import os
import re
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Define directories
OUTPUT_FOLDER = "processed_files/"
INPUT_FILE = os.path.join(OUTPUT_FOLDER, "cleaned_bank_statement.csv")
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "categorized_bank_statement.csv")

class UPITransactionCategorizer:
    def __init__(self):
        self.company_categories = {
            "PAYROLL": "INCOME", "SALARY CREDIT": "INCOME", "SAL CREDIT": "INCOME",
            "HR PAYMENT": "INCOME", "PAY DISBURSEMENT": "INCOME", "WAGES": "INCOME",
            "BUSINESS INCOME": "INCOME", "FREELANCE PAYMENT": "INCOME", "CLIENT PAYMENT": "INCOME",
            "INVOICE PAYMENT": "INCOME", "PAYMENT RECEIVED": "INCOME", "REVENUE CREDIT": "INCOME",
            "INTEREST CREDIT": "INCOME", "BANK INTEREST": "INCOME", "FD INTEREST": "INCOME",
            "RD INTEREST": "INCOME", "DEPOSIT INTEREST": "INCOME", "SAVINGS ACCOUNT INTEREST": "INCOME",
            "REFUND": "INCOME", "REVERSAL": "INCOME", "CASHBACK": "INCOME", "MONEYBACK": "INCOME",
            "DISCOUNT CREDIT": "INCOME", "CHARGEBACK": "INCOME", "REVERSAL CREDIT": "INCOME",
            "SUBSIDY": "INCOME", "PENSION CREDIT": "INCOME", "SCHOLARSHIP": "INCOME", "GOVERNMENT PAYMENT": "INCOME",

            "PRUDENT": "SAVINGS_INVESTMENTS", "SBI MF": "SAVINGS_INVESTMENTS", "HDFC MF": "SAVINGS_INVESTMENTS",
            "ICICI PRU MF": "SAVINGS_INVESTMENTS", "AXIS MF": "SAVINGS_INVESTMENTS", "MOTILAL OSWAL MF": "SAVINGS_INVESTMENTS",
            "UTI MF": "SAVINGS_INVESTMENTS", "NIPPON MF": "SAVINGS_INVESTMENTS", "TATA MF": "SAVINGS_INVESTMENTS",
            "ZERODHA": "SAVINGS_INVESTMENTS", "UPSTOX": "SAVINGS_INVESTMENTS", "GROWW": "SAVINGS_INVESTMENTS",
            "5PAISA": "SAVINGS_INVESTMENTS", "ANGEL ONE": "SAVINGS_INVESTMENTS", "ICICI DIRECT": "SAVINGS_INVESTMENTS",
            "SIP": "SAVINGS_INVESTMENTS", "FD": "SAVINGS_INVESTMENTS", "RD": "SAVINGS_INVESTMENTS",
            "NATIONAL SAVINGS CERTIFICATE": "SAVINGS_INVESTMENTS", "BOND PURCHASE": "SAVINGS_INVESTMENTS",

            "LOAN EMI": "LIABILITIES", "HDFC EMI": "LIABILITIES", "ICICI EMI": "LIABILITIES", "SBI EMI": "LIABILITIES",
            "BAJAJ FIN EMI": "LIABILITIES", "CREDIT CARD PAYMENT": "LIABILITIES", "HDFC CREDIT CARD": "LIABILITIES",
            "ICICI CC PAYMENT": "LIABILITIES", "AXIS CC BILL": "LIABILITIES", "HDFC LOAN": "LIABILITIES",
            "ICICI LOAN": "LIABILITIES", "KOTAK LOAN": "LIABILITIES", "AXIS LOAN": "LIABILITIES", "INDUSIND LOAN": "LIABILITIES",
            "ZESTMONEY": "LIABILITIES", "SIMPL PAY": "LIABILITIES", "LAZYPAY": "LIABILITIES", "POSTPE": "LIABILITIES",
            "AMAZON PAY LATER": "LIABILITIES", "EMI": "LIABILITIES",

            "HUNGERBOX":"DISCRETIONARY_EXPENSES", "HUBBLE":"DISCRETIONARY_EXPENSES","AMAZON": "DISCRETIONARY_EXPENSES", "FLIPKART": "DISCRETIONARY_EXPENSES", "AJIO": "DISCRETIONARY_EXPENSES",
            "TATA CLIQ": "DISCRETIONARY_EXPENSES", "NYKAA": "DISCRETIONARY_EXPENSES", "NETFLIX": "DISCRETIONARY_EXPENSES",
            "PRIME VIDEO": "DISCRETIONARY_EXPENSES", "SPOTIFY": "DISCRETIONARY_EXPENSES", "HOTSTAR": "DISCRETIONARY_EXPENSES",
            "APPLE MUSIC": "DISCRETIONARY_EXPENSES", "SWIGGY": "DISCRETIONARY_EXPENSES", "ZOMATO": "DISCRETIONARY_EXPENSES",
            "DOMINOS": "DISCRETIONARY_EXPENSES", "MCDONALDS": "DISCRETIONARY_EXPENSES", "BARISTA": "DISCRETIONARY_EXPENSES",
            "STARBUCKS": "DISCRETIONARY_EXPENSES", "MAKEMYTRIP": "DISCRETIONARY_EXPENSES", "YATRA": "DISCRETIONARY_EXPENSES",
            "GOIBIBO": "DISCRETIONARY_EXPENSES", "UBER": "DISCRETIONARY_EXPENSES", "OLA": "DISCRETIONARY_EXPENSES",
            "AIRBNB": "DISCRETIONARY_EXPENSES", "APPLE STORE": "DISCRETIONARY_EXPENSES", "ROLEX": "DISCRETIONARY_EXPENSES",
            "OMEGA": "DISCRETIONARY_EXPENSES", "LV": "DISCRETIONARY_EXPENSES",

            "HPCL": "TRANSPORT_FUEL", "BPCL": "TRANSPORT_FUEL", "IOCL": "TRANSPORT_FUEL", "PETROL PUMP": "TRANSPORT_FUEL",
            "METRO CARD": "TRANSPORT_FUEL", "IRCTC": "TRANSPORT_FUEL", "RAILWAY TICKET": "TRANSPORT_FUEL",
            "BLABLA CAR": "TRANSPORT_FUEL", "VEHICLE LOAN": "TRANSPORT_FUEL",

            "DREAM11": "RED_FLAGS", "RUMMYCIRCLE": "RED_FLAGS", "BET365": "RED_FLAGS", "PARIMATCH": "RED_FLAGS",
            "CASHE": "RED_FLAGS", "MONEYVIEW": "RED_FLAGS", "KREDITBEE": "RED_FLAGS", "NAVI LOAN": "RED_FLAGS",
            "CRYPTO EXCHANGE": "RED_FLAGS", "FOREX TRADING": "RED_FLAGS", "RIPPLE": "RED_FLAGS", "WAZIRX": "RED_FLAGS",
            "COINBASE": "RED_FLAGS", "COINDCX": "RED_FLAGS", "ZEBPAY": "RED_FLAGS",

            "APOLLO": "HEALTHCARE_INSURANCE", "FORTIS": "HEALTHCARE_INSURANCE", "MAX HEALTHCARE": "HEALTHCARE_INSURANCE",
            "MEDANTA": "HEALTHCARE_INSURANCE", "LIC PREMIUM": "HEALTHCARE_INSURANCE", "TATA AIG": "HEALTHCARE_INSURANCE",
            "ICICI LOMBARD": "HEALTHCARE_INSURANCE", "HDFC ERGO": "HEALTHCARE_INSURANCE", "PHARMACY": "HEALTHCARE_INSURANCE",
            "1MG": "HEALTHCARE_INSURANCE", "MEDPLUS": "HEALTHCARE_INSURANCE",

            "INCOME TAX": "GOVERNMENT_TAX_PAYMENTS", "GST PAYMENT": "GOVERNMENT_TAX_PAYMENTS", "TDS": "GOVERNMENT_TAX_PAYMENTS",
            "NPS": "GOVERNMENT_TAX_PAYMENTS", "EPF": "GOVERNMENT_TAX_PAYMENTS", "PPF": "GOVERNMENT_TAX_PAYMENTS",
            "FASTAG RECHARGE": "GOVERNMENT_TAX_PAYMENTS", "TRAFFIC CHALLAN": "GOVERNMENT_TAX_PAYMENTS",
            "MUNICIPAL TAX": "GOVERNMENT_TAX_PAYMENTS"
        }


        # Load LLM for categorization fallback
        self.llm = ChatGroq(
            temperature=0.3,
            model_name="llama-3.3-70b-specdec",
            groq_api_key=os.getenv("GROK_API_KEY")
        )

    def extract_upi_company(self, narration):
        """Extracts UPI merchant name from narration."""
        match = re.search(r'UPI-([\w\s&]+?)-', narration, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def categorize_transaction(self, narration):
        """Categorizes a transaction based on predefined categories or uses LLM if unknown."""
        narration_upper = narration.upper()
        company_name = self.extract_upi_company(narration_upper)

        if company_name and company_name in self.company_categories:
            return self.company_categories[company_name]

        for keyword, category in self.company_categories.items():
            if keyword in narration_upper:
                return category

        # Fallback: Use LLM for unknown businesses
        if company_name:
            try:
                response = self.llm.invoke(f"Is '{company_name}' a business/company name or a person's name? "
                                           "If its a person's name return OTHERS. "
                                           "If it's clearly a business, return the category from: SAVINGS_INVESTMENTS, "
                                           "LIABILITIES, DISCRETIONARY_EXPENSES, TRANSPORT_FUEL, RED_FLAGS, HEALTHCARE_INSURANCE, "
                                           "GOVERNMENT_TAX_PAYMENTS. "
                                           "If unclear, return 'OTHERS'. Return only the category name.")
                return response.content.strip().upper()
            except Exception as e:
                print(f"LLM Error for {company_name}: {e}")
                return "OTHERS"

        return "OTHERS"

# Main execution block
if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        print("Error: Cleaned bank statement file not found!")
        exit()

    categorizer = UPITransactionCategorizer()
    df = pd.read_csv(INPUT_FILE)

    # Convert amount columns to numeric type
    def convert_amount(col):
        return pd.to_numeric(col.astype(str).str.replace(',', ''), errors='coerce')

    df['Withdrawal Amt.'] = convert_amount(df['Withdrawal Amt.'])
    df['Deposit Amt.'] = convert_amount(df['Deposit Amt.'])

    # Categorize transactions
    df['Category'] = df['Narration'].apply(categorizer.categorize_transaction)

    # Handle OTHERS category based on transaction amounts
    others_mask = df['Category'] == 'OTHERS'
    withdrawal_mask = others_mask & df['Withdrawal Amt.'].notna() & (df['Withdrawal Amt.'] > 0)
    deposit_mask = others_mask & df['Deposit Amt.'].notna() & (df['Deposit Amt.'] > 0)

    df.loc[withdrawal_mask, 'Category'] = 'Other Expenses'
    df.loc[deposit_mask, 'Category'] = 'Other Income'

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Categorized transactions saved to: {OUTPUT_FILE}")