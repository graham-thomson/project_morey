import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import pandas as pd
import plotly.express as px

TITLE = "Project Morey \U0001F3C8 \U0001F4C8"

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
application = app.server
app.title = TITLE

df = pd.read_csv("./2019_2020_top_players.csv")
POSITIONS = df["position"].drop_duplicates().to_list()
YEARS = df["year"].drop_duplicates().to_list()

app.layout = html.Div(
    children=[
        html.H1(children=TITLE),
        dcc.Graph(id="zscore_box"),
        html.Div(
            [
                html.P(children="Positions:"),
                dcc.Checklist(
                    id="position-checklist",
                    options=[{"label": i, "value": i} for i in POSITIONS],
                    value=POSITIONS,
                    labelStyle={"display": "inline-block"},
                ),
                html.P(children="Year:"),
                dcc.RadioItems(
                    id="year-picker",
                    options=[{"label": i, "value": i} for i in YEARS],
                    value=2020,
                    labelStyle={"display": "inline-block"},
                ),
            ],
            style={"width": "90%", "display": "inline-block"},
        ),
    ]
)


@app.callback(
    Output("zscore_box", "figure"),
    Input("position-checklist", "value"),
    Input("year-picker", "value"),
)
def update_graph(position_value, year_value):
    dff = df[(df["year"] == year_value) & (df["position"].isin(position_value))]

    zscore_box = px.box(
        dff,
        x="position",
        y="z_score",
        color="position",
        points="all",
        hover_data=[
            "player_name",
            "total_points",
            "average_points",
            "age",
            "experience_years",
        ],
        labels={"z_score": "Total Points Z-Score"},
    )

    total_points_box = px.box(
        dff,
        x="position",
        y="total_points",
        color="position",
        points="all",
        hover_data=[
            "player_name",
            "total_points",
            "z_score",
            "average_points",
            "age",
            "experience_years",
        ],
        labels={"total_points": "Total Points"},
    )

    fig = make_subplots(rows=2, cols=1, shared_xaxes=False)

    # update xaxis properties
    fig.update_xaxes(title_text="Position", row=2, col=1)

    # update yaxis properties
    fig.update_yaxes(title_text="Total Points", row=1, col=1)
    fig.update_yaxes(title_text="Z-Score", row=2, col=1)

    n_boxes = len(zscore_box.data)

    for i in range(n_boxes):
        b = total_points_box.data[i]
        b.showlegend = False
        fig.add_trace(b, row=1, col=1)

    for i in range(n_boxes):
        b = zscore_box.data[i]
        b.showlegend = False
        fig.add_trace(b, row=2, col=1)

    fig.update_layout(
        title_text=f"{year_value} Top Players Total Points and Total Points Z-Score (scaled within position).",
        height=700,
    )

    return fig


# run app
if __name__ == "__main__":
    application.run(debug=True, port=8080)
