import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the CSV file
file_path = 'FastFoodNutritionMenu_Cleaned.csv'
data = pd.read_csv(file_path)

# Extract unique fast food chains
unique_chains = data['Company'].unique()
chain_options = [{"label": chain, "value": chain} for chain in unique_chains]

# Dash App
app = dash.Dash(__name__)
server = app.server

# Layout
app.layout = html.Div([
    html.H1('Fast Food Comparison', style={'textAlign': 'center'}),
    html.Div([
        # Left half (Restaurant 1)
        html.Div([
            html.H3('Restaurant 1', style={'textAlign': 'center'}),
            dcc.Dropdown(id='chain-dropdown-1', options=chain_options, placeholder='Select Restaurant 1', searchable=True,
                         style={'backgroundColor': 'white', 'color': 'black'}),
            dcc.Dropdown(id='food-dropdown-1-1', placeholder='Select Food 1', searchable=True,
                         style={'backgroundColor': 'white', 'color': 'black'}),
            dcc.Dropdown(id='food-dropdown-1-2', placeholder='Select Food 2',
                         style={'backgroundColor': 'white', 'color': 'black'}),
            dcc.Dropdown(id='food-dropdown-1-3', placeholder='Select Food 3',
                         style={'backgroundColor': 'white', 'color': 'black'}),
            html.Div(id='info-1'),  # Placeholder for additional information
            dcc.Graph(id='graph-1', style={'display': 'none'}),  # Graph for Restaurant 1
        ], style={'width': '50%', 'display': 'inline-block', 'backgroundColor': '#1a1a1a', 'color': '#f0f0f0'}),
        # Right half (Restaurant 2)
        html.Div([
            html.H3('Restaurant 2', style={'textAlign': 'center'}),
            dcc.Dropdown(id='chain-dropdown-2', options=chain_options, placeholder='Select Restaurant 2', searchable=True,
                         style={'backgroundColor': 'white', 'color': 'black'}),
            dcc.Dropdown(id='food-dropdown-2-1', placeholder='Select Food 1', searchable=True,
                         style={'backgroundColor': 'white', 'color': 'black'}),
            dcc.Dropdown(id='food-dropdown-2-2', placeholder='Select Food 2',
                         style={'backgroundColor': 'white', 'color': 'black'}),
            dcc.Dropdown(id='food-dropdown-2-3', placeholder='Select Food 3',
                         style={'backgroundColor': 'white', 'color': 'black'}),
            html.Div(id='info-2'),  # Placeholder for additional information
            dcc.Graph(id='graph-2', style={'display': 'none'}),  # Graph for Restaurant 2
        ], style={'width': '50%', 'display': 'inline-block', 'backgroundColor': '#1a1a1a', 'color': '#f0f0f0'}),
    ]),
], style={'backgroundColor': '#1a1a1a', 'color': '#f0f0f0'})

# Callback to update food choices for Restaurant 1
@app.callback(
    [Output('food-dropdown-1-1', 'options'),
     Output('food-dropdown-1-2', 'options'),
     Output('food-dropdown-1-3', 'options')],
    Input('chain-dropdown-1', 'value')
)
def update_food_choices_1(selected_chain):
    food_choices = data[data['Company'] == selected_chain]['Item']
    options = [{"label": food, "value": food} for food in food_choices]
    return options, options, options

# Callback to update food choices for Restaurant 2
@app.callback(
    [Output('food-dropdown-2-1', 'options'),
     Output('food-dropdown-2-2', 'options'),
     Output('food-dropdown-2-3', 'options')],
    Input('chain-dropdown-2', 'value')
)
def update_food_choices_2(selected_chain):
    food_choices = data[data['Company'] == selected_chain]['Item']
    options = [{"label": food, "value": food} for food in food_choices]
    return options, options, options

# Callback to create visualization for Restaurant 1
@app.callback(
    [Output('graph-1', 'figure'),
     Output('info-1', 'children'),
     Output('graph-1', 'style')],
    Input('food-dropdown-1-1', 'value'),
    Input('food-dropdown-1-2', 'value'),
    Input('food-dropdown-1-3', 'value')
)
def create_visualization_1(*selected_foods):
    return create_visualization(selected_foods)

# Callback to create visualization for Restaurant 2
@app.callback(
    [Output('graph-2', 'figure'),
     Output('info-2', 'children'),
     Output('graph-2', 'style')],
    Input('food-dropdown-2-1', 'value'),
    Input('food-dropdown-2-2', 'value'),
    Input('food-dropdown-2-3', 'value')
)
def create_visualization_2(*selected_foods):
    return create_visualization(selected_foods)

def create_visualization(selected_foods):
    selected_foods = [food for food in selected_foods if food is not None]  # Filter out None values
    if not selected_foods:
        return dash.no_update, dash.no_update, {'display': 'none'}

    # Initialize a DataFrame to store the combined nutritional information
    combined_data = pd.DataFrame(columns=data.columns[2:])
    info_data = {label: 0 for label in ['Calories', 'Calories from Fat', 'Sodium(mg)', 'Cholesterol(mg)', 'Weight Watchers Points']}

    # Iterate through the selected foods and sum up the nutritional information
    for selected_food in selected_foods:
        food_data = data[data['Item'] == selected_food].iloc[:, 2:].copy()
        # Convert the values to numerical type
        food_data = food_data.apply(pd.to_numeric, errors='ignore')
        combined_data = combined_data.add(food_data, fill_value=0)
        for label in info_data.keys():
            value = food_data[label].values[0]
            info_data[label] += int(value) if isinstance(value, str) and value.isdigit() else value


    # Information to be removed from the chart
    info_labels = list(info_data.keys())

    # Removing the information from the labels and values for the chart
    labels = [col for col in combined_data.columns if col not in info_labels]
    values = [combined_data.iloc[0][label] for label in labels]

    # Creating a DataFrame for the donut chart
    graph_data = pd.DataFrame({
        'Nutritional Information': labels,
        'Value': values
    })

    # Creating the figure with a donut chart
    fig = px.pie(graph_data, names='Nutritional Information', values='Value',
                 hole=0.3, title='Combined Nutritional Information')

    # Customizing the background color
    fig.update_layout(
        paper_bgcolor="#abb5ba",  # Darker background for the plot
        plot_bgcolor="#abb5ba"    # Darker background for the plot
    )

    info_div = [html.Div(f"{label}: {value}") for label, value in info_data.items()]

    return fig, info_div, {'display': 'block'}  # Returning the figure and showing the graph

if __name__ == '__main__':
    app.run_server(debug=True)
