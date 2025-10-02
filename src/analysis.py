# 🏘️ Amsterdam Airbnb & Gentrification
# Author: Greeshmanth Balasa

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

# --- Paths & folders ---
DATA_CANDIDATES = ["data/listings.csv", "data/listings.csv.gz"]
FIG_DIR = "figures"
os.makedirs(FIG_DIR, exist_ok=True)

# --- Load dataset ---
path = next((p for p in DATA_CANDIDATES if os.path.exists(p)), None)
if path is None:
    raise FileNotFoundError("Put 'listings.csv' (or .csv.gz) into the data/ folder.")

print(f"Loading dataset: {path}")
if path.endswith(".gz"):
    df = pd.read_csv(path, compression="gzip", low_memory=False)
else:
    df = pd.read_csv(path, low_memory=False)

print("Rows, Cols:", df.shape)
print("Sample columns:", list(df.columns[:15]))

# --- Price cleanup (InsideAirbnb often stores as '$1,234.00') ---
if "price" not in df.columns:
    raise KeyError("No 'price' column found. Are you sure this is the *listings* file?")

if df["price"].dtype == "object":
    df["price"] = (
        df["price"].astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

# --- Pick the best neighbourhood column ---
NEIGH_CANDIDATES = ["neighbourhood_cleansed", "neighbourhood", "neighbourhood_group_cleansed"]
neigh_col = next((c for c in NEIGH_CANDIDATES if c in df.columns), None)
if neigh_col is None:
    raise KeyError("No neighbourhood column found. Check columns printed above.")

# Basic sanity: should have many unique names, not just 'Netherlands'
unique_vals = df[neigh_col].astype(str).str.strip().str.lower().unique()
if len(unique_vals) < 5 or "netherlands" in unique_vals:
    raise ValueError(
        f"Column '{neigh_col}' does not look like Amsterdam neighborhoods. "
        "Double-check you downloaded the *Amsterdam listings* file."
    )

# --- Price distribution (cap at 99th percentile for readability) ---
p99 = df["price"].dropna().quantile(0.99)
plt.figure(figsize=(12,5))
sns.histplot(df["price"].dropna(), bins=50)
plt.xlim(0, p99)
plt.title("Distribution of Airbnb Prices in Amsterdam (capped at 99th percentile)")
plt.xlabel("Price (€)")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "price_distribution.png"))
plt.close()

# --- Top neighborhoods by listing count ---
top_neigh = df[neigh_col].value_counts().head(10)
plt.figure(figsize=(12,6))
sns.barplot(x=top_neigh.index, y=top_neigh.values)  # no palette to avoid seaborn warning
plt.xticks(rotation=45, ha="right")
plt.title(f"Top 10 {neigh_col} by Number of Listings")
plt.ylabel("Listings")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "top_neighbourhoods.png"))
plt.close()

# --- Jordaan focus (usually falls under 'Centrum-West') ---
jordaan_keywords = ["jordaan", "centrum-west"]
mask_jordaan = df[neigh_col].astype(str).str.contains("|".join(jordaan_keywords), case=False, na=False)
jordaan = df[mask_jordaan].copy()
print("Listings matched as Jordaan/Centrum-West:", len(jordaan))

if not jordaan.empty:
    p99_j = jordaan["price"].dropna().quantile(0.99)
    plt.figure(figsize=(12,5))
    sns.histplot(jordaan["price"].dropna(), bins=40)
    plt.xlim(0, p99_j)
    plt.title("Price Distribution in Jordaan/Centrum-West (99th pct cap)")
    plt.xlabel("Price (€)")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "jordaan_price_distribution.png"))
    plt.close()

print("✅ Done. Check the 'figures/' folder.")
