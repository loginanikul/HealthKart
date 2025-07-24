import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
import plotly.graph_objects as go  # 👈 Use this instead of plotly.express

def scrape_wikipedia_population():
    url = 'https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    table = None
    for t in soup.find_all('table', {'class': 'wikitable'}):
        caption = t.find('caption')
        if caption and 'population' in caption.get_text().lower():
            table = t
            break

    if not table:
        print("Could not find the population table")
        return None

    headers = []
    header_row = table.find('tr')
    for th in header_row.find_all(['th', 'td']):
        header_text = th.get_text().strip()
        header_text = re.sub(r'\[.*?\]', '', header_text)
        headers.append(header_text)

    col_mapping = {}
    for i, header in enumerate(headers):
        header_lower = header.lower()
        if 'location' in header_lower or 'country' in header_lower:
            col_mapping['Country'] = i
        elif 'population' in header_lower:
            col_mapping['Population'] = i
        elif '%' in header_lower or 'percent' in header_lower:
            col_mapping['Percentage'] = i

    required_cols = ['Country', 'Population']
    if not all(col in col_mapping for col in required_cols):
        print("Could not identify all required columns")
        print(f"Found columns: {headers}")
        return None

    data = []
    for row in table.find_all('tr')[1:]:
        cells = row.find_all(['td', 'th'])
        row_data = []
        for cell in cells:
            cell_text = cell.get_text().strip()
            cell_text = re.sub(r'\[.*?\]', '', cell_text)
            cell_text = re.sub(r'\s+', ' ', cell_text)
            row_data.append(cell_text)
        if len(row_data) == len(headers):
            data.append(row_data)

    selected_cols = [col_mapping['Country'], col_mapping['Population']]
    if 'Percentage' in col_mapping:
        selected_cols.append(col_mapping['Percentage'])

    df = pd.DataFrame(data)[selected_cols]

    if 'Percentage' in col_mapping:
        df.columns = ['Country', 'Population', 'Percentage']
    else:
        df.columns = ['Country', 'Population']

    df['Country'] = df['Country'].apply(lambda x: re.sub(r'\[.*?\]', '', x))
    df['Population'] = df['Population'].str.replace(',', '').str.replace(' ', '')
    df['Population'] = pd.to_numeric(df['Population'], errors='coerce')
    df = df[df['Population'].notna() & (df['Population'] > 0)]

    world_population = df.iloc[0]['Population']
    df = df[~df['Country'].str.lower().str.contains('world')]

    if 'Percentage' not in df.columns:
        df['Percentage'] = (df['Population'] / world_population) * 100
    else:
        df['Percentage'] = df['Percentage'].str.replace(',', '.').str.replace('%', '')
        df['Percentage'] = pd.to_numeric(df['Percentage'], errors='coerce')

    return df.head(20)

# Main execution
if __name__ == "__main__":
    df = scrape_wikipedia_population()

    if df is not None:
        df_display = df.copy()
        df_display['Percentage'] = df_display['Percentage'].apply(lambda x: f"{x:.2f}%")

        print("\nTop 20 Countries by Population (with % of world):\n")
        print(df_display[['Country', 'Population', 'Percentage']].to_string(index=False))

        # Prepare for heatmap
        heatmap_df = df.sort_values("Percentage", ascending=False).copy()
        heatmap_df.set_index('Country', inplace=True)

        # Text annotations inside heatmap
        text_annotations = heatmap_df['Percentage'].apply(lambda x: f"{x:.2f}%").values.reshape(-1, 1)

        # Create Plotly interactive heatmap with annotations
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_df['Percentage'].values.reshape(-1, 1),
            x=["% of World Population"],
            y=heatmap_df.index.tolist(),
            text=text_annotations,
            texttemplate="%{text}",
            textfont={"size": 14},
            hovertemplate="<b>%{y}</b><br>Population Share: %{z:.2f}%<extra></extra>",
            colorscale="YlGnBu",
            showscale=True
        ))

        fig.update_layout(
            title="Top 20 Countries by Population (% of World)",
            title_x=0.5,
            height=600,
            xaxis=dict(showticklabels=False),
            yaxis=dict(tickfont=dict(size=12))
        )

        fig.show()

        # Optional: Save to HTML
        fig.write_html("interactive_population_heatmap_with_labels.html")

    else:
        print("Failed to retrieve population data.")
