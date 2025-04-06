import pandas as pd
import numpy as np
import json
import requests
import dash
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
import dash_bootstrap_components as dbc
#import dash_core_components as dcc
from dash.dependencies import Input, Output
from sklearn.preprocessing import MinMaxScaler

#Getting the coordinates for the city
geojson_url = "https://www.donostia.eus/datuirekiak/baliabideak/mapa_auzoak/auzoak.json"
response = requests.get(geojson_url)
city_geojson = json.loads(response.content.decode('utf-8-sig'))


app = dash.Dash(external_stylesheets=[dbc.themes.MORPH, '/assets/style.css'])

#Read our data
df = pd.read_excel('modified_sensor_data.xlsx')

#variables we are going to use for elements of the layout
areas = df['Location'].unique()
areas_list = areas.tolist()
var_list = ['Luminosity', 'Temperature [°C]', 'Humidity [%]']

mean_luminosity=df.groupby('Location')['Luminosity'].mean()
mean_temperature=df.groupby('Location')['Temperature [°C]'].mean()
mean_humidity=df.groupby('Location')['Humidity [%]'].mean()

df_means=pd.DataFrame({'Luminosity': mean_luminosity,
                        'Temperature [°C]': mean_temperature,
                        'Humidity [%]': mean_humidity})
df_means.to_excel('mean_sensor_data.xlsx')
mean_df= pd.read_excel('mean_sensor_data.xlsx')
locs = mean_df['Location']

#data for pop_crime (we normalized)
demo = pd.read_excel('demografiaedadbarrio.xlsx')
deli = pd.read_excel('delitosbarrio.xlsx')
deli['demo'] = demo.groupby(['Location','Year'])['#People'].sum().values
scaler = MinMaxScaler()
deli[['demo', 'Delitos']] = scaler.fit_transform(deli[['demo', 'Delitos']])

#data for the rest of the analysis graphs (we normalized)
mean_df['crimes'] = [225,1262,190,2380,836,116,80] #data from city records
mean_df['income'] = [26191,21502,25522,25410,22475,23834,30474] #data from city records
demo = demo[demo['Year'] == 2023]
mean_df['population'] = demo.groupby('Location')['#People'].sum().values
mean_df['studies'] = [34.72,31.49,34.12,35.83,31.74,31.01,31.22] #data from city records
columns_to_normalize = ['Temperature [°C]','Humidity [%]', 'Luminosity','crimes','income','population','studies']
scaler = MinMaxScaler()
mean_df[columns_to_normalize] = scaler.fit_transform(mean_df[columns_to_normalize])

# we create thresholds to visualize better the data

df_thr = df
conditions = [(df_thr['Luminosity'] < 250), (df_thr['Luminosity'] > 249) & (df_thr['Luminosity'] < 256),
              (df_thr['Luminosity'] > 255) & (df_thr['Luminosity'] < 261), (df_thr['Luminosity'] > 260) & (df_thr['Luminosity'] < 266)
              , (df_thr['Luminosity'] > 265) & (df_thr['Luminosity'] < 271), (df_thr['Luminosity'] > 270) & (df_thr['Luminosity'] < 276)
              , (df_thr['Luminosity'] > 275) & (df_thr['Luminosity'] < 281), (df_thr['Luminosity'] > 280) & (df_thr['Luminosity'] < 286)
              , (df_thr['Luminosity'] > 285) & (df_thr['Luminosity'] < 291), (df_thr['Luminosity'] > 290)]
replace_values = ['Menor de 250' , '250 - 255', '255 - 260', '260 - 265', '265 - 270', '270 - 275', '275 - 280', 
                 '280 - 285', '285 - 290', 'Mayor de 290']
df['Threshold_ill'] = np.select(conditions, replace_values)

conditions = [(df_thr['Temperature [°C]'] > 10) & (df_thr['Temperature [°C]'] < 10.99),
              (df_thr['Temperature [°C]'] > 11) & (df_thr['Temperature [°C]'] < 11.99), (df_thr['Temperature [°C]'] > 12) & (df_thr['Temperature [°C]'] < 12.99), 
              (df_thr['Temperature [°C]'] > 13) & (df_thr['Temperature [°C]'] < 13.99), (df_thr['Temperature [°C]'] > 14) & (df_thr['Temperature [°C]'] < 15)]
replace_values = ['10º - 10.99º' ,'11º - 11.99º', '12º - 12.99º', '13º - 13.99º', '14º - 15º']
df['Threshold_temp'] = np.select(conditions, replace_values)

