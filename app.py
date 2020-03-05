from dash.dependencies import Input, Output
from pandas.io.json import json_normalize
from wowapi import WowApi

import base64
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


##### Getting into the API and data
def get_Data(client_ID, secret_key, raid, faction):
    """Function to use a given api client ID and secret key, which returns separate dataframes depending on certain features"""
    
    # API Key
    api = WowApi(client_ID, secret_key)
    
    # Get Raid Data
    mythic_raid_leaderboard = api.get_mythic_raid_leaderboard('us', 'dynamic-us', raid, faction)
    mythic_raid_leaderboard_json = mythic_raid_leaderboard['entries']
    
    # Convert to CSV
    df = json_normalize(mythic_raid_leaderboard_json)
    
    # Data Preprocessing
    ## Obtain the date from epoch
    df['Date'] =  pd.to_datetime(df['timestamp'], unit = 'ms')

    ## Drop Columns
    drop_cols = ['guild.name','region',  'guild.realm.name.en_US',  'faction.type' , 'Date', 'rank']
    df = df[drop_cols]

    ## Rename Columns
    rename_Columns = {'guild.name': 'Guild', 'region': 'Region',
                      'guild.realm.name.en_US': 'Realm', 'faction.type': 'Faction',
                      'rank': 'Rank'}
    df.rename(columns = rename_Columns, inplace = True)

    ## Changing values in columns
    df['Region'] = df['Region'].map({'us': 'US', 'eu': 'EU', 'cn': 'CN', 'kr': 'KR', 'tw': 'TW'})
    
    return df


############### Datatable
def datatable_leaderboards(raid_data, color, border, header):
    datatable = dash_table.DataTable( 
                id = 'typing_formatting_1',
                data = raid_data.to_dict('records'),
                columns =
                [
                    {
                        'id': 'Guild',
                        'name': 'Guild',
                        'type': 'text'
                    }, 

                    {
                        'id': 'Region',
                        'name': 'Region',
                        'type': 'text'
                    }, 

                    {
                        'id': 'Realm',
                        'name': 'Realm',
                        'type': 'text'
                    }, 

                    {
                        'id': 'Date',
                        'name': 'Date',
                        'type': 'text'
                    }, 

                    {
                        'id': 'Rank',
                        'name': 'Rank',
                        'type': 'numeric',
                    },  

                ],

    ### Highlight Cells based on conditions - first, second, and third row
                style_data_conditional =
                [
                    {
                        "if": {"row_index": 0},
                        "backgroundColor": "#FFD700",
                        'color': 'black'

                },

                    {
                        "if": {"row_index": 1},
                        "backgroundColor": "#C0C0C0",
                        'color': 'black'

                    },

                    {
                        "if": {"row_index": 2},
                        "backgroundColor": "#CD7F32",
                        'color': 'black'

                    }
                ],

    ### Formatting the data/headers cells
                style_cell = {'backgroundColor': color, 'font-family': 'helvetica' },

                style_data = {'border': border,
                              'font-size': 18, 'font-family': 'helvetica' 
                             },

                style_header = { 'border': header,
                               'font-size': 21, 'font-family': 'helvetica' 
                               },
                editable = True,
                filter_action = "native",
                sort_action = "native",
                sort_mode = "multi",
                column_selectable = "single",
                row_selectable = "multi",
                row_deletable = True,
                selected_columns = [],
                selected_rows = [],
                page_action = "native",
                page_current = 0,
                page_size = 100,
            )
    return datatable


