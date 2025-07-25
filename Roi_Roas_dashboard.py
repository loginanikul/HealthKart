# Import required libraries
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta


# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = "HealthKart - Influencer Campaign Analytics"

# Database connection parameters
username = 'root'
password = 'Anikul@2143'
host = 'localhost'
port = '3306'
database = 'Project'

# Create SQLAlchemy engine (with encoded password)
from urllib.parse import quote_plus
engine = create_engine(
    f"mysql+pymysql://{username}:{quote_plus(password)}@{host}:{port}/{database}"
)

# Function to execute SQL queries
def run_query(query):
    try:
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)
        return df
    except Exception as e:
        print(f"Database error: {e}")
        return pd.DataFrame()

# Calculate overall metrics
def calculate_overall_metrics():
    query = """
    SELECT
        SUM(t.revenue) AS total_revenue,
        SUM(py.total_payout) AS total_payout,
        SUM(t.revenue) - SUM(py.total_payout) AS net_profit,
        ROUND(SUM(t.revenue) / NULLIF(SUM(py.total_payout), 0), 2) AS roas,
        ROUND((SUM(t.revenue) - SUM(py.total_payout)) / NULLIF(SUM(py.total_payout), 0), 2) AS roi,
        SUM(t.orders) AS total_orders
    FROM tracking_data t
    JOIN payouts py ON t.influencer_id = py.influencer_id;
    """
    return run_query(query).iloc[0]

# Get data for visualizations
def get_campaign_data():
    query = """
    WITH campaign_data AS (
        SELECT
            t.campaign,
            SUM(t.revenue) AS campaign_revenue,
            SUM(py.total_payout) AS campaign_payout,
            SUM(t.revenue) * 0.15 AS estimated_baseline_revenue,
            SUM(t.orders) AS orders
        FROM tracking_data t
        JOIN payouts py ON t.influencer_id = py.influencer_id
        GROUP BY t.campaign
    )
    SELECT
        campaign,
        campaign_revenue,
        campaign_payout,
        estimated_baseline_revenue,
        campaign_revenue - estimated_baseline_revenue AS incremental_revenue,
        ROUND((campaign_revenue - estimated_baseline_revenue) / NULLIF(campaign_payout, 0), 2) AS incremental_roas
    FROM campaign_data;
    """
    return run_query(query)

def get_influencer_data():
    query = """
    SELECT
        i.id,
        i.name,
        i.platform,
        i.category,
        SUM(t.revenue) AS total_revenue,
        SUM(py.total_payout) AS total_payout,
        SUM(t.orders) AS total_orders,
        ROUND(SUM(t.revenue) / NULLIF(SUM(py.total_payout), 0), 2) AS roas,
        ROUND(SUM(py.total_payout) / NULLIF(SUM(t.orders), 0), 2) AS cost_per_order
    FROM influencers i
    JOIN tracking_data t ON i.id = t.influencer_id
    JOIN payouts py ON i.id = py.influencer_id
    GROUP BY i.id, i.name, i.platform, i.category;
    """
    return run_query(query)

def get_product_data():
    query = """
    SELECT
        t.product,
        i.platform,
        SUM(t.revenue) AS total_revenue,
        SUM(py.total_payout) AS total_payout,
        SUM(t.orders) AS total_orders,
        ROUND(SUM(t.revenue) / NULLIF(SUM(py.total_payout), 0), 2) AS roas
    FROM tracking_data t
    JOIN influencers i ON t.influencer_id = i.id
    JOIN payouts py ON t.influencer_id = py.influencer_id
    GROUP BY t.product, i.platform;
    """
    return run_query(query)

def get_trend_data():
    query = """
  SELECT
        DATE_FORMAT(t.date, '%%Y-%%m-01') AS month,
        SUM(t.revenue) AS total_revenue,
        SUM(py.total_payout) AS total_payout,
        ROUND(SUM(t.revenue) / NULLIF(SUM(py.total_payout), 0), 2) AS roas,
        COUNT(DISTINCT t.campaign) AS campaign_count
    FROM tracking_data t
    JOIN payouts py ON t.influencer_id = py.influencer_id
    GROUP BY month
    ORDER BY month;
    """
    return run_query(query)