conditions = [(df_thr['Humidity [%]'] < 50), (df_thr['Humidity [%]'] > 49.99) & (df_thr['Humidity [%]'] < 53), 
              (df_thr['Humidity [%]'] > 52.99) & (df_thr['Humidity [%]'] < 56),(df_thr['Humidity [%]'] > 55.99) & (df_thr['Humidity [%]'] < 59)
              , (df_thr['Humidity [%]'] > 58.99) & (df_thr['Humidity [%]'] < 62), (df_thr['Humidity [%]'] > 61.99) & (df_thr['Humidity [%]'] < 65)
              , (df_thr['Humidity [%]'] > 64.99) & (df_thr['Humidity [%]'] < 68.01), (df_thr['Humidity [%]'] > 68)]
replace_values = ['Menor a 50', '50 - 52.99' , '53 - 55.99º', '56º - 58.99', '59º - 61.99', '62 - 64.99', 
                  '65 - 68', 'Mayor a 68']
df['Threshold_hum'] = np.select(conditions, replace_values)

lum_list = df_thr['Luminosity'].unique()
temp_list = df_thr['Temperature [°C]'].unique()
hum_list = df_thr['Humidity [%]'].unique()

illumination = df['Luminosity']
temperature = df['Temperature [°C]']


app.layout = html.Div([
    html.Br(),
    dbc.Row([
            dbc.Col([
                html.H1('SAN SEBASTIAN IN THE WILD', style={'font-size':'60px', 'text-align': 'center'})
                ]),
        ]),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Data Collected', value='tab-1', children=[
            html.Div([      
html.Br(),
dbc.Row([
    dbc.Col([
        
        dbc.Row([
            
            dcc.Dropdown(
                id = 'drop1',
                options=[{'label': str(option), 'value': option} for option in areas_list],
                multi = False, 
                placeholder = 'SELECT...',
                style={'width': '500px', 'color': 'blue', 'background-color': 'lightgray',  'margin': 'auto', 'border': 'none'},
                value=areas_list[0],
                className='my-dropdown'
                )
            ]),
        dbc.Row([
            dcc.Graph(id = 'graph_illumination', style={'padding-top': '2px'})
            ]),
        ], width=4),
    dbc.Col([
        dbc.Row([
            dcc.Graph(id = 'graph_temp', style={'padding-top': '38px'})
            ]),
        ], width=4),   
    dbc.Col([
        dbc.Row([
            dcc.Graph(id = 'graph_hum', style={'padding-top': '38px'})
            ])
        ], width=4),
    dbc.Col([
        dbc.Row([
            dcc.Graph(id = 'graph_illumination_2')
            ]),
        dbc.Row([
            dcc.RangeSlider(
                id='slider1',
                min=lum_list.min(),
                max=lum_list.max(),
                step=1,
                marks={lum_list.min().tolist(): str(lum_list.min()), lum_list.max().tolist(): str(lum_list.max())},
                value=[lum_list.min(), lum_list.max()],
                className='slider1'
                )
            ]),
        ], width=4),
    dbc.Col([
        dbc.Row([
            dcc.Graph(id = 'graph_temp_2')
            ]),
      dbc.Row([
          dcc.RangeSlider(
              id='slider2',
              min=temp_list.min(),
              max=temp_list.max(),
              step=0.1,
              marks={10: '10', 15: '15'},
              value=[temp_list.min(), temp_list.max()],
              allowCross=False,
                className='slider2'

              )
          ]),
      ], width=4),
    dbc.Col([
        dbc.Row([
            dcc.Graph(id = 'graph_hum_2')
            ]),
      dbc.Row([
          dcc.RangeSlider(
              id='slider3',
              min=hum_list.min(),
              max=hum_list.max(),
              step=1,
              marks={hum_list.min().tolist(): str(hum_list.min()), hum_list.max().tolist(): str(hum_list.max())},
              value=[hum_list.min(), hum_list.max()],
                className='slider3'

              )
          ])
      ], width=4)

                    ]),
                ]),
            ]),
        dcc.Tab(label='Analysis', value='tab-2', children=[
            html.Div([
                dbc.Row([
                    dbc.Col([
                      
                      dcc.Dropdown(
                          id = 'drop2',
                          options=[{'label': str(option), 'value': option} for option in var_list],
                          multi = False, 
                          placeholder = 'SELECT...',
                          style={'width': '500px', 'color': 'blue', 'background-color': 'lightgray',  'margin': 'auto', 'border': 'none'},
                          value=var_list[0]
                          )  
                      
                    ]),
                ]),
                dbc.Row([
                    dbc.Col([
                        
                        dcc.Graph(id = 'crimes')
                        
                        ], width=6),
                    dbc.Col([
                        
                        dcc.Graph(id = 'population')
                        
                        ], width=6)
                    ]),
                dbc.Row([
                    dbc.Col([
                        
                        dcc.Graph(id = 'income')
                        
                        ], width=6),
                    dbc.Col([
                        
                        dcc.Graph(id = 'studies')
                        
                        ], width=6)
                    ]),
                dbc.Row([
                    dbc.Col([
                        dcc.Dropdown(
                            id = 'drop3',
                            options=[{'label': str(option), 'value': option} for option in areas_list],
                            multi = False, 
                            placeholder = 'SELECT...',
                            style={'width': '500px', 'color': 'blue', 'background-color': 'lightgray',  'margin': 'auto', 'border': 'none'},
                            value=areas_list[0]
                            )
                        ])
                    ]),
                dbc.Row([
                    dbc.Col([dcc.Graph(id = 'pop_crime'),
                             ], width=6),
                    dbc.Col([dcc.Graph(
            id='scatter-plot',
        )], width=6)
                    ]),
            ])
        ]),
        dcc.Tab(label='Map', value='tab-3', children=[
            html.Div([
                dcc.RadioItems(
        id='radio',
        options=[
            {'label': 'Luminosity', 'value': 'Luminosity',},
            {'label': 'Temperature [°C]', 'value': 'Temperature [°C]'},
            {'label': 'Humidity', 'value': 'Humidity [%]'}
        ],
        value='Luminosity',
        labelStyle={'display': 'inline-block'}, 
        className='radio'

    ),
    dcc.Graph(id='choropleth-map')
                ])
            ]
            
            )
    ]),
])