################# Bar Plots
def bar_cluster(df, x, code, title, xaxis):
    """Function to create a histogram."""
    bar = px.histogram(df, x,
                 color = code,
                 color_discrete_sequence =  px.colors.qualitative.Pastel)
    
    bar.update_xaxes(showline = True, linewidth = 1, linecolor = 'black', 
                          mirror = True, gridcolor = 'LightPink', automargin = True, 
                          zeroline = True, zerolinewidth = 2, zerolinecolor = 'LightPink', 
                          ticks = "outside", tickwidth = 2, tickcolor = 'black', ticklen = 10,
                          title = xaxis, title_font  =  dict(size  =  16)) 
    bar.update_yaxes(showline = True, linewidth = 2, linecolor = 'black', 
                          mirror = True, gridcolor = 'LightPink',
                          zeroline = True, zerolinewidth = 1, zerolinecolor = 'LightPink', 
                          ticks = "outside", tickwidth = 2, tickcolor = 'black', ticklen = 10,
                          title = 'Number of Guilds', title_font  =  dict(size  =  16))
    
    
    bar.update_layout(
        title = title,
        title_font  =  dict(size  =  20),
        legend = dict(
            x = 1,
            y = 1,
            traceorder = "normal",
            font = dict(
                family = "sans-serif",
                size = 14,
                color = "black"
            ),
            bgcolor = "#e5ecf6",
            bordercolor = "Black",
            borderwidth = 2
        )
    )
    return bar




######################## Time series
def timeseries(df, x, y, code, title, xaxis):
    "Function to create a time series plot."
    ts = px.line(df, x, y, 
                 color = code,
                 color_discrete_sequence =  px.colors.qualitative.Pastel)
    
    ts.update_xaxes(showline = True, linewidth = 1, linecolor = 'black', 
                          mirror = True, gridcolor = 'LightPink', automargin = True, 
                          zeroline = True, zerolinewidth = 2, zerolinecolor = 'LightPink', 
                          ticks = "outside", tickwidth = 2, tickcolor = 'black', ticklen = 10,
                          title = xaxis, title_font  =  dict(size  =  16)) 
    ts.update_yaxes(showline = True, linewidth = 2, linecolor = 'black', 
                          mirror = True, gridcolor = 'LightPink',
                          zeroline = True, zerolinewidth = 1, zerolinecolor = 'LightPink', 
                          ticks = "outside", tickwidth = 2, tickcolor = 'black', ticklen = 10,
                          title = 'Rank', title_font  =  dict(size  =  16))
    
    ts.update_traces(marker = dict(size = 10,
                                   line = dict(width = 2,
                                             color = 'DarkSlateGrey')), mode = 'markers')

    ts.add_trace(
        go.Scatter(
            x = x ,
            y = y,
            mode = "lines",
            line = go.scatter.Line(color = '#67093A'),
            showlegend = False)
)
    
    
    ts.update_layout(
        title = title,
        title_font  =  dict(size  =  20),
        legend = dict(
            x = 1,
            y = 1,
            traceorder = "normal",
            font = dict(
                family = "sans-serif",
                size = 14,
                color = "black"
            ),
            bgcolor = "#e5ecf6",
            bordercolor = "Black",
            borderwidth = 2
        )
    )
    return ts


##### Dataframes
# Call in various dataframe leaderboards

uldir_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
         raid = 'uldir', faction = 'alliance')

uldir_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
         raid = 'uldir', faction = 'horde')

BOD_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
         raid = 'battle-of-dazaralor', faction = 'alliance')

BOD_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
         raid = 'battle-of-dazaralor', faction = 'horde')

COS_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
         raid = 'crucible-of-storms', faction = 'alliance')

COS_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
         raid = 'crucible-of-storms', faction = 'horde')

TEP_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
         raid = 'the-eternal-palace', faction = 'alliance')

TEP_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
         raid = 'the-eternal-palace', faction = 'horde')

NTWC_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
         raid = 'nyalotha-the-waking-city', faction = 'alliance')

NTWC_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
         raid = 'nyalotha-the-waking-city', faction = 'horde')



## Importing Logo and encoding it
image1_filename = 'assets/logo.jpg' 
encoded_image1 = base64.b64encode(
    open(image1_filename, 'rb').read())

image2_filename = 'assets/ally_logo.jpg' 
encoded_image2 = base64.b64encode(
    open(image2_filename, 'rb').read())

image3_filename = 'assets/horde_logo.jpg' 
encoded_image3 = base64.b64encode(
    open(image3_filename, 'rb').read())



############################### DASHBOARD ###################



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Set server for web app
server = app.server
app.config['suppress_callback_exceptions'] = True


