from dash import Dash, html, callback, Input, Output, State

from components.calendar_component import calendar_container
from components.data_table import table_data_filter, data_table_layout


app = Dash(__name__, prevent_initial_callbacks=True)

app.layout = html.Div(
    [
        html.Div(html.H1("Dashboard"), id="text-grid"),
        html.Div(
            [
                html.H2(
                    "Total jobs: 0",
                    id="total-jobs-count",
                    style={"display": "inline-block", "marginRight": "1rem"},
                ),
                html.H2(
                    "Recommended jobs: 0",
                    id="recommended-jobs-count",
                    style={"display": "inline-block"},
                ),
            ],
            id="overview-stat-grid",
        ),
        html.Div([calendar_container()], id="calendar-grid"),
        html.Div(
            children=table_data_filter(),
            id="table-filter-box",
        ),
        html.Div(
            [data_table_layout()],
            id="table-grid",
        ),
        html.Div([], id="job-detail-button"),
    ],
    className="container-grid",
)


@callback(
    Output("total-jobs-count", "children"),
    Output("recommended-jobs-count", "children"),
    Input("total-data-display-store", "modified_timestamp"),
    State("total-data-display-store", "data"),
    prevent_initial_call=True,
)
def update_count_display(_, data_count):

    return (
        f"Total jobs: {data_count['total_jobs']}",
        f"Recommended jobs: {data_count['recommended_jobs']}",
    )


if __name__ == "__main__":

    app.run(debug=False, host="0.0.0.0")