@app.callback(
    Output(component_id='graph_illumination', component_property='figure'),
    Output(component_id='graph_temp', component_property='figure'),
    Output(component_id='graph_hum', component_property='figure'),
    Output(component_id='graph_illumination_2', component_property='figure'),
    Output(component_id='graph_temp_2', component_property='figure'),
    Output(component_id='graph_hum_2', component_property='figure'),
    Output(component_id='crimes', component_property='figure'),
    Output(component_id='population', component_property='figure'),
    Output(component_id='income', component_property='figure'),
    Output(component_id='studies', component_property='figure'),
    Output(component_id='pop_crime', component_property='figure'),
    Output(component_id='scatter-plot', component_property='figure'),
    Input(component_id='drop1', component_property='value'),
    Input(component_id='slider1', component_property='value'),
    Input(component_id='slider2', component_property='value'),
    Input(component_id='slider3', component_property='value'),
    Input(component_id='drop2', component_property='value'),
    Input(component_id='drop3', component_property='value'),
)
def update_graphs(selected_area1, lum_range, temp_range, hum_range, selected_op, selected_area2):#, selected_thr1, selected_thr2, selected_thr3, selected_area3):
    
    df_loc = df[(df['Location'] ==  selected_area1)] 
    
    value_counts = df_loc['Threshold_ill'].value_counts()

    fig_illu = px.pie(names=value_counts.index, values=value_counts.values, 
            title = 'Luminosity Data', hole = 0.2,
            color_discrete_sequence = ['#2a3e4b',  '#4cbbb3',  '#dcdfd8',  
            '#8f9c9d',  '#3d6f6d',  '#5a5f4e',  '#70d0cc',  '#428c7c',  '#44546c', '#248c84'])
    fig_illu.update_layout(showlegend=True)
    
    value_counts = df_loc['Threshold_temp'].value_counts()
    fig_temp = px.pie(names=value_counts.index, values=value_counts.values,
               title = 'Temperature Data [°C]', hole = 0.2,
               color_discrete_sequence = ['#ee7676',  '#f29090',  '#fdcdcd', 
            '#abbfbf',  '#9bbbbb',  '#ffcece',  '#f18b8b']
                      )
    
    value_counts = df_loc['Threshold_hum'].value_counts()
    fig_hum = px.pie(names=value_counts.index, values=value_counts.values,
              title = 'Humidity Data [%]', hole = 0.2,
              color_discrete_sequence = ['#c7522a',  '#d68a58',  '#e5c185',  
            '#f0daa5',  '#fbf2c4',  '#b8cdab', '#74a892',  '#3a978c']       
                     )
    selected_rows_lum = df_loc[(df_loc['Luminosity'] >= lum_range[0]) & (df_loc['Luminosity'] <= lum_range[1])]
    fig_illu_2 = px.histogram(selected_rows_lum, x='Luminosity',
                              title = 'Luminosity Range',
                              color_discrete_sequence = ['#2a3e4b',  '#4cbbb3',  '#dcdfd8',  
                              '#8f9c9d',  '#3d6f6d',  '#5a5f4e',  '#70d0cc',  '#428c7c',  '#44546c', '#248c84'])
    
    selected_rows_temp = df_loc[(df_loc['Temperature [°C]'] >= temp_range[0]) & (df_loc['Temperature [°C]'] <= temp_range[1])]
    fig_temp_2 = px.histogram(selected_rows_temp, x='Temperature [°C]',
                              title = 'Temperature Range [°C]',
                              color_discrete_sequence = ['#ee7676',  '#f29090',  '#fdcdcd', 
                           '#abbfbf',  '#9bbbbb',  '#ffcece',  '#f18b8b']
                              )
    
    selected_rows_hum = df_loc[(df_loc['Humidity [%]'] >= hum_range[0]) & (df_loc['Humidity [%]'] <= hum_range[1])]
    fig_hum_2 = px.histogram(selected_rows_hum, x='Humidity [%]',
                              title = 'Humidity Range [%]',
                              color_discrete_sequence = ['#c7522a',  '#d68a58',  '#e5c185',  
                            '#f0daa5',  '#fbf2c4',  '#b8cdab', '#74a892',  '#3a978c']
                              )
    
    mean_df_alt = mean_df.sort_values(by='crimes', ascending=True)
    crimes = px.bar(mean_df_alt, x='Location', y=[selected_op, 'crimes'], 
                    color_discrete_map={'selected_op': '#2a3e4b', 'crimes': '#d57500'},
              barmode='group', labels={'value': 'Value', 'location': 'Location'},
              title="{} {}".format(selected_op, 'and Crimes by Location'))
    
    mean_df_alt = mean_df.sort_values(by='population', ascending=True)
    population = px.bar(mean_df_alt, x='Location', y=[selected_op, 'population'], 
                        color_discrete_map={'selected_op': '#2a3e4b', 'population': '#2a3e4b'},
               barmode='group', labels={'value': 'Value', 'location': 'Location'},
               title= "{} {}".format(selected_op, 'and Population by Location'))
    
    mean_df_alt = mean_df.sort_values(by='income', ascending=True)
    income = px.bar(mean_df_alt, x='Location', y=[selected_op, 'income'], 
                    color_discrete_map={'selected_op': '#70d0cc', 'income': '#74a892'},
               barmode='group', labels={'value': 'Value', 'location': 'Location'},
               title= "{} {}".format(selected_op, 'and Income by Location'))
    
    mean_df_alt = mean_df.sort_values(by='studies', ascending=True)
    studies = px.bar(mean_df_alt, x='Location', y=[selected_op, 'studies'], 
                     color_discrete_map={'selected_op': '#2a3e4b', 'studies': '#f29090'},
               barmode='group', labels={'value': 'Value', 'location': 'Location'},
               title="{} {}".format(selected_op, 'and Studies by Location'))
    
    pop_crime = px.line(deli[deli['Location'] == selected_area2], x='Year', y=['demo', 'Delitos'], 
              labels={'value': 'Value', 'location': 'Location'},
              title='Population and Crime Evolution')
    
    light_temp = px.scatter(df[df['Location'] == selected_area2], x='Luminosity', y='Temperature [°C]',
              labels={'x': 'Illumination', 'y': 'Temperature', 'location': 'Location'},
              title=f'Correlation of Illumination and Temperature in {selected_area2}'
              )
    
    
    return fig_illu, fig_temp, fig_hum, fig_illu_2, fig_temp_2, fig_hum_2, crimes, population, income, studies, pop_crime, light_temp


@app.callback(
    Output('choropleth-map', 'figure'),
    Input('radio', 'value')
)
def update_map(radio_value):
    neighborhoods_to_display = ['MIRAMON - ZORROAGA', 'IBAETA', 'ANTIGUA', 'AIETE','AMARABERRI','GROS','ERDIALDEA']

    for loc in city_geojson['features']:
            neighborhood_name = loc['properties']['name']
            if neighborhood_name in neighborhoods_to_display:
                    loc['id'] = loc['properties']['name']  
                    

    fig = go.Figure(go.Choroplethmapbox(
            geojson=city_geojson,
            locations=locs,
            z=mean_df[radio_value],
            colorscale='Viridis',
            colorbar_title=radio_value))
                    
                    

    fig.update_layout(mapbox_style="carto-positron",
        mapbox_zoom=11,  #se acerca o aleja del mapbox_center. 
        mapbox_center = {"lat":  43.312691, "lon": -1.993332})  #Datos de Donosti
   
    return fig

if __name__ == '__main__':
    app.run_server(port=8051)
    