# Define layout of the app 
app.layout = html.Div([
    html.Div(
        [
            html.Div(id = 'background_image', 
                            
             style = {'display': 'flex', 'align-items': 'center',
                                 'justify-content': 'center'},
                    ),
            
                     html.H1('World of Warcraft: Battle For Azeroth Mythic Raid Dashboard'),
        ], style = {"border-bottom": "2px black ridge"}
    ),
    
    html.Div([
        dcc.Dropdown(
            id = 'Raids',
            options = [
                {'label': 'Uldir', 'value': 'U'},
                {'label': 'Battle of Dazar''alor', 'value': 'BOD'},
                {'label': 'Crucible of Storms', 'value': 'COS'},
                {'label': 'The Eternal Palace', 'value': 'TEP'},
                {'label': 'Ny''alotha, the Waking City', 'value': 'NTWC'},
            ],
            value = 'Raids',
            placeholder = "Select a Raid",
        ),
        
        dcc.Tabs(
            id = "tabs-with-classes",
            value = 'tab-2',
            parent_className = 'custom-tabs',
            className = 'custom-tabs-container',
            children = [
                dcc.Tab(
                    label = 'Alliance',
                    value = 'tab-1-example',
                    className = 'custom-tab',
                    selected_className = 'custom-tab--selected'
                ),
                dcc.Tab(
                    label = 'Horde',
                    value = 'tab-2-example',
                    className = 'custom-tab',
                    selected_className = 'custom-tab--selected'
                
                ),
            ], 
        # Colors for Tabs    
            colors={
                "border": '#D9DBDE',
                "primary": "gold",
                "background": "cornsilk"
            }
        
        
        ),
        
        html.H1('Leaderboard'),
        
        html.Div(id = 'tabs-content-classes'),
    
    ]
    ),
    
    html.Div(className = 'row', children = 
             [
                 html.Div(
                     [
                         dcc.Graph(id = 'Region' ),
                     ], style = {'backgroundColor': '#FFFFFF'}, className = 'six columns'
                 ),
                 html.Div(
                     [
                         dcc.Graph(id = 'Realm'),
                     ], style = {'backgroundColor': '#FFFFFF'}, className = 'six columns'
                 ),
             ], style = {'backgroundColor': '#FFFFFF'}
            ),
    
    html.Div(
        [
            dcc.Graph(id = 'Time series'),
        ], style = {'backgroundColor': '#FFFFFF'}
    ),
], style = {'backgroundColor': '#D9DBDE', 'font-family': 'helvetica'}

)


  
  
    

### Dynamically changes the background image depending on what user inputs    
@app.callback(
    Output('background_image', 'children'),
    [Input(component_id = 'tabs-with-classes', component_property = 'value'),]
)

def render_image(tab):
    if tab == 'tab-1-example':
        return html.Img(src = 'data:image/png;base64,{}'
                             .format(encoded_image2.decode()))
    elif tab == 'tab-2-example':
        return html.Img(src = 'data:image/png;base64,{}'
                             .format(encoded_image3.decode()))
    else:
        return html.Img(src = 'data:image/png;base64,{}'
                             .format(encoded_image1.decode()))
    return html.Img(src = 'data:image/png;base64,{}'
                             .format(encoded_image1.decode()))
    


### Dynamically changes the datatable depending on what user inputs    
@app.callback(
    Output('tabs-content-classes', 'children'),
    [Input(component_id = 'tabs-with-classes', component_property = 'value'),
    Input(component_id = 'Raids', component_property = 'value'),]
)
    