# Get data
overall_metrics = calculate_overall_metrics()
campaign_df = get_campaign_data()
influencer_df = get_influencer_data()
product_df = get_product_data()
trend_df = get_trend_data()

# Convert month to datetime
if not trend_df.empty:
    trend_df['month'] = pd.to_datetime(trend_df['month']).dt.to_period('M').dt.to_timestamp()

# Create visualizations
def create_metric_card(title, value, delta=None, delta_type=None):
    return dbc.Card(
        dbc.CardBody([
            html.H5(title, className="card-title"),
            html.H3(f"{value}", className="card-value"),
            html.Div(f"{delta} {delta_type}", className="card-delta") if delta else None
        ]),
        className="metric-card"
    )

# Layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col(html.H1("HealthKart Influencer Campaign Performance", className="text-center my-4"), width=12)
    ]),
    
    # Overall Metrics
    dbc.Row([
        dbc.Col(create_metric_card("Total Revenue", f"${overall_metrics['total_revenue']:,.0f}"), md=3),
        dbc.Col(create_metric_card("Total Payout", f"${overall_metrics['total_payout']:,.0f}"), md=3),
        dbc.Col(create_metric_card("ROAS", f"{overall_metrics['roas']}x"), md=3),
        dbc.Col(create_metric_card("ROI", f"{overall_metrics['roi']*100:.0f}%", 
                                  f"{overall_metrics['roi']*100:.0f}%", 
                                  "increase" if overall_metrics['roi'] > 0 else "decrease"), md=3),
    ], className="mb-4"),
    
    # Charts and Graphs
    dbc.Row([
        # Campaign Performance
        dbc.Col([
            html.H4("Campaign Performance by Incremental ROAS", className="text-center mb-3"),
            dcc.Graph(
                id='campaign-roas-chart',
                figure=px.bar(
                    campaign_df.sort_values('incremental_roas', ascending=False),
                    x='campaign',
                    y='incremental_roas',
                    color='incremental_roas',
                    color_continuous_scale='RdYlGn',
                    labels={'incremental_roas': 'Incremental ROAS', 'campaign': 'Campaign'},
                    height=400
                ).update_layout(yaxis_title="Incremental ROAS")
            )
        ], md=6),
        
        # ROAS Trend
        dbc.Col([
            html.H4("ROAS Trend Over Time", className="text-center mb-3"),
            dcc.Graph(
                id='roas-trend-chart',
                figure=px.line(
                    trend_df,
                    x='month',
                    y='roas',
                    markers=True,
                    labels={'roas': 'ROAS', 'month': 'Month'},
                    height=400
                ).update_traces(line=dict(color='#4C78A8', width=3))
                .add_trace(go.Bar(
                    x=trend_df['month'],
                    y=trend_df['campaign_count'],
                    name='Campaigns',
                    yaxis='y2',
                    marker=dict(color='#F58518')
                )).update_layout(
                    yaxis=dict(title='ROAS'),
                    yaxis2=dict(title='Campaign Count', overlaying='y', side='right'),
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
                )
            )
        ], md=6)
    ], className="mb-4"),
    
    dbc.Row([
        # Top Influencers
        dbc.Col([
            html.H4("Top Performing Influencers", className="text-center mb-3"),
            dcc.Graph(
                id='influencer-roas-chart',
                figure=px.bar(
                    influencer_df.sort_values('roas', ascending=False).head(10),
                    x='name',
                    y='roas',
                    color='category',
                    labels={'roas': 'ROAS', 'name': 'Influencer', 'category': 'Category'},
                    height=400
                ).update_layout(yaxis_title="ROAS")
            )
        ], md=6),
        
        # Product Performance
        dbc.Col([
            html.H4("ROAS by Product and Platform", className="text-center mb-3"),
            dcc.Graph(
                id='product-roas-chart',
                figure=px.treemap(
                    product_df,
                    path=['product', 'platform'],
                    values='total_orders',
                    color='roas',
                    color_continuous_scale='RdYlGn',
                    labels={'roas': 'ROAS', 'total_orders': 'Orders'},
                    height=400
                )
            )
        ], md=6)
    ], className="mb-4"),
    
    # Detailed Data Tables
    dbc.Row([
        dbc.Col([
            html.H4("Campaign Details", className="text-center mb-3"),
            dash.dash_table.DataTable(
                id='campaign-table',
                columns=[{"name": i, "id": i} for i in campaign_df.columns],
                data=campaign_df.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
                page_size=10
            )
        ], md=6),
        
        dbc.Col([
            html.H4("Influencer Details", className="text-center mb-3"),
            dash.dash_table.DataTable(
                id='influencer-table',
                columns=[{"name": i, "id": i} for i in influencer_df.columns if i != 'id'],
                data=influencer_df.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
                page_size=10
            )
        ], md=6)
    ], className="mb-4"),
    
    # Filters
    dbc.Row([
        dbc.Col([
            html.H5("Filters", className="mb-3"),
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Date Range:"),
                            dcc.DatePickerRange(
                                id='date-range',
                                min_date_allowed=trend_df['month'].min(),
                                max_date_allowed=trend_df['month'].max() + timedelta(days=30),
                                start_date=trend_df['month'].min(),
                                end_date=trend_df['month'].max()
                            )
                        ], md=4),
                        dbc.Col([
                            html.Label("Platform:"),
                            dcc.Dropdown(
                                id='platform-filter',
                                options=[{'label': p, 'value': p} for p in influencer_df['platform'].unique()],
                                multi=True,
                                placeholder="Select Platforms"
                            )
                        ], md=4),
                        dbc.Col([
                            html.Label("Influencer Category:"),
                            dcc.Dropdown(
                                id='category-filter',
                                options=[{'label': c, 'value': c} for c in influencer_df['category'].unique()],
                                multi=True,
                                placeholder="Select Categories"
                            )
                        ], md=4)
                    ])
                ])
            ])
        ], width=12)
    ], className="mb-4")
], fluid=True)

