from flask import Flask
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, Dash

with open("./mapping.csv", "r") as f:
    mapping_list = [x.split(",") for x in f.read().split("\n")]

chars = [x[0] for x in mapping_list]
radicals = [x[1] for x in mapping_list]
keys = [x[2] for x in mapping_list]

server = Flask(__name__)
app = Dash(__name__, server = server, external_stylesheets=[dbc.themes.UNITED])
app.title = "倉頡字典"

app_input = html.Div([
    html.P("輸入文字："),
    dbc.Input(id = "textInput", placeholder="以文字查詢", type="text"),
    html.Br(),
    dbc.Button("查詢", id = "btn", color="secondary")
])


app_output = html.Div([
    html.P("查詢結果"),
    html.Div(id = "output")
])


app.layout = dbc.Container(
    [
        html.H1("倉頡字典"),
        html.Hr(),
        dbc.Row([app_input]),
        dbc.Row([app_output])
    ]
)


@app.callback(
    Output(component_id='output', component_property='children'),
    Input("btn", "n_clicks"),
    Input('textInput', 'value'),
)
def make_output(n, input_value):
    if input_value is None:
        return html.Table([])
    
    input_value = list(input_value)
    input_value.reverse()
    idx = [chars.index(x) if x in chars else None for x in input_value]
    idx = [x for x in idx if x is not None]
    tbl = []
    for i in idx:
        tbl.append(html.Tr([
            html.Td(chars[i], style={"width":"40pt"}),
            html.Td(radicals[i], style={"width":"100pt"}),
            html.Td(keys[i], style={"width":"60pt"})
        ], style = {"height":"30pt"}))
    return html.Table(tbl) 

if __name__ == "__main__":
    app.run(debug = True)
