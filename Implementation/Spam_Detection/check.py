import pandas as pd

df = pd.read_csv("../data/enron_emails.csv")  # Adjust path if needed
print(df.columns)
print(df.head())  # Show first 5 rows
