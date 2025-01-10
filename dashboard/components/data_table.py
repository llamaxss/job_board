from dash import dcc, html, callback, Input, Output, State, dash_table
import pandas as pd
from typing import List, Dict

from db import Engine
from jobextractor.utils import job_url


def table_data_filter():

    return [
        dcc.Store(
            id="filter-table-store",
            data={
                "jobtype": [],
                "joblevel": [],
                "webname": [],
            },
        ),
        dcc.Store(
            id="total-data-display-store",
            data={
                "total_jobs": 0,
                "recommended_jobs": 0,
            },
        ),
        dcc.Dropdown(
            [],
            multi=True,
            id="filter-jobtype",
            className="table-filter",
            placeholder="Job Type",
            searchable=False,
        ),
        dcc.Dropdown(
            [],
            multi=True,
            id="filter-joblevel",
            className="table-filter",
            placeholder="Job Level",
            searchable=False,
        ),
        dcc.Dropdown(
            [],
            className="table-filter",
            multi=True,
            id="filter-web-name",
            placeholder="Website",
            searchable=False,
        ),

    ]


@callback(
    [
        Output("filter-jobtype", "options"),
        Output("filter-joblevel", "options"),
        Output("filter-web-name", "options"),
    ],
    Input("filter-table-store", "data"),
)
def init_option_filter(_):

    data: pd.DataFrame = pd.read_sql(
        "SELECT * FROM job_board JOIN (SELECT wtb.job_id AS job_id, GROUP_CONCAT(wt.work_type, ', ') AS work_type FROM work_type AS wt JOIN work_type_bridge AS wtb ON wt.work_type_id = wtb.work_type_id GROUP BY wtb.job_id) AS job_type_text ON job_board.id = job_type_text.job_id;",
        con=Engine,
        dtype={"listing_date": "datetime64[ns]"},
    )

    work_type_type = pd.read_sql("SELECT work_type FROM work_type;", con=Engine)
    job_type_options = [
        {"label": job_type, "value": job_type}
        for job_type in work_type_type["work_type"]
    ]

    job_level_options = [
        {"label": job_type, "value": job_type}
        for job_type in data["job_level"].unique()
    ]
    web_name_options = [
        {"label": job_type, "value": job_type} for job_type in data["web_name"].unique()
    ]

    return [
        job_type_options,
        job_level_options,
        web_name_options,
    ]


DEFAULT_COLUMNS = [
    {
        "companyName": "",
        "location": "",
        "title": "",
        "work_type": "",
        "listing_date": "",
        "salary_range": "",
        "web_name": "",
        "job_level": "",
        "max_salary": "",
        "min_salary": "",
        "url": "",
    }
]


def data_table_layout(
    data: List[Dict[str, str]] = DEFAULT_COLUMNS
) -> dash_table.DataTable:

    return dash_table.DataTable(
        id="table",
        data=data,
        columns=[
            {"name": "Company Name", "id": "company"},
            {"name": "Location", "id": "location"},
            {"name": "Title", "id": "title"},
            {"name": "Work Type", "id": "work_type"},
            {"name": "Listing Date", "id": "listing_date"},
            {"name": "Salary Range", "id": "salary_range"},
            {"name": "Website", "id": "web_name"},
            {"name": "Job Level", "id": "job_level"},
        ],
        page_action="native",
        page_size=20,
        style_table={"overflowX": "auto"},
        style_header={
            "textAlign": "center",
            "backgroundColor": "#6e98c3",
            "color": "white !important",
        },
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#e4edf5",
            },
        ],
        sort_action="native",
    )


@callback(
    Output("table", "style_data_conditional"),
    Input("table", "active_cell"),
    prevent_initial_call=True,
)
def style_selected_row(selected_cell):

    default_style = [
        {
            "if": {"row_index": "odd"},
            "backgroundColor": "#e4edf5",
        },
    ]
    if selected_cell is None:
        return default_style

    return [
        *default_style,
        {
            "if": {"row_index": selected_cell["row"]},
            "backgroundColor": "rgba(255, 65, 54, 0.2)",
        },
    ]


@callback(
    Output("job-detail-button", "children"),
    Input("table", "active_cell"),
    prevent_initial_call=True,
)
def show_list_job_detail(selected_cell):
    if selected_cell is None:
        return []

    rows_id = selected_cell["row_id"]
    job_data = pd.read_sql(
        f"SELECT job_id, web_name FROM job_board WHERE id = '{rows_id}';",
        con=Engine,
    ).loc[0, ["job_id", "web_name"]]
    url = job_url(job_data["job_id"], job_data["web_name"])
    return html.Button(
        [
            html.A(
                "View Job Details",
                href=url,
                target="_blank",
                style={"textDecoration": "none", "color": "white"},
            )
        ]
    )


@callback(
    Output("filter-table-store", "data", allow_duplicate=True),
    Input("filter-jobtype", "value"),
    State("filter-table-store", "data"),
    prevent_initial_call=True,
)
def update_filter_jobtype(jobtype, store_data):

    store_data["jobtype"] = jobtype
    return store_data


@callback(
    Output("filter-table-store", "data", allow_duplicate=True),
    Input("filter-joblevel", "value"),
    State("filter-table-store", "data"),
    prevent_initial_call=True,
)
def update_filter_joblevel(joblevel, store_data):

    store_data["joblevel"] = joblevel
    return store_data


@callback(
    Output("filter-table-store", "data", allow_duplicate=True),
    Input("filter-web-name", "value"),
    State("filter-table-store", "data"),
    prevent_initial_call=True,
)
def update_filter_website(website, store_data):

    store_data["webname"] = website
    return store_data


@callback(
    [
        Output("total-data-display-store", "data"),
        Output("table-grid", "children"),
    ],
    Input("filter-table-store", "modified_timestamp"),
    Input("date-selected-store", "modified_timestamp"),
    State("filter-table-store", "data"),
    State("date-selected-store", "data"),
    State("total-data-display-store", "data"),
)
def create_table(_, __, filter_args, date_filter_args, data_count):

    data: pd.DataFrame = pd.read_sql(
        "SELECT * FROM job_board JOIN (SELECT wtb.job_id AS job_id, GROUP_CONCAT(wt.work_type, ', ') AS work_type FROM work_type AS wt JOIN work_type_bridge AS wtb ON wt.work_type_id = wtb.work_type_id GROUP BY wtb.job_id) AS job_type_text ON job_board.id = job_type_text.job_id;",
        con=Engine,
        dtype={"listing_date": "datetime64[ns]"},
    )

    filted_data = data.copy()
    if (start_date := date_filter_args["start-date"]) and (
        end_date := date_filter_args["end-date"]
    ):
        filted_data = filted_data[
            (filted_data["listing_date"] >= start_date)
            & (filted_data["listing_date"] <= end_date)
        ]

    if jobtype := filter_args["jobtype"]:
        filted_data = filted_data[
            filted_data["work_type"].apply(
                lambda x: bool(set(x.split(", ")).intersection(jobtype))
            )
        ]

    if joblevel := filter_args["joblevel"]:
        filted_data = filted_data[filted_data["job_level"].isin(joblevel)]

    if webname := filter_args["webname"]:
        filted_data = filted_data[filted_data["web_name"].isin(webname)]

    filted_data["listing_date"] = filted_data["listing_date"].dt.strftime("%Y-%m-%d")

    fomated_data = filted_data.to_dict("records")

    data_count["total_jobs"] = filted_data.shape[0]
    data_count["recommended_jobs"] = filted_data[
        filted_data["job_level"].isin(["Decent level"])
    ].shape[0]

    return [data_count, data_table_layout(data=fomated_data)]