def render_datatable(tab, raids):
    # Tab 1
    if (tab == 'tab-1-example') & (raids == 'U') :
        
        uldir_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'uldir', faction = 'alliance')
    
        data = uldir_alliance
        
        return datatable_leaderboards(data, '#95BFFF', '1px solid gold', '1px solid gold')
    
    elif (tab == 'tab-1-example') & (raids == 'BOD') :
        
        BOD_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'battle-of-dazaralor', faction = 'alliance')
        
        data = BOD_alliance
        
        return datatable_leaderboards(data, '#95BFFF', '1px solid gold', '1px solid gold')
    
    elif (tab == 'tab-1-example') & (raids == 'COS') :
        
        COS_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'crucible-of-storms', faction = 'alliance')
        
        data = COS_alliance
        
        return datatable_leaderboards(data, '#95BFFF', '1px solid gold', '1px solid gold')
    
    elif (tab == 'tab-1-example') & (raids == 'TEP') :
        
        TEP_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'the-eternal-palace', faction = 'alliance')
        
        data = TEP_alliance
        
        return datatable_leaderboards(data, '#95BFFF', '1px solid gold', '1px solid gold')

    elif (tab == 'tab-1-example') & (raids == 'NTWC') :
        
        NTWC_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'nyalotha-the-waking-city', faction = 'alliance')
        
        data = NTWC_alliance
        
        return datatable_leaderboards(data, '#95BFFF', '1px solid gold', '1px solid gold' )
    
    # Tab 2
    elif (tab == 'tab-2-example') & (raids == 'U') :
        
        uldir_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'uldir', faction = 'horde')
        
        data = uldir_horde
        
        return datatable_leaderboards(data, '#FF959F', '1px solid blue', '1px solid blue')
    
    elif (tab == 'tab-2-example') & (raids == 'BOD') :
        
        BOD_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'battle-of-dazaralor', faction = 'horde')
        
        data = BOD_horde
        
        return datatable_leaderboards(data, '#FF959F', '1px solid blue', '1px solid blue')
    
    elif (tab == 'tab-2-example') & (raids == 'COS') :
        
        COS_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'crucible-of-storms', faction = 'horde')
        
        data = COS_horde
        
        return datatable_leaderboards(data, '#FF959F', '1px solid blue', '1px solid blue')

    elif (tab == 'tab-2-example') & (raids == 'TEP') :
        
        TEP_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'the-eternal-palace', faction = 'horde')
        
        data = TEP_horde
        
        return datatable_leaderboards(data, '#FF959F', '1px solid blue', '1px solid blue')
    
    elif (tab == 'tab-2-example') & (raids == 'NTWC') :
        
        NTWC_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'nyalotha-the-waking-city', faction = 'horde')
        
        data = NTWC_horde
        
        return datatable_leaderboards(data, '#FF959F', '1px solid blue', '1px solid blue')
    
    return 'Select a faction and raid'

    
    
### Plots



### Dynamically updates the region plot given the user inputs

