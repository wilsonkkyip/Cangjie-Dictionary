# Cangjie Input Method Dictionary

This repo describes how to create a dictionary for [Cangjie input method](https://en.wikipedia.org/wiki/Cangjie_input_method) from scrach. The [Unicode Character Database (version 14.0)](https://www.unicode.org/versions/Unicode14.0.0/) (UCD) is used to map each Chinese character to a combination of "[radicals](https://en.wikipedia.org/wiki/Radical_(Chinese_characters))" for the Cangjie input method. A Python Dash webapp is also created to receive Chinese characters as queries and return the corresponding combination of radicals for Cangjie input method. 

## Converting UCD into a csv file

Download the [`Unihan.zip`](https://www.unicode.org/Public/14.0.0/ucd/Unihan.zip) from the [UCD directory](https://www.unicode.org/Public/14.0.0/ucd/). Unzip it and run the following script in Python to create a mapping table in csv format.

```python
with open("./Unihan/Unihan_DictionaryLikeData.txt", "r") as f:
    content = f.read()

content = content.split("\n")
content = [x for x in content if len(x) > 0]
content = [x for x in content if x.startswith("U+")]
content = [x.split("\t") for x in content]
content = [x for x in content if x[1] == "kCangjie"]

unicode = [x[0] for x in content]
unicode = [x.replace("U+", "") for x in unicode]

def u_to_character(x):
    return ("\\U" + str(x).zfill(8)).encode().decode("unicode_escape")

chars = [u_to_character(x) for x in unicode]

radicals_dict = [
    "日", "月", "金", "木", "水", "火", "土", "竹", "戈", "十", "大", "中", "一",
    "弓", "人", "心", "手", "口", "尸", "廿", "山", "女", "田", "難", "卜", "重"
]
radicals_dict = dict(zip(
    list(map(chr, range(65, 91))), 
    radicals_dict
))

radicals = [x[2] for x in content]
for i, x in enumerate(radicals):
    for k, v in radicals_dict.items():
        r = radicals[i]
        radicals[i] = r.replace(k, v)

mapping_list = []
for i in range(len(content)):
    mapping_list.append(
        "{},{},{}".format(chars[i], radicals[i], content[i][2])
    )

mapping_list = "\n".join(mapping_list)

with open("./mapping.csv", "w") as f:
    f.write(mapping_list)
```

## The Dash WebApp

With the above csv mapping table, the script below create a Dash app. It is also ready for deployment on Flask. It is tested on an Apache2 framework along with the `app.wsgi` and an appropriate Apache site configuration file. 

```python 
# app.py
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
```

## The `app.wsgi`

```python 
import sys
sys.path.insert(0, "/var/www/html/cangjie")
from app import server as application
```