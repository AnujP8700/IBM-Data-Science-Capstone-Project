# Importing required libraries

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Loading the dataset into a pandas dataframe

url = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv'
spacex_df = pd.read_csv(url, index_col = 0)
spacex_df.head()

max_payload = ((spacex_df['Payload Mass (kg)'].max()//2500)+1)*2500
min_payload = int(spacex_df['Payload Mass (kg)'].min())

options = [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]
options.append({'label': 'All Sites', 'value': 'All Sites'})

# Creating a Dash application

app = dash.Dash(__name__)

app.layout = html.Div(children = [html.H1('SpaceX Launch Records Dashboard',
                                          style = {'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
                                html.Br(),
                                
                                # Task 1: Add a dropdown list to enable launch site selection
                                html.Div(dcc.Dropdown(id = 'site-dropdown',
                                                      options = options,
                                                      placeholder = 'Select a site',
                                                      value = 'All Sites',
                                                      )),#style = {'width': '80%', 'padding': '3px', 'font-size': 25, 'textAlign': 'center'})),
                                html.Br(),

                                # Task 2: Add a pie chart to show total successfull launch count for all sites
                                # If a specific launch site is selected, then show the success vs failure count for the site
                                html.Div(
                                    dcc.Graph(id = 'success-pie-chart')),
                                html.Br(),

                                html.P('Payload Range (Kg):'),
                                # Task 3: Add a slider to select payload range
                                dcc.RangeSlider(id = 'payload-slider',
                                                min = min_payload, 
                                                max = max_payload, 
                                                step = 2500,
                                                value = [min_payload, max_payload],
                                                marks = {i: f'{i:.0f}' for i in range(min_payload, 10000 + 1, 2500)}),
                                html.Br(),

                                # Task 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id = 'success-payload-scatter-chart')),

])

# Task 2: Add a callback function for 'site-dropdown' as input, 'success-pie-chart' as output
@app.callback(Output(component_id = 'success-pie-chart', component_property = 'figure'),
               Input(component_id = 'site-dropdown', component_property = 'value'))

def generate_pie(site):
    if site == 'All Sites':
        success_pie_df = spacex_df.groupby('Launch Site', as_index = False)['class'].sum()
        fig = px.pie(success_pie_df, values = 'class', names = 'Launch Site')
        fig.update_layout(title = {'text': 'Total Success Launches by Site', 'x': 0.005, 'y': 0.98, 'xanchor': 'left', 'yanchor': 'top'})
        return fig
    else:
        pie_df = spacex_df[spacex_df['Launch Site'] == site]
        pie_df = pie_df.groupby('class', as_index = True)['class'].count()
        pie_df = pie_df.to_frame()
        pie_df.rename(columns = {'class': 'count'}, inplace = True)
        pie_df.reset_index(inplace = True)
        pie_df['class'].replace({0: 'Failure', 1: 'Success'}, inplace = True)
        fig = px.pie(pie_df, names = 'class', values = 'count')
        fig.update_layout(title = {'text': 'Success vs Failure for ' + site + 'Site', 'x': 0.005, 'y': 0.98, 'xanchor': 'left', 'yanchor': 'top'})
        return fig
    
# Task 4: Add a calback function for 'site-dropdown' and 'payload-slider' as inputs and 'success-payload-scatter-chart' as output
@app.callback(Output(component_id = 'success-payload-scatter-chart', component_property = 'figure'),
               [Input(component_id = 'site-dropdown', component_property = 'value'),
                Input(component_id = 'payload-slider', component_property = 'value')])

def generate_scatter(site, range_):
    min_weight = range_[0]
    max_weight = range_[1]
    scatter_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_weight) & (spacex_df['Payload Mass (kg)'] <= max_weight)]
    if site == 'All Sites':
        fig = px.scatter(scatter_df, 
                    x = 'Payload Mass (kg)', 
                    y = 'class',
                    color = 'Booster Version Category' 
                    )
        fig.update_layout(title = {'text': 'Correlation between Payload and Success for All Sites', 'x': 0.005, 'y': 0.98, 'xanchor': 'left', 'yanchor': 'top'},)
        fig.update_xaxes(tickformat = 'd')
        return fig
    else:
        scatter_df = scatter_df[scatter_df['Launch Site'] == site]
        fig = px.scatter(scatter_df, x = 'Payload Mass (kg)', y = 'class', color = 'Booster Version Category')
        fig.update_layout(title = {'text': 'Correlation between Payload and Success for ' + site, 'x': 0.005, 'y': 0.98, 'xanchor': 'left', 'yanchor': 'top'})
        fig.update_xaxes(tickformat = 'd')
        return fig
    
if __name__ == '__main__':
    app.run_server()