@app.callback(
    Output('Region', 'figure'),
    
    [Input( 'tabs-with-classes', 'value'),
    Input( 'Raids', 'value'),]
    
    
)

    
def callback_region(tab, raids):
    """Returns 3D Plots of the Clusters based on which method was selected"""
    
    # Tab 1
    if (tab == 'tab-1-example') & (raids == 'U') :
        
        uldir_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'uldir', faction = 'alliance')
    
        data = uldir_alliance
        
        sorted_freq_region = data.assign(freq = data.groupby('Region')['Region'].transform('count'))\
        .sort_values(by = ['freq','Region'],ascending = [False,True]).loc[:,['Region']]
        
        uldir_alliance_region = bar_cluster(df = sorted_freq_region, x = 'Region',
                        code = 'Region'  , title = 'Distribution of Regions', xaxis = 'Region')
        
        figure = uldir_alliance_region
        
        return figure
    
    elif (tab == 'tab-1-example') & (raids == 'BOD') :
        
        BOD_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'battle-of-dazaralor', faction = 'alliance')
        
        data = BOD_alliance

        sorted_freq_region = data.assign(freq = data.groupby('Region')['Region'].transform('count'))\
        .sort_values(by = ['freq','Region'],ascending = [False,True]).loc[:,['Region']]
        
        BOD_alliance_region = bar_cluster(df = sorted_freq_region, x = 'Region',
                        code = 'Region'  , title = 'Distribution of Regions', xaxis = 'Region')
        
        figure = BOD_alliance_region 
        
        return figure
    
    elif (tab == 'tab-1-example') & (raids == 'COS') :
        
        COS_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'crucible-of-storms', faction = 'alliance')
        
        data = COS_alliance
        
        sorted_freq_region = data.assign(freq = data.groupby('Region')['Region'].transform('count'))\
        .sort_values(by = ['freq','Region'],ascending = [False,True]).loc[:,['Region']]
        
        COS_alliance_region = bar_cluster(df = sorted_freq_region, x = 'Region',
                        code = 'Region'  , title = 'Distribution of Regions', xaxis = 'Region')
        
        figure = COS_alliance_region
        
        return figure
    
    elif (tab == 'tab-1-example') & (raids == 'TEP') :
        
        TEP_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'the-eternal-palace', faction = 'alliance')
        
        data = TEP_alliance
        
        sorted_freq_region = data.assign(freq = data.groupby('Region')['Region'].transform('count'))\
        .sort_values(by = ['freq','Region'],ascending = [False,True]).loc[:,['Region']]
        
        TEP_alliance_region = bar_cluster(df = sorted_freq_region, x = 'Region',
                        code = 'Region'  , title = 'Distribution of Regions', xaxis = 'Region')
        
        figure = TEP_alliance_region
        
        return figure

    elif (tab == 'tab-1-example') & (raids == 'NTWC') :
        
        NTWC_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'nyalotha-the-waking-city', faction = 'alliance')
        
        data = NTWC_alliance
        
        sorted_freq_region = data.assign(freq = data.groupby('Region')['Region'].transform('count'))\
        .sort_values(by = ['freq','Region'],ascending = [False,True]).loc[:,['Region']]
        
        NTWC_alliance_region = bar_cluster(df = sorted_freq_region, x = 'Region',
                        code = 'Region'  , title = 'Distribution of Regions', xaxis = 'Region')
        
        figure = NTWC_alliance_region
        
        return figure
    
    # Tab 2
    elif (tab == 'tab-2-example') & (raids == 'U') :
        
        uldir_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'uldir', faction = 'horde')
        
        data = uldir_horde
        
        sorted_freq_region = data.assign(freq = data.groupby('Region')['Region'].transform('count'))\
        .sort_values(by = ['freq','Region'],ascending = [False,True]).loc[:,['Region']]
        
        uldir_horde_region = bar_cluster(df = sorted_freq_region, x = 'Region',
                        code = 'Region'  , title = 'Distribution of Regions', xaxis = 'Region')
        
        figure = uldir_horde_region
        
        return figure
    
    elif (tab == 'tab-2-example') & (raids == 'BOD') :
        
        BOD_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'battle-of-dazaralor', faction = 'horde')
        
        data = BOD_horde
        
        sorted_freq_region = data.assign(freq = data.groupby('Region')['Region'].transform('count'))\
        .sort_values(by = ['freq','Region'],ascending = [False,True]).loc[:,['Region']]
        
        BOD_horde_region = bar_cluster(df = sorted_freq_region, x = 'Region',
                        code = 'Region'  , title = 'Distribution of Regions', xaxis = 'Region')
        
        figure = BOD_horde_region
        
        return figure
    
    elif (tab == 'tab-2-example') & (raids == 'COS') :
        
        COS_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'crucible-of-storms', faction = 'horde')
        
        data = COS_horde
        
        sorted_freq_region = data.assign(freq = data.groupby('Region')['Region'].transform('count'))\
        .sort_values(by = ['freq','Region'],ascending = [False,True]).loc[:,['Region']]
        
        COS_horde_region = bar_cluster(df = sorted_freq_region, x = 'Region',
                        code = 'Region'  , title = 'Distribution of Regions', xaxis = 'Region')
        figure = COS_horde_region
        
        return figure

    elif (tab == 'tab-2-example') & (raids == 'TEP') :
        
        TEP_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'the-eternal-palace', faction = 'horde')
        
        data = TEP_horde
        
        sorted_freq_region = data.assign(freq = data.groupby('Region')['Region'].transform('count'))\
        .sort_values(by = ['freq','Region'],ascending = [False,True]).loc[:,['Region']]
        
        TEP_horde_region = bar_cluster(df = sorted_freq_region, x = 'Region',
                        code = 'Region'  , title = 'Distribution of Regions', xaxis = 'Region')
        
        figure = TEP_horde_region
        
        return figure
    
    elif (tab == 'tab-2-example') & (raids == 'NTWC') :
        
        NTWC_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'nyalotha-the-waking-city', faction = 'horde')
        
        data = NTWC_horde
        
        sorted_freq_region = data.assign(freq = data.groupby('Region')['Region'].transform('count'))\
        .sort_values(by = ['freq','Region'],ascending = [False,True]).loc[:,['Region']]
        
        NTWC_horde_region = bar_cluster(df = sorted_freq_region, x = 'Region',
                        code = 'Region'  , title = 'Distribution of Regions', xaxis = 'Region')
        
        figure = NTWC_horde_region
        
        return figure
    
    return 'Select a faction and raid.'


    
