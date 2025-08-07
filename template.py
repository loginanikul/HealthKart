import pandas as pd

# ---------------------
# 1. Load Data
# ---------------------
def load_data(path, file_type='csv', **kwargs):
    if file_type == 'csv':
        df = pd.read_csv(path, **kwargs)
    elif file_type == 'excel':
        df = pd.read_excel(path, **kwargs)
    elif file_type == 'json':
        df = pd.read_json(path, **kwargs)
    else:
        raise ValueError("Unsupported file type.")
    return df

# ---------------------
# 2. Inspect Data
# ---------------------
def inspect_data(df):
    print("🔍 Data Overview:")
    print(df.head(), "\n")
    print(df.tail(), "\n")
    print(df.info(), "\n")
    print(df.describe(include='all'), "\n")
    print("Missing values:\n", df.isnull().sum())

# ---------------------
# 3. Clean Data
# ---------------------
def clean_data(df):
    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    # Replace negative profits with 0
    if 'profit' in df.columns:
        df['profit'] = df['profit'].apply(lambda x: max(x, 0))

    # Fill null discounts with 0 if present
    if 'discount' in df.columns:
        df['discount'] = df['discount'].fillna(0)

    # Drop rows with critical nulls (customizable)
    df = df.dropna(subset=['sales']) if 'sales' in df.columns else df

    return df

# ---------------------
# 4. Filter Data
# ---------------------
def filter_data(df, min_sales=0):
    if 'sales' in df.columns:
        df = df[df['sales'] >= min_sales]
    return df

# ---------------------
# 5. Save Cleaned Data
# ---------------------
def save_data(df, path='cleaned_data.csv'):
    df.to_csv(path, index=False)
    print(f"✅ Cleaned data saved to {path}")

# ---------------------
# 🧪 Main Runner
# ---------------------
def run_pipeline():
    # Load
    df = load_data("superstore.csv")

    # Inspect
    inspect_data(df)

    # Clean
    df_cleaned = clean_data(df)

    # Filter
    df_filtered = filter_data(df_cleaned, min_sales=100)

    # Save
    save_data(df_filtered)

# ---------------------
# Execute
# ---------------------
if __name__ == "__main__":
    run_pipeline()
