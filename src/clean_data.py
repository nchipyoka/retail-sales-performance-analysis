"""Clean the Kaggle retail_store_sales.csv without deleting any rows.

Usage: python clean_data.py retail_store_sales.csv retail_store_sales_clean.csv

Rules found in the data (all verified before use):
  * Each item has one fixed price: price = 5 + 1.5 * (item number - 1)
  * Each category has its own item code (e.g. Furniture -> FUR)
  * Total Spent = Price Per Unit * Quantity on every complete row
"""
import sys
import pandas as pd

CODES = {
    "Beverages": "BEV", "Butchers": "BUT", "Computers and electric accessories": "CEA",
    "Electric household essentials": "EHE", "Food": "FOOD", "Furniture": "FUR",
    "Milk Products": "MILK", "Patisserie": "PAT",
}

df = pd.read_csv(sys.argv[1])
df["Transaction Date"] = pd.to_datetime(df["Transaction Date"])
c = df.copy()

for _ in range(2):  # two passes so each fix can feed the next
    n = c["Item"].str.extract(r"Item_(\d+)_")[0].astype(float)
    c["Price Per Unit"] = c["Price Per Unit"].fillna(5 + 1.5 * (n - 1))        # price from item
    c["Price Per Unit"] = c["Price Per Unit"].fillna(c["Total Spent"] / c["Quantity"])
    item_no = ((c["Price Per Unit"] - 5) / 1.5 + 1).round()
    c["Item"] = c["Item"].fillna("Item_" + item_no.astype("Int64").astype(str) + "_" + c["Category"].map(CODES))
    c["Quantity"] = c["Quantity"].fillna(c["Total Spent"] / c["Price Per Unit"])
    c["Total Spent"] = c["Total Spent"].fillna(c["Price Per Unit"] * c["Quantity"])

# Blank discount flags are labelled, not guessed
c["Discount Applied"] = c["Discount Applied"].map({True: "Yes", False: "No", "True": "Yes", "False": "No"}).fillna("Unknown")
c["Year"] = c["Transaction Date"].dt.year
c["Month"] = c["Transaction Date"].dt.month
c["Quantity"] = c["Quantity"].astype("Int64")

print("Missing before:", df[["Item", "Price Per Unit", "Quantity", "Total Spent"]].isna().sum().to_dict())
print("Missing after: ", c[["Item", "Price Per Unit", "Quantity", "Total Spent"]].isna().sum().to_dict())
c.to_csv(sys.argv[2], index=False)
