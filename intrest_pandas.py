import pandas as pd
from pandas.io.pytables import dropna_doc
file_path = "/Users/anirudha/Desktop/analyst1/Superstore_Sample.xls"
discount_data = {
            'Discount': [0.1, 0.2, None, 0.0, None]
}

df= pd.read_excel(file_path)

# print(df)
# print(df.head())
print(df.info())

# print(df['Profit'].head(5))
# top_5_profit=df.sort_values(by='Profit').head(5)
# top_5_order_profit = top_5_profit[['Order ID', 'Profit']]
# print(top_5_order_profit)

# average_profit_by_region = df.groupby('Region')['Profit'].mean().sort_values(ascending=False)

# # Display the result
# print("Average Profit by Region:")
# print(average_profit_by_region)

# # Get the Region with highest average profit
# highest_avg_profit_region = average_profit_by_region.idxmax()
# highest_avg_value = average_profit_by_region.max()

# print(highest_avg_value)
# print(f"\n✅ Region with highest average profit: {highest_avg_profit_region},{highest_avg_value}")  

missing_discount = df[df['Discount'].isnull()]
print("Rows with missing Discount values:")
print(missing_discount)
df['Discount'] = df['Discount'].fillna(0.1)
df.rename(columns={'Order Date': 'OrderDate_kardiya'}, inplace=True)
df['OrderDate_list'] = pd.to_datetime(df['OrderDate_kardiya'])
df['Profit'] = df['Profit'].apply(lambda x: 2 if x < 0 else x)
pivot = df.pivot_table(index='Category', columns='Region', values='Sales', aggfunc='sum').head(5)
print('The Result of pivot table',pivot)

print(df.head(5))