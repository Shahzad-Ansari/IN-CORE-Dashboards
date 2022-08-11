# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 19:53:57 2022

@author: ShahzadAnsari
"""

#%%
#BLOCK 1
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_table
import math
import numpy as np
#%%
#BLOCK 2

# =============================================================================
# Data frame manipulation
# =============================================================================
df = pd.read_csv("building_inventory.csv") # get dataframe and select desired columns
df = df[
        [
            "strctid","parid","blockidstr",
            "address1","house_no","archetype",
            "year_built","gsq_foot","appr_bldg",
            "dwell_unit","x","y",
            "gsq_meter","aprbldg","aprland",
            "aprtot","huestimate","d_sf"
        ]   
    ]

# create a new column called color and assign a color for each archetype
color = []
for row in df['archetype']:
    if row == 1:
        color.append('blue')
    if row == 5:
        color.append('red')
    if row == 6:
        color.append('green')
    if row == 7:
        color.append('orange')
    if row == 8:
        color.append('yellow')
    if row == 9:
        color.append('purple')
    if row == 10:
        color.append('brown')
    if row == 11:
        color.append('pink')
    if row == 12:
        color.append('gray')
    if row == 13:
        color.append('olive')
    if row == 14:
        color.append('cyan')
    if row == 15:
        color.append('firebrick')
    if row == 16:
        color.append('lime')
    if row == 17:
        color.append('royalblue')
    if row == 18:
        color.append('violet')
    if row == 19:
        color.append('teal') 
df['color'] = color

# Find the mean of year build aprtot and gsq foot
dff = df.groupby('archetype',as_index=False)[['year_built','aprtot','gsq_foot']].mean() 

#%%
#BLOCK 3
# create a new dash app
app = dash.Dash(__name__)
#%%
#BLOCK 4
app.layout = html.Div([
    
# =============================================================================
#     Data table
# =============================================================================
    ##################################################################
    html.Div([
        dash_table.DataTable(
            id='datatable_id',
            data=dff.to_dict('records'),
            # itterate through the names of the columns in the df
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": False} for i in dff.columns
            ],
            editable=False, # dont want it to be editable
            row_selectable="multi", # want to be able to select more than one value
            row_deletable=False, # dont want user to be able to delete value
            selected_rows=[], # on instatiation, no rows are selected
            page_action="native", # the built in paging action from DCC
            page_current= 0, # start it at the first page 
            page_size= 6, # each page has 6 rows
            # styling for each column 
            style_cell_conditional=[
                {'if': {'column_id': 'archetype'},
                 'width': '20%', 'textAlign': 'left'},
                {'if': {'column_id': 'year_built'},
                 'width': '20%', 'textAlign': 'left'},
                {'if': {'column_id': 'gsq_foot'},
                 'width': '25%', 'textAlign': 'left'},
                {'if': {'column_id': 'aprtot'},
                 'width': '35%', 'textAlign': 'left'},
            ],
        ),
    ],className='row'),
    
    ##################################################################
# =============================================================================
# Drop Down barr
# =============================================================================
    html.Div([
        html.Div([
        dcc.Dropdown(id='chartdropdown',
            # The options that you can select from        
            options=[
                     {'label': 'Archetype', 'value': 'archetype'},
                     {'label': 'Year Built', 'value': 'year_built'},
                     {'label': 'Dwell Unit', 'value': 'dwell_unit'}
            ],
            value='archetype', # default value selected
            multi=False, # dont want user to be able to select multiple values
            clearable=False # dont want user to be able to reset value as null
        ),
        ],className='six columns'),

    ],className='row'),
    
    
    ##################################################################
# =============================================================================
# Graphs
# =============================================================================
    html.Div([
        html.Div([
            dcc.Graph(id='map'), # new graph named map
        ],className='six columns'),

        html.Div([
            dcc.Graph(id='graphs'), # new graph named graphs
        ],className='six columns'),

    ],className='row'),
    ##################################################################
   
])

#%%
#BLOCK 5

# callback to update graphs and map
@app.callback(
    [Output('graphs', 'figure'),
     Output('map','figure')],
     
    [Input('chartdropdown', 'value'),
     Input('datatable_id','selected_rows'),
     Input('datatable_id', 'data')]
)
#function to update the visualization and graphs
def update_output(chartdropdown,selected_rows,data):
    
# =============================================================================
#    P1. Select the specific archetypes
# =============================================================================
    selected_archetypes = [] # start with no archetypes selected
    if len(selected_rows) == 0: # if there are no selected fows
        
        selected_rows = list(np.arange(0,16)) # there are 16 possible values in the table this is used to determine which row index was selected by default all are
        # for every row that has been selected
        for i in selected_rows:
            selected_archetypes.append(data[i]['archetype']) # append the archetype number to the selected archetype
        print(selected_archetypes)
        dff = df.loc[df['archetype'].isin(selected_archetypes)] # get the dataframe containting the specified archetypes.
         
    else:
        # for every row that has been selected
        for i in selected_rows:
          selected_archetypes.append(data[i]['archetype']) # appened the selected rows
        print(selected_archetypes)
        dff = df.loc[df['archetype'].isin(selected_archetypes)] # get the dataframe containg the specified archetypes

# =============================================================================
#    P2. Make the facet figure container with 2 rows and 1 column 
# =============================================================================
    fig = make_subplots(rows=2,cols=1,column_widths=[10],row_width=[100,100])    
# =============================================================================
#   P3. Histogram
# =============================================================================
    Histogram_1 = go.Histogram(
        x=dff[chartdropdown], # x values of the histogram are the input from chartdropdown
        texttemplate="%{x}", # the column name 
        textfont_size=20 # text font size
        )
# =============================================================================
#     P4. Box Plot
# =============================================================================
    Box_1 = go.Box(x=dff[chartdropdown]) # create a box plot from the selected input from chartdropdown
    fig.add_trace(Histogram_1,1,1) # add the graph to possition 1,1 in the faceted figure container
    fig.add_trace(Box_1,2,1) # add the graph to the possition 2,1 in the faceted figure container
    lowerRange_hist = 1830 if(chartdropdown == 'year_built') else dff[chartdropdown].min() # set the lower bound 
    upperRange_hist =  2010 if(chartdropdown == 'year_built') else dff[chartdropdown].max() # set the upper bound
    fig.update_xaxes(range=[lowerRange_hist-1,upperRange_hist+1],type="linear") # set the x axis range 
    
    # if the analysis is on year_built scale linearly else scale log
    if 'year_built' in chartdropdown:
        fig.update_yaxes(type="linear",row=1,col=1)
    else:
        fig.update_yaxes(type="log",row=1,col=1)
        
    # update the title on the graphs
    fig.update_layout(title_text=f"Information on {chartdropdown}",showlegend=False,width=1000,height=1000,bargap=0.2)
# =============================================================================
#     P6. Map box
# =============================================================================
    # map box access token
    mapbox_access_token = 'pk.eyJ1IjoicHJvbWFjaG9zIiwiYSI6ImNsNG5hYjkyYjFhZXYzanA0cTVwNjA3dm4ifQ.pcuIpf5FRuFB7SxT8k05Xw'
    
    # create a scatter plot named map
    maps = go.Figure(go.Scattermapbox(
            lat=dff['y'], # get the lattitude 
            lon=dff['x'], # get the longitude
            mode='markers', # sets the scatterplot points to markers
            marker =({'color':dff['color'],'size':3.5}) # the color of the markers is set to the color of the archetype and size set to 3.5

        ))
    

# =============================================================================
#   P7. Map Layout
# =============================================================================
    
    # update the layout of the map
    maps.update_layout(
        autosize=True, #  auotmatically size the map
        hovermode='closest', # show hover info on the closest marker
        showlegend=True, # show legend of the colors of the markers
       # set default map view
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=37.0433, # set default lat and long 
                lon=-94.51306
            ),
            pitch=0,
            zoom=12
        ),
        # set mapbox dimensions
        width=2000,
        height=2000
    )
    
    
# =============================================================================
#     P8. Return the output
# =============================================================================
    #since the callback has a list of two outputs we must have the same.
    return [fig,maps]


#------------------------------------------------------------------
#%%
# =============================================================================
# Block 6: Run the server
# =============================================================================
if __name__ == '__main__':
    app.run_server(debug=True,use_reloader=False)
#%%

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