# Add callbacks for filters
@app.callback(
    [Output('campaign-roas-chart', 'figure'),
     Output('influencer-roas-chart', 'figure'),
     Output('roas-trend-chart', 'figure'),
     Output('product-roas-chart', 'figure'),
     Output('campaign-table', 'data'),
     Output('influencer-table', 'data')],
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('platform-filter', 'value'),
     Input('category-filter', 'value')]
)
def update_dashboard(start_date, end_date, platforms, categories):
    # This is a placeholder - in a real app you would filter your data based on these inputs
    # For this demo, we'll return the original data
    return (
        px.bar(
            campaign_df.sort_values('incremental_roas', ascending=False),
            x='campaign',
            y='incremental_roas',
            color='incremental_roas',
            color_continuous_scale='RdYlGn'
        ).update_layout(yaxis_title="Incremental ROAS"),
        
        px.bar(
            influencer_df.sort_values('roas', ascending=False).head(10),
            x='name',
            y='roas',
            color='category'
        ).update_layout(yaxis_title="ROAS"),
        
        px.line(
            trend_df,
            x='month',
            y='roas',
            markers=True
        ).update_traces(line=dict(color='#4C78A8', width=3))
        .add_trace(go.Bar(
            x=trend_df['month'],
            y=trend_df['campaign_count'],
            name='Campaigns',
            yaxis='y2',
            marker=dict(color='#F58518')
        )).update_layout(
            yaxis=dict(title='ROAS'),
            yaxis2=dict(title='Campaign Count', overlaying='y', side='right')
        ),
        
        px.treemap(
            product_df,
            path=['product', 'platform'],
            values='total_orders',
            color='roas',
            color_continuous_scale='RdYlGn'
        ),
        
        campaign_df.to_dict('records'),
        influencer_df.to_dict('records')
    )

# Add custom CSS
app.css.append_css({
    'external_url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css'
})

app.css.append_css({
    'external_url': (
        "https://fonts.googleapis.com/css2?"
        "family=Roboto:wght@300;400;500;700&display=swap"
    )
})

app.css.append_css({
    'external_url': '/assets/custom.css'
})

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)