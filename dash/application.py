import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import pandas as pd
import plotly.express as px
from metrics import apply_metric_functions, metrics_dict

TITLE = "Project Morey \U0001F3C8 \U0001F4C8"

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
application = app.server
app.title = TITLE

df = pd.read_csv("./2019_2020_top_players.csv")
df.loc[df["height_inches"] == 0.0, "height_inches"] = None
df.dropna(subset=["height_inches", "weight_lbs"], inplace=True)

df = apply_metric_functions(df)
POSITIONS = df["position"].drop_duplicates().to_list()
YEARS = df["year"].drop_duplicates().to_list()
BASE_METRICS = [
    "z_score",
    "total_points",
    "average_points",
    "salary",
    "height_inches",
    "weight_lbs",
]
SYNTHETIC_METRICS = list(metrics_dict.keys())
METRICS = BASE_METRICS + SYNTHETIC_METRICS

app.layout = html.Div(
    children=[
        html.H1(children=TITLE),
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
        dcc.Graph(id="zscore_box"),
        html.Div(
            [
                html.P(children="Top Boxplot Metric:"),
                dcc.Dropdown(
                    id="metric-picker1",
                    options=[
                        {"label": i.replace("_", " ").title(), "value": i}
                        for i in METRICS
                    ],
                    value="total_points",
                ),
                html.P(children="Bottom Boxplot Metric:"),
                dcc.Dropdown(
                    id="metric-picker2",
                    options=[
                        {"label": i.replace("_", " ").title(), "value": i}
                        for i in METRICS
                    ],
                    value="z_score",
                ),
            ],
            style={"width": "50%", "display": "inline-block"},
        ),
        dcc.Graph(id="scatter-matrix"),
        dcc.Dropdown(
            id="matrix-select",
            options=[{"label": i, "value": i} for i in BASE_METRICS],
            value=BASE_METRICS,
            multi=True,
        ),
    ]
)


@app.callback(
    Output("zscore_box", "figure"),
    Input("metric-picker1", "value"),
    Input("metric-picker2", "value"),
    Input("position-checklist", "value"),
    Input("year-picker", "value"),
)
def update_graph(metric1, metric2, position_value, year_value):
    dff = df[(df["year"] == year_value) & (df["position"].isin(position_value))]

    box1 = px.box(
        dff,
        x="position",
        y=metric1,
        color="position",
        points="all",
        hover_data=[
            "player_name",
            "total_points",
            "average_points",
            "age",
            "experience_years",
        ],
        labels={metric1: metric1.replace("_", " ")},
    )

    box2 = px.box(
        dff,
        x="position",
        y=metric2,
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
        labels={metric2: metric2.replace("_", " ")},
    )

    fig = make_subplots(rows=2, cols=1, shared_xaxes=False)

    # update xaxis properties
    fig.update_xaxes(title_text="Position", row=2, col=1)

    # update yaxis properties
    fig.update_yaxes(title_text=metric1.replace("_", " ").title(), row=1, col=1)
    fig.update_yaxes(title_text=metric2.replace("_", " ").title(), row=2, col=1)

    n_boxes = len(box1.data)

    for i in range(n_boxes):
        b = box1.data[i]
        b.showlegend = False
        fig.add_trace(b, row=1, col=1)

    for i in range(n_boxes):
        b = box2.data[i]
        b.showlegend = False
        fig.add_trace(b, row=2, col=1)

    fig.update_layout(
        title_text=f"{year_value} Top Players ({metric1.replace('_', ' ').title()} and {metric2.replace('_', ' ').title()})",
        height=700,
    )

    return fig


@app.callback(
    Output("scatter-matrix", "figure"),
    Input("matrix-select", "value"),
    Input("position-checklist", "value"),
    Input("year-picker", "value"),
)
def update_scatter_matrix(matrix_select, position_value, year_value):
    dff = df[(df["year"] == year_value) & (df["position"].isin(position_value))]

    fig = px.scatter_matrix(
        dff,
        dimensions=[m for m in BASE_METRICS if m in matrix_select],
        color="position",
        hover_data=["player_name"],
        labels={
            m: m.replace("_", " ").title() for m in BASE_METRICS if m in matrix_select
        },
    )

    fig.update_layout(
        title_text="Scatter Matrix",
        height=700,
    )
    return fig


# run app
if __name__ == "__main__":
    application.run(debug=True, port=8080)
