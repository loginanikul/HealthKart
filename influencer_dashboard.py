from sqlalchemy import create_engine, text
import pandas as pd
import dash
from dash import dcc, html, dash_table
import plotly.express as px

# Database configuration
username = 'root'
password = 'Anikul@2143'
host = 'localhost'
port = '3306'
database = 'Project'

# Create SQLAlchemy engine
engine = create_engine(
    f"mysql+pymysql://{username}:{password.replace('@', '%40')}@{host}:{port}/{database}"
)

# Fetch data from database
with engine.connect() as conn:
    df = pd.read_sql(text("SELECT * FROM influencers"), conn)

# Create Dash application
app = dash.Dash(__name__)

# Create bar chart
fig = px.bar(
    df,
    x='name',
    y='follower_count',
    color='platform',
    title='Influencer Followers by Platform',
    labels={'name': 'Influencer', 'follower_count': 'Followers'},
    height=500
)

# Define dashboard layout
app.layout = html.Div([
    html.H1("Influencer Dashboard by Anirudha", style={'textAlign': 'center'}),

    # Bar chart
    html.Div([
        dcc.Graph(figure=fig)
    ], style={'width': '80%', 'margin': '0 auto'}),

    # Data table
    html.H2("Influencer Data Table", style={'textAlign': 'center', 'marginTop': '40px'}),

    dash_table.DataTable(
        id='influencer-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_table={'overflowX': 'auto', 'width': '90%', 'margin': '0 auto'},
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white',
            'fontWeight': 'bold'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'border': '1px solid grey'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        page_size=10,
        filter_action='native',
        sort_action='native'
    ),

    # Summary table
    html.H3("Summary Statistics", style={'textAlign': 'center', 'marginTop': '40px'}),

    dash_table.DataTable(
        id='summary-table',
        columns=[
            {"name": "Metric", "id": "metric"},
            {"name": "Value", "id": "value"}
        ],
        data=[
            {"metric": "Total Influencers", "value": len(df)},
            {"metric": "Total Followers", "value": f"{df['follower_count'].sum():,}"},
            {"metric": "Average Followers", "value": f"{df['follower_count'].mean():,.0f}"}
        ],
        style_table={'width': '50%', 'margin': '0 auto'},
        style_cell={'textAlign': 'center', 'padding': '8px'},
        style_header={
            'backgroundColor': 'lightblue',
            'fontWeight': 'bold'
        }
    )
], style={'fontFamily': 'Arial, sans-serif'})

# Run the server
if __name__ == '__main__':
    app.run(debug=True)