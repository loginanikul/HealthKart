from sqlalchemy import create_engine, text
import pandas as pd
import dash
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

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

# Fetch posts data from database
with engine.connect() as conn:
    posts_df = pd.read_sql(text("SELECT * FROM posts"), conn)
    print(posts_df.head(1))

# Convert date column
if 'date' in posts_df.columns:
    posts_df['date'] = pd.to_datetime(posts_df['date'])

# Calculate metrics
if all(col in posts_df.columns for col in ['likes', 'comments']):
    posts_df['total_engagement'] = posts_df['likes'] + posts_df['comments']
    if 'reach' in posts_df.columns:
        posts_df['engagement_rate'] = ((posts_df['total_engagement'] / posts_df['reach'].replace(0, pd.NA)) * 100).fillna(0).round(2)
    else:
        posts_df['engagement_rate'] = None

# Create Dash app
app = dash.Dash(__name__)

# Engagement bar chart
engagement_fig = px.bar(
    posts_df.sort_values('total_engagement', ascending=False),
    x='influencer_id',
    y='total_engagement',
    color='platform',
    title='Total Engagement by Influencer',
    labels={'influencer_id': 'Influencer ID'},
    height=500
)

# Platform distribution
platform_fig = px.pie(
    posts_df,
    names='platform',
    title='Post Distribution by Platform',
    hole=0.3
)

# Timeline
if 'date' in posts_df.columns:
    time_series_df = posts_df.set_index('date').resample('D').size().reset_index(name='count')
    today_str = datetime.today().strftime('%B %d, %Y')
    timeline_fig = px.line(
        time_series_df,
        x='date',
        y='count',
        title=(f'Daily Post Activity of {today_str}'),
        labels={'date': 'Date', 'count': 'Number of Posts'}
    )
else:
    timeline_fig = go.Figure()
    timeline_fig.update_layout(title='Daily Post Activity (No date data available)')

# Top posts table
top_posts_df = posts_df.sort_values('total_engagement', ascending=False).head(10)[
    ['influencer_id', 'caption', 'platform', 'likes', 'comments', 'total_engagement']
]

# Layout
app.layout = html.Div([
    html.H1("Posts Tracking Dashboard by Anirudha & Ani's AI", style={'textAlign': 'center' }),
    
    html.Div([
        html.Div([
            html.Div(f"{len(posts_df)}", style={'fontSize': '2.5rem', 'fontWeight': 'bold'}),
            html.Div("Total Posts", style={'fontSize': '1rem' ,  'background-color': ''})
        ], className='kpi-card'),
        
        html.Div([
            html.Div(f"{posts_df['total_engagement'].sum():,}", style={'fontSize': '2.5rem', 'fontWeight': 'bold'}),
            html.Div("Total Engagement", style={'fontSize': '1rem'})
        ], className='kpi-card'),
        
        html.Div([
            html.Div(f"{posts_df['engagement_rate'].mean():.2f}%", style={'fontSize': '2.5rem', 'fontWeight': 'bold'}),
            html.Div("Avg. Engagement Rate", style={'fontSize': '1rem'})
        ], className='kpi-card'),
        
        html.Div([
            html.Div(f"{posts_df['likes'].mean():,.0f}", style={'fontSize': '2.5rem', 'fontWeight': 'bold'}),
            html.Div("Avg. Likes per Post", style={'fontSize': '1rem'})
        ], className='kpi-card')
    ], style={
        'display': 'flex', 
        'justifyContent': 'space-around', 
        'margin': '20px 0',
        'flexWrap': 'wrap'
    }),
    
    html.Div([
        html.Div([dcc.Graph(figure=engagement_fig)], style={'width': '65%', 'padding': '10px'}),
        html.Div([dcc.Graph(figure=platform_fig)], style={'width': '35%', 'padding': '10px'}),
    ], style={'display': 'flex', 'margin': '0 auto', 'width': '95%'}),
    
    html.Div([dcc.Graph(figure=timeline_fig)], style={'width': '95%', 'margin': '0 auto', 'padding': '10px'}),
    
    html.H2("Top Performing Posts", style={'textAlign': 'center', 'marginTop': '40px'}),
    dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in top_posts_df.columns],
        data=top_posts_df.to_dict('records'),
        style_table={'overflowX': 'auto', 'width': '90%', 'margin': '0 auto'},
        style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'fontWeight': 'bold'},
        style_cell={
            'textAlign': 'left', 'padding': '10px', 'border': '1px solid grey',
            'maxWidth': '300px', 'overflow': 'hidden', 'textOverflow': 'ellipsis',
        },
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
        tooltip_data=[{col: {'value': str(val), 'type': 'markdown'} for col, val in row.items()} for row in top_posts_df.to_dict('records')],
        tooltip_duration=None,
        page_size=10,
        filter_action='native',
        sort_action='native'
    ),
    
    html.H2("All Posts Data", style={'textAlign': 'center', 'marginTop': '40px'}),
    dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in posts_df.columns],
        data=posts_df.to_dict('records'),
        style_table={'overflowX': 'auto', 'width': '95%', 'margin': '0 auto'},
        style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'fontWeight': 'bold'},
        style_cell={
            'textAlign': 'left', 'padding': '8px', 'border': '1px solid grey',
            'maxWidth': '200px', 'overflow': 'hidden', 'textOverflow': 'ellipsis',
        },
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
        tooltip_data=[{col: {'value': str(val), 'type': 'markdown'} for col, val in row.items()} for row in posts_df.to_dict('records')],
        tooltip_duration=None,
        page_size=300,
        filter_action='native',
        sort_action='native'
    )
], style={'fontFamily': 'Arial, sans-serif', 'padding': '20px', 'backgroundColor': '#f9f9f9'})

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
