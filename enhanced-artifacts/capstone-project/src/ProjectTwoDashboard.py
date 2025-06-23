
from dash import Dash
import dash_leaflet as dl
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import base64
import re
from bson import ObjectId
import os
import pandas as pd
from AnimalShelterCRUD import AnimalShelterCRUD, MongoDBConnection

###########################
# Data Manipulation / Model
###########################
host = os.getenv("MONGO_HOST")
port = os.getenv("MONGO_PORT")
db_name = os.getenv("MONGO_DB_NAME")

db_connection = MongoDBConnection(host, port, db_name)
db = AnimalShelterCRUD(db_connection, "animals")

df = pd.DataFrame.from_records(db.read({}))
df.drop(columns=['Unnamed: 0'], inplace=True, errors='ignore')

df = pd.DataFrame.from_records(db.read({}))
if '_id' in df.columns:
    df['_id'] = df['_id'].astype(str)
print(df.columns)
print(df.head())



#########################
# Dashboard Layout / View
#########################
app = Dash(__name__)

image_filename = '../Grazioso Salvare Logo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

app.layout = html.Div([
    html.Center(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), height=250, width=251)),
    html.Center(html.B(html.H1('Alan Chumsawang SNHU CS 340 MongoDB Authentication'))),
    html.Hr(),
    dcc.RadioItems(
        id='filter-type',
        options=[
            {'label': 'All', 'value': 'All'},
            {'label': 'Water Rescue', 'value': 'Water'},
            {'label': 'Mountain or Wilderness Rescue', 'value': 'Mountain'},
            {'label': 'Disaster Rescue or Individual Tracking', 'value': 'Disaster'},
        ],
        value='All'
    ),
    html.Hr(),
    dash_table.DataTable(
        id='datatable-id',
        columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns],
        data=df.to_dict('records'),
        row_selectable='single',
        page_size=10,
        style_table={'overflowX': 'auto'}
    ),
    html.Br(),
    html.Hr(),
    html.Div(className='row',
             style={'display': 'flex'},
             children=[
                 html.Div(id='graph-id', className='col s12 m6'),
                 html.Div(id='map-id', className='col s12 m6')
             ])
])

#############################################
# Interaction Between Components / Controller
#############################################

@app.callback(
    [Output('datatable-id', 'data'),
     Output('datatable-id', 'columns')],
    [Input('filter-type', 'value')]
)
def update_dashboard(filter_type):
    if filter_type == 'All':
        df = pd.DataFrame.from_records(db.read({}))
    elif filter_type == 'Water':
        df = pd.DataFrame.from_records(db.read({
            '$or': [
                {"breed": {'$regex': re.compile(".*lab.*", re.IGNORECASE)}},
                {"breed": {'$regex': re.compile(".*chesa.*", re.IGNORECASE)}},
                {"breed": {'$regex': re.compile(".*newf.*", re.IGNORECASE)}},
            ],
            "sex_upon_outcome": "Intact Female",
            "age_upon_outcome_in_weeks": {"$gte": 26.0, "$lte": 156.0}
        }))
    elif filter_type == 'Mountain':
        df = pd.DataFrame.from_records(db.read({
            '$or': [
                {"breed": {'$regex': re.compile(".*german.*", re.IGNORECASE)}},
                {"breed": {'$regex': re.compile(".*mala.*", re.IGNORECASE)}},
                {"breed": {'$regex': re.compile(".*old engilish.*", re.IGNORECASE)}},
                {"breed": {'$regex': re.compile(".*husk.*", re.IGNORECASE)}},
                {"breed": {'$regex': re.compile(".*rott.*", re.IGNORECASE)}},
            ],
            "sex_upon_outcome": "Intact Male",
            "age_upon_outcome_in_weeks": {"$gte": 26.0, "$lte": 156.0}
        }))
    elif filter_type == 'Disaster':
        df = pd.DataFrame.from_records(db.read({
            '$or': [
                {"breed": {'$regex': re.compile(".*german.*", re.IGNORECASE)}},
                {"breed": {'$regex': re.compile(".*golden.*", re.IGNORECASE)}},
                {"breed": {'$regex': re.compile(".*blood.*", re.IGNORECASE)}},
                {"breed": {'$regex': re.compile(".*dober.*", re.IGNORECASE)}},
                {"breed": {'$regex': re.compile(".*rott.*", re.IGNORECASE)}},
            ],
            "sex_upon_outcome": "Intact Male",
            "age_upon_outcome_in_weeks": {"$gte": 20.0, "$lte": 300.0}
        }))
    else:
        raise Exception("Unknown filter")

    # 🛠️ Convert ObjectId to string to prevent serialization errors
    if '_id' in df.columns:
        df['_id'] = df['_id'].astype(str)

    if 'animal_id' in df.columns:
        df['animal_id'] = df['animal_id'].apply(lambda x: str(x) if isinstance(x, ObjectId) else x)
    else:
        print("Warning: 'animal_id' column not found in DataFrame.")

    columns = [{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns]
    data = df.to_dict('records')

    return data, columns


@app.callback(
    Output('graph-id', "children"),
    [Input('datatable-id', "derived_virtual_data")]
)
def update_graphs(viewData):
    if viewData is None or len(viewData) == 0:
        return [html.Div("No data available to display")]

    dffPie = pd.DataFrame.from_dict(viewData)
    if 'breed' not in dffPie.columns:
        return [html.Div("No breed data available to display")]

    breed_counts = dffPie['breed'].value_counts()

    top_n = 10
    top_breeds = breed_counts.head(top_n)
    other_count = breed_counts.iloc[top_n:].sum()

    chart_data = pd.concat([
        top_breeds,
        pd.Series({'Other': other_count})
    ]).reset_index()

    chart_data.columns = ['breed', 'count']

    fig = px.pie(chart_data, names='breed', values='count', title='Preferred Animals (Top Breeds)')

    return [dcc.Graph(figure=fig)]

@app.callback(
    Output('map-id', "children"),
    [Input('datatable-id', "derived_virtual_data"),
     Input('datatable-id', "derived_virtual_selected_rows")]
)
def update_map(viewData, index):
    if viewData is None or index is None or len(index) == 0:
        markerArray = (30.75, -97.48)
        toolTip = "Austin Animal Center"
        popUpHeading = "Austin Animal Center"
        popUpParagraph = "Shelter Home Location"
    else:
        dff = pd.DataFrame.from_dict(viewData)
        row = index[0]
        try:
            coordLat = float(dff.iloc[row]['location_lat'])
            coordLong = float(dff.iloc[row]['location_long'])
            markerArray = (coordLat, coordLong)
            toolTip = dff.iloc[row]['breed']
            popUpHeading = "Animal Name"
            popUpParagraph = dff.iloc[row]['name']
        except (ValueError, KeyError):
            markerArray = (30.75, -97.48)
            toolTip = "Austin Animal Center"
            popUpHeading = "Austin Animal Center"
            popUpParagraph = "Shelter Home Location"

    return [dl.Map(style={'width': '700px', 'height': '450px'}, center=markerArray,
                   zoom=10, children=[dl.TileLayer(id="base-layer-id"),
                                      dl.Marker(position=markerArray, children=[
                                          dl.Tooltip(toolTip),
                                          dl.Popup([
                                              html.H1(popUpHeading),
                                              html.P(popUpParagraph)
                                          ])
                                      ])
                                      ])
            ]

if __name__ == '__main__':
    app.run(debug=True, port=8050)