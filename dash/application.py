import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

TITLE = "Project Morey \U0001F3C8 \U0001F4C8"

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
application = app.server
app.title = TITLE


def serve_layout():

    df = pd.read_csv("./2020_top_players.csv")

    zscore_box = px.box(
        df,
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
    )

    total_points_box = px.box(
        df,
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
    )

    return html.Div(
        children=[
            html.H1(children=TITLE),
            html.H4(
                children=f"2020 Top Players Total Points and Total Points Z-Score (scaled within position)."
            ),
            dcc.Graph(id="total_points_box", figure=total_points_box),
            dcc.Graph(id="zscore_box", figure=zscore_box),
        ]
    )


app.layout = serve_layout

########### Run the app
if __name__ == "__main__":
    application.run(debug=True, port=8080)
