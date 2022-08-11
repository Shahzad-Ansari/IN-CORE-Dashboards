# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 23:53:15 2022

@author: ShoebAnsari
"""


#%%
# =============================================================================
#   Block 1: Imports
# =============================================================================
from dash import Dash, dcc, html
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go
#%%
# =============================================================================
#   Block 2: Loading Dataframe
# =============================================================================
df = pd.read_csv("building_inventory.csv") # From the data frame
df = df[
        [

            "blockidstr","x","y","archetype" # select only these columns
        ]   
    ]
df = df.loc[df['archetype'].isin([1, 5])] # only rows that are archetype 1 or 5
df['blockidstr'] = df['blockidstr'].str.replace('CB','') # remove the CB in the blockidstr

df = df.rename(columns={'blockidstr': 'Blockgroup'}) # rename blockidstr to Blockgroup

df['Blockgroup'] = df['Blockgroup'].astype('int64') # cast Blockgroup to int

#%%
# =============================================================================
#   Block 3: Solution XLS
# =============================================================================
xls = pd.ExcelFile('Joplin Solution Excerpt.xlsx') # load the solution xls
solution1 = pd.read_excel(xls, 'Sheet1') # get both sheets in 
solution2 = pd.read_excel(xls, 'Sheet2') 
solution1['Blockgroup'] = solution1['Blockgroup'].astype('int64') # cast Blockgroup in solution to int
#%%
# =============================================================================
#   Block 4: Data Manipulation
# =============================================================================
centroidDF = df.groupby('Blockgroup',as_index = False)[['x','y']].mean() # data frame with the centroid data
countDF = df['Blockgroup'].value_counts() # find the count of each block group
countDF = countDF.reset_index(level=0) # reset index
countDF.columns.values[0] = 'Blockgroup' # rename colums
countDF.columns.values[1] = 'count'
mergedDF = pd.merge(centroidDF,solution1,on='Blockgroup') # merge centroid df with solution df on blockgroup
mergedDF['Blockgroup'] = mergedDF['Blockgroup'].values.astype('int64') # cast Blockgroup to int
modeDF = mergedDF.loc[mergedDF.groupby(['Blockgroup','Solution ID'])['Quantity'].idxmax()].reset_index(drop=True) # get the mode of each blockgroup
modeDF = pd.merge(modeDF,countDF,on='Blockgroup') # merge the mode df with the count df on Blockgroup
#%%
# =============================================================================
#   Block 5: Mitigation Color 
# =============================================================================

# Set the colors for each mitigation level
color = []
for row in modeDF['Mitigation Level']:
    if row == 0:
        color.append('grey')
    if row == 1:
        color.append('blue')
    if row == 2:
        color.append('orange')
    if row == 3:
        color.append('red')
modeDF['color'] = color

# Delete unused dataframes
del centroidDF
del xls
del solution1
del color
del row
del countDF



#%%
# def pareto_frontier(Xs, Ys, maxX = True, maxY = True):
# # Sort the list in either ascending or descending order of X
#     myList = sorted([[Xs[i], Ys[i]] for i in range(len(Xs))], reverse=maxX)
# # Start the Pareto frontier with the first value in the sorted list
#     p_front = [myList[0]]    
# # Loop through the sorted list
#     for pair in myList[1:]:
#         if maxY: 
#             if pair[1] >= p_front[-1][1]: # Look for higher values of Y…
#                 p_front.append(pair) # … and add them to the Pareto frontier
#         else:
#             if pair[1] <= p_front[-1][1]: # Look for lower values of Y…
#                 p_front.append(pair) # … and add them to the Pareto frontier
# # Turn resulting pairs back into a list of Xs and Ys
#     p_frontX = [pair[0] for pair in p_front]
#     p_frontY = [pair[1] for pair in p_front]
#     return p_frontX, p_frontY

# Xs, Ys = solution2['Economic Loss'],solution2['Functionality']# get your data from somewhere to go here
# p_front = pareto_frontier(Xs, Ys, maxX = False, maxY = True) 

#%%
# =============================================================================
#   Block 6: Run App
# =============================================================================
app = Dash(__name__)
#%%
# =============================================================================
#   Block 7: 3D Scatterplot
# =============================================================================
fig = go.Figure() # create a figure
# 3D Scatter plot 
fig.add_trace(go.Scatter3d(
            x = solution2['Economic Loss'], # x dim for scatter plot
            y = solution2['Functionality'], # y dim for scatter plot
            z = solution2['Dislocation'], # z dim for scatter plot
            mode = 'markers', # type of points on scatterplot
            name = 'markers', # name of the points on the scatterplot
            
            # settings for the scatterplot
            marker=dict(
                size=10, # The size of the markers are set by this 
                color=solution2['Dislocation'], # set color to an array/list of desired values
                colorscale='Viridis',   # choose a colorscale
                opacity=0.8 # opacity 
            )
        ))
#%%
# =============================================================================
#  Block 8: Figure interactivity
# =============================================================================
fig.update_layout(clickmode='event+select') #What happens when you click on a point

# titles and dimensions
fig.update_layout(scene = dict(
                    xaxis_title='Economic Loss',
                    yaxis_title='Functionality',
                    zaxis_title='Dislocation'),
                    title="Preto Frontier",
                    width=1200,
                    height=900)


#%%
# =============================================================================
#   Block 9: Layout
# =============================================================================
app.layout = html.Div([
   
    # the html container for the 3D scatterplot
    dcc.Graph(
        id='basic-interactions',
        figure=fig
    ),
    
    # the html contianer for the Mapbox
    html.Div([
        dcc.Graph(id='map'),
    ],className='six columns'),
    
])

#%%
# =============================================================================
#   Block 10: Callback
# =============================================================================
@app.callback(
    Output('map','figure'),
    Input('basic-interactions', 'clickData'))
# =============================================================================
#   Block 11: Callback Function
# =============================================================================
def update_map(clickData):
    # insert your own mapbox token
    mapbox_access_token = 'pk.eyJ1IjoicHJvbWFjaG9zIiwiYSI6ImNsNG5hYjkyYjFhZXYzanA0cTVwNjA3dm4ifQ.pcuIpf5FRuFB7SxT8k05Xw'
    
# =============================================================================
#     P1. Render Map when no point is clicked
# =============================================================================
    # If No point has been clicked
    if clickData is None:
        #make a map
        maps = go.Figure(go.Scattermapbox(
            lat=df['y'], # set lat and long
            lon=df['x'],
            mode='markers', 
            marker =({'size':5.5}) # make markers size variable 
        ))
    
        # set up map layout
        maps.update_layout(
            autosize=True, # Autosize
            hovermode='closest', # Show info on the closest marker
            showlegend=True, # show legend of colors
            mapbox=dict(
                accesstoken=mapbox_access_token, # token
                bearing=0, # starting facing direction
                # starting location
                center=dict(
                    lat=37.0433,
                    lon=-94.51306
                ),
                #angle and zoom
                pitch=0,
                zoom=12
            ),
            #height and width
            width=2000,
            height=1000
        )
        return maps
    
# =============================================================================
#     P2. Render map with click data
# =============================================================================
    # if a point is clicked
    else: 
        # get the x and y coords from the json obj
        xCoord = clickData['points'][0]['x'] 
        yCoord = clickData['points'][0]["y"]
        zCoord = clickData['points'][0]["z"]
        
        #add flush = True or it wont display the message.
        print(f'xcoord is {xCoord} and ycoord is {yCoord} and zcord is {zCoord}',flush=True)
        
        #get the solution ID 
        solutionRow = solution2.loc[(solution2['Economic Loss'] == xCoord) & (solution2['Functionality'] == yCoord) & (solution2['Dislocation'] == zCoord)].values[0]
        solutionID = int(solutionRow[0])        
        
        print(f'solution id is {solutionID}',flush=True)
        # get the rows that coorespond to that solution ID
        sample = modeDF.loc[(modeDF['Solution ID'] == solutionID)]
        
        # render the map with the new solution data        
        maps = go.Figure(go.Scattermapbox(
            lat=sample['y'],
            lon=sample['x'],
            mode='markers', 
            marker =({'color':sample['color'],'size':sample['count']})

        ))
        
# =============================================================================
#   P3. Map Layout
# =============================================================================
        
        # set up map layout
        maps.update_layout(
            autosize=True, # Autosize
            hovermode='closest', # Show info on the closest marker
            showlegend=True, # show legend of colors
            mapbox=dict(
                accesstoken=mapbox_access_token, # token
                bearing=0, # starting facing direction
                # starting location
                center=dict(
                    lat=37.0433,
                    lon=-94.51306
                ),
                #angle and zoom
                pitch=0,
                zoom=12
            ),
            #height and width
            width=2000,
            height=1000
        )

        return maps


#%%
# =============================================================================
#   Block 11: Run
# =============================================================================
if __name__ == '__main__':
    app.run_server(debug=True,use_reloader=False)