### Dynamically updates the realm plot given the user's inputs    
@app.callback(
    Output('Realm', 'figure'),
    
    [Input(component_id = 'tabs-with-classes', component_property = 'value'),
    Input(component_id = 'Raids', component_property = 'value'),]
    
)
def callback_realm(tab, raids):

    
    # Tab 1
        # Tab 1
    if (tab == 'tab-1-example') & (raids == 'U') :
        
        uldir_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'uldir', faction = 'alliance')
    
        data = uldir_alliance
        
        sorted_freq_realm = data.assign(freq = data.groupby('Realm')['Realm'].transform('count'))\
        .sort_values(by = ['freq','Realm'],ascending = [False,True]).loc[:,['Realm']]
        
        uldir_alliance_realm = bar_cluster(df = sorted_freq_realm, x = 'Realm',
                        code = 'Realm'  , title = 'Distribution of Realms', xaxis = 'Realm')
        
        figure = uldir_alliance_realm
        
        return figure
    
    elif (tab == 'tab-1-example') & (raids == 'BOD') :
        
        BOD_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'battle-of-dazaralor', faction = 'alliance')
        
        data = BOD_alliance

        sorted_freq_realm = data.assign(freq = data.groupby('Realm')['Realm'].transform('count'))\
        .sort_values(by = ['freq','Realm'],ascending = [False,True]).loc[:,['Realm']]
        
        BOD_alliance_realm = bar_cluster(df = sorted_freq_realm, x = 'Realm',
                        code = 'Realm'  , title = 'Distribution of Realms', xaxis = 'Realm')
        
        figure = BOD_alliance_realm 
        
        return figure
    
    elif (tab == 'tab-1-example') & (raids == 'COS') :
        
        COS_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'crucible-of-storms', faction = 'alliance')
        
        data = COS_alliance
        
        sorted_freq_realm = data.assign(freq = data.groupby('Realm')['Realm'].transform('count'))\
        .sort_values(by = ['freq','Realm'],ascending = [False,True]).loc[:,['Realm']]
        
        COS_alliance_realm = bar_cluster(df = sorted_freq_realm, x = 'Realm',
                        code = 'Realm'  , title = 'Distribution of Realms', xaxis = 'Realm')
        
        figure = COS_alliance_realm
        
        return figure
    
    elif (tab == 'tab-1-example') & (raids == 'TEP') :
        
        TEP_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'the-eternal-palace', faction = 'alliance')
        
        data = TEP_alliance
        
        sorted_freq_realm = data.assign(freq = data.groupby('Realm')['Realm'].transform('count'))\
        .sort_values(by = ['freq','Realm'],ascending = [False,True]).loc[:,['Realm']]
        
        TEP_alliance_realm = bar_cluster(df = sorted_freq_realm, x = 'Realm',
                        code = 'Realm'  , title = 'Distribution of Realms', xaxis = 'Realm')
        
        figure = TEP_alliance_realm
        
        return figure

    elif (tab == 'tab-1-example') & (raids == 'NTWC') :
        
        NTWC_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'nyalotha-the-waking-city', faction = 'alliance')
        
        data = NTWC_alliance
        
        sorted_freq_realm = data.assign(freq = data.groupby('Realm')['Realm'].transform('count'))\
        .sort_values(by = ['freq','Realm'],ascending = [False,True]).loc[:,['Realm']]
        
        NTWC_alliance_realm = bar_cluster(df = sorted_freq_realm, x = 'Realm',
                        code = 'Realm'  , title = 'Distribution of Realms', xaxis = 'Realm')
        
        figure = NTWC_alliance_realm
        
        return figure
    
    # Tab 2
    elif (tab == 'tab-2-example') & (raids == 'U') :
        
        uldir_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'uldir', faction = 'horde')
        
        data = uldir_horde
        
        sorted_freq_realm = data.assign(freq = data.groupby('Realm')['Realm'].transform('count'))\
        .sort_values(by = ['freq','Realm'],ascending = [False,True]).loc[:,['Realm']]
        
        uldir_horde_realm = bar_cluster(df = sorted_freq_realm, x = 'Realm',
                        code = 'Realm'  , title = 'Distribution of Realms', xaxis = 'Realm')
        
        figure = uldir_horde_realm 
        
        return figure
    
    elif (tab == 'tab-2-example') & (raids == 'BOD') :
        
        BOD_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'battle-of-dazaralor', faction = 'horde')
        
        data = BOD_horde
        
        sorted_freq_realm = data.assign(freq = data.groupby('Realm')['Realm'].transform('count'))\
        .sort_values(by = ['freq','Realm'],ascending = [False,True]).loc[:,['Realm']]
        
        BOD_horde_realm = bar_cluster(df = sorted_freq_realm, x = 'Realm',
                        code = 'Realm'  , title = 'Distribution of Realms', xaxis = 'Realm')
        
        figure = BOD_horde_realm
        
        return figure
    
    elif (tab == 'tab-2-example') & (raids == 'COS') :
        
        COS_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'crucible-of-storms', faction = 'horde')
        
        data = COS_horde
        
        sorted_freq_realm = data.assign(freq = data.groupby('Realm')['Realm'].transform('count'))\
        .sort_values(by = ['freq','Realm'],ascending = [False,True]).loc[:,['Realm']]
        
        COS_horde_realm = bar_cluster(df = sorted_freq_realm, x = 'Realm',
                        code = 'Realm'  , title = 'Distribution of Realms', xaxis = 'Realm')
        
        figure = COS_horde_realm 
        
        return figure

    elif (tab == 'tab-2-example') & (raids == 'TEP') :
        
        TEP_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'the-eternal-palace', faction = 'horde')
        
        data = TEP_horde
        
        sorted_freq_realm = data.assign(freq = data.groupby('Realm')['Realm'].transform('count'))\
        .sort_values(by = ['freq','Realm'],ascending = [False,True]).loc[:,['Realm']]
        
        TEP_horde_realm = bar_cluster(df = sorted_freq_realm, x = 'Realm',
                        code = 'Realm'  , title = 'Distribution of Realms', xaxis = 'Realm')
        
        figure = TEP_horde_realm
        
        return figure
    
    elif (tab == 'tab-2-example') & (raids == 'NTWC') :
        
        NTWC_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'nyalotha-the-waking-city', faction = 'horde')
        
        data = NTWC_horde
        
        sorted_freq_realm = data.assign(freq = data.groupby('Realm')['Realm'].transform('count'))\
        .sort_values(by = ['freq','Realm'],ascending = [False,True]).loc[:,['Realm']]
        
        
        NTWC_horde_realm = bar_cluster(df = sorted_freq_realm, x = 'Realm',
                        code = 'Realm', title = 'Distribution of Realms', xaxis = 'Realm')
        
        figure = NTWC_horde_realm
        
        return figure
    
    return 'Select a faction and raid.'



### Dynamically updates the time series plot given the user's inputs
@app.callback(
    Output('Time series', 'figure'),
    [Input(component_id = 'tabs-with-classes', component_property = 'value'),
    Input(component_id = 'Raids', component_property = 'value'),]
)

def callback_timeseries(tab, raids):

    
    # Tab 1
    if (tab == 'tab-1-example') & (raids == 'U') :
        
        uldir_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'uldir', faction = 'alliance')
    
        data = uldir_alliance
        
        figure = timeseries(df = data, x = data['Date'],
                   y = data['Rank'], code = data['Region'],
                   title = 'Mythic Raid Leaderboard Time series', xaxis = 'Date')
    
        return figure
    
    elif (tab == 'tab-1-example') & (raids == 'BOD') :
        
        BOD_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'battle-of-dazaralor', faction = 'alliance')
        
        data = BOD_alliance

        figure = timeseries(df = data, x = data['Date'],
                   y = data['Rank'], code = data['Region'],
                   title = 'Mythic Raid Leaderboard Time series', xaxis = 'Date')
        
        return figure
    
    elif (tab == 'tab-1-example') & (raids == 'COS') :
        
        COS_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'crucible-of-storms', faction = 'alliance')
        
        data = COS_alliance
        
        figure = timeseries(df = data, x = data['Date'],
                   y = data['Rank'], code = data['Region'],
                   title = 'Mythic Raid Leaderboard Time series', xaxis = 'Date')
        
        return figure
    
    elif (tab == 'tab-1-example') & (raids == 'TEP') :
        
        TEP_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'the-eternal-palace', faction = 'alliance')
        
        data = TEP_alliance
        
        figure = timeseries(df = data, x = data['Date'],
                   y = data['Rank'], code = data['Region'],
                   title = 'Mythic Raid Leaderboard Time series', xaxis = 'Date')
        
        return figure

    elif (tab == 'tab-1-example') & (raids == 'NTWC') :
        
        NTWC_alliance = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'nyalotha-the-waking-city', faction = 'alliance')
        
        data = NTWC_alliance
        
        figure = timeseries(df = data, x = data['Date'],
                   y = data['Rank'], code = data['Region'],
                   title = 'Mythic Raid Leaderboard Time series', xaxis = 'Date')
        
        return figure
    
    # Tab 2
    elif (tab == 'tab-2-example') & (raids == 'U') :
        
        uldir_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'uldir', faction = 'horde')
        
        data = uldir_horde
        
        figure = timeseries(df = data, x = data['Date'],
                   y = data['Rank'], code = data['Region'],
                   title = 'Mythic Raid Leaderboard Time series', xaxis = 'Date')
    
        return figure
    
    elif (tab == 'tab-2-example') & (raids == 'BOD') :
        
        BOD_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'battle-of-dazaralor', faction = 'horde')
        
        data = BOD_horde
        
        figure = timeseries(df = data, x = data['Date'],
                   y = data['Rank'], code = data['Region'],
                   title = 'Mythic Raid Leaderboard Time series', xaxis = 'Date')
        
        return figure
    
    elif (tab == 'tab-2-example') & (raids == 'COS') :
        
        COS_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'crucible-of-storms', faction = 'horde')
        
        data = COS_horde
        
        figure = timeseries(df = data, x = data['Date'],
                   y = data['Rank'], code = data['Region'],
                   title = 'Mythic Raid Leaderboard Time series', xaxis = 'Date')
        
        return figure

    elif (tab == 'tab-2-example') & (raids == 'TEP') :
        
        TEP_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'the-eternal-palace', faction = 'horde')
        
        data = TEP_horde
        
        figure = timeseries(df = data, x = data['Date'],
                   y = data['Rank'], code = data['Region'],
                   title = 'Mythic Raid Leaderboard Time series', xaxis = 'Date')
        
        return figure
    
    elif (tab == 'tab-2-example') & (raids == 'NTWC') :
        
        NTWC_horde = get_Data(client_ID = 'c21b7526b481437199fe2f412b267412', secret_key = 'nOiBABqC2wJF71GcWZmcShXea1tSBT4a',
        raid = 'nyalotha-the-waking-city', faction = 'horde')
        
        data = NTWC_horde
        
        figure = timeseries(df = data, x = data['Date'],
                   y = data['Rank'], code = data['Region'],
                   title = 'Mythic Raid Leaderboard Time series', xaxis = 'Date')
        
        return figure
    
    return 'Select a faction and raid.'
    
if __name__ == '__main__':
    app.run_server(debug = True)