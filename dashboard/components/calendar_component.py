import calendar
from dash import dash_table, html, callback, Input, Output, ctx, ALL, State, MATCH, dcc
import pandas as pd
from datetime import datetime, date, timedelta
import time
from typing import Optional

MAX_YEAR = 2100
MIN_YEAR = 1900


def calendar_container():

    return html.Div(
        [
            dcc.Store(
                id="current-calendar-store",
                data={"year": datetime.now().year, "month": datetime.now().month},
            ),
            dcc.Store(
                id="date-selected-store",
                data={
                    "end-date": None,
                    "start-date": None,
                    "end-date-label": "End",
                    "start-date-label": "Start",
                },
            ),
            dcc.Store(
                id="select-filter-store",
                data={"select-filter": "end"},
            ),
            html.Div(
                [
                    dcc.Input(
                        id="year-input",
                        type="number",
                        value=datetime.now().year,
                        min=MIN_YEAR,
                        max=MAX_YEAR,
                    ),
                    html.Div(
                        [
                            html.Button(
                                "<",
                                id="button-previous",
                                className="change-month",
                            ),
                            html.Button(
                                "Start",
                                id="button-start",
                                className="calendar-button-filter",
                            ),
                            html.Button(
                                "End",
                                id="button-end",
                                className="calendar-button-filter",
                            ),
                            html.Button(
                                ">",
                                id="button-next",
                                className="change-month",
                            ),
                        ],
                        className="calendar-tool-container",
                    ),
                ],
            ),
            html.Div(children=[], id="calendar-container"),
            html.Button("Clear", id="clear-button"),
        ],
        id="calendar",
    )


@callback(
    [Output("button-start", "children"), Output("button-end", "children")],
    Input("date-selected-store", "data"),
    prevent_initial_call=True,
)
def calendar_picker_label(data_selected):

    start_label = data_selected["start-date"] or data_selected["start-date-label"]
    end_label = data_selected["end-date"] or data_selected["end-date-label"]
    return [start_label, end_label]

@callback(
    [Output("button-start", "className"), Output("button-end", "className")],
    Input("select-filter-store", "data"),
    # prevent_initial_call=True,
)
def calendar_picker_class(filter_mode):
    filter_mode = filter_mode["select-filter"]

    if filter_mode == "start":
        start_label = "calendar-button-filter actived"
        end_label = "calendar-button-filter"
    elif filter_mode == "end":
        start_label = "calendar-button-filter"
        end_label = "calendar-button-filter actived"

    return [start_label, end_label]

@callback(
    Output("date-selected-store", "data", allow_duplicate=True),
    Input("clear-button", "n_clicks"),
    State("date-selected-store", "data"),
    prevent_initial_call=True,
)
def clear_selected_data(_, data):
    data["end-date"] = None
    data["start-date"] = None
    
    return data


@callback(
    Output("select-filter-store", "data"),
    Input("button-start", "n_clicks"),
    Input("button-end", "n_clicks"),
    State("select-filter-store", "data"),
    running=(
        [
            (Output("button-start", "disabled"), True, False),
            (Output("button-end", "disabled"), True, False),
        ]
    ),
    prevent_initial_call=True,
)
def select_filter(_, __, data):
    if ctx.triggered_id == "button-start":
        data["select-filter"] = "start"
    elif ctx.triggered_id == "button-end":
        data["select-filter"] = "end"
    return data


@callback(
    Output("calendar-container", "children"),
    Input("current-calendar-store", "modified_timestamp"),
    State("current-calendar-store", "data"),
    prevent_initial_call=True,
)
def update_calendar(_, data):
    return calendar_table(data["year"], data["month"])


@callback(
    Output("current-calendar-store", "data", allow_duplicate=True),
    Input("year-input", "value"),
    State("current-calendar-store", "data"),
    prevent_initial_call=True,
)
def update_year_input(year_input, data):
    data["year"] = year_input
    return data


@callback(
    [
        Output("current-calendar-store", "data", allow_duplicate=True),
        Output("year-input", "value"),
    ],
    Input("button-previous", "n_clicks"),
    Input("button-next", "n_clicks"),
    State("current-calendar-store", "data"),
    running=(
        [
            (Output("button-previous", "disabled"), True, False),
            (Output("button-next", "disabled"), True, False),
        ]
    ),
    prevent_initial_call=True,
)
def update_calendar_data(_, __, data):
    current_calendar_date = date(data["year"], data["month"], 15)
    if ctx.triggered_id == "button-previous" and data["year"] > MIN_YEAR:
        current_calendar_date = current_calendar_date - timedelta(days=20)
    elif ctx.triggered_id == "button-next" and data["year"] < MAX_YEAR:
        current_calendar_date = current_calendar_date + timedelta(days=20)
    data = {"year": current_calendar_date.year, "month": current_calendar_date.month}

    return [data, data["year"]]


def calendar_table(year_selected, month_selected):

    calendar_text = calendar.TextCalendar(firstweekday=6)
    title, day_of_week_arrb, *week_list, _ = calendar_text.formatmonth(
        year_selected, month_selected
    ).split("\n")
    month_name = title.split()[0]
    calendar_weeks = [
        [week[i : i + 2].strip() for i in range(0, len(week), 3)] for week in week_list
    ]

    return html.Table(
        [
            html.Thead(
                [
                    html.Tr(
                        [
                            html.Th(month_name, colSpan=7),
                        ]
                    ),
                    html.Tr([html.Th(month) for month in day_of_week_arrb.split()]),
                ]
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(
                                day,
                                id={"type": "day-calendar", "id": col + (7 * row)},
                                disable_n_clicks=(
                                    True
                                    if day == ""
                                    else disable_clicks(
                                        year_selected, month_selected, day, date.today()
                                    )
                                ),
                                className=(
                                    None
                                    if day == ""
                                    else init_style_calendar(
                                        "{year}-{month:0>2}-{day:0>2}".format(
                                            year=year_selected,
                                            month=month_selected,
                                            day=day,
                                        ),
                                        date.today(),
                                    )
                                ),
                                **{
                                    "data-date": (
                                        "{year}-{month:0>2}-{day:0>2}".format(
                                            year=year_selected,
                                            month=month_selected,
                                            day=day,
                                        )
                                        if day != ""
                                        else None
                                    ),
                                    "data-prevent-initial": (
                                        True if col + (7 * row) == 0 else None
                                    ),
                                },
                            )
                            for col, day in enumerate(week)
                        ]
                    )
                    for row, week in enumerate(calendar_weeks)
                ]
            ),
        ], id="calendar-table"
    )


def disable_clicks(year, month, day, today) -> bool:

    date_ = date(year, month, int(day))

    if date_ > today:
        return True
    else:
        return False


def init_style_calendar(date_data, today: date) -> str:

    date_ = datetime.strptime(date_data, "%Y-%m-%d").date()
    if date_ == today:
        return "calendar-cell today-style"
    elif date_ > today:
        return "disabled-style"

    return "calendar-cell"


@callback(
    [
        Output("date-selected-store", "data", allow_duplicate=True),
        Output({"type": "day-calendar", "id": ALL}, "data-prevent-initial"),
    ],
    Input({"type": "day-calendar", "id": ALL}, "n_clicks"),
    State("date-selected-store", "data"),
    State({"type": "day-calendar", "id": ALL}, "data-date"),
    State({"type": "day-calendar", "id": ALL}, "data-prevent-initial"),
    State("select-filter-store", "data"),
    prevent_initial_call=True,
)
def display_output(
    _,
    selected_dates: dict[str, str],
    selected_datas: list[str],
    prevent_first_initial: list[Optional[bool]],
    filter_mode,
) -> list[list[Optional[str]], list[Optional[bool]]]:
    selected_id = ctx.triggered_id.id
    selected_data = selected_datas[selected_id]

    if selected_data is None or prevent_first_initial[selected_id]:
        prevent_first_initial[selected_id] = None
        return [selected_dates, prevent_first_initial]

    selected_date = date.fromisoformat(selected_data)
    start_date = selected_dates.get("start-date")
    end_date = selected_dates.get("end-date")

    if start_date is None and end_date is None:
        selected_dates["start-date"] = selected_date
        selected_dates["end-date"] = selected_date
    else:
        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)

        if selected_date < start_date:
            selected_dates["start-date"] = selected_date
        elif selected_date > end_date:
            selected_dates["end-date"] = selected_date
        elif selected_date == start_date or selected_date == end_date:
            selected_dates["start-date"] = selected_date
            selected_dates["end-date"] = selected_date
        else:
            if filter_mode["select-filter"] == "start":
                selected_dates["start-date"] = selected_date
            elif filter_mode["select-filter"] == "end":
                selected_dates["end-date"] = selected_date

    return [selected_dates, prevent_first_initial]


@callback(
    Output({"type": "day-calendar", "id": ALL}, "className"),
    Input("date-selected-store", "modified_timestamp"),
    State("date-selected-store", "data"),
    State({"type": "day-calendar", "id": ALL}, "data-date"),
    State({"type": "day-calendar", "id": ALL}, "className"),
)
def style_select_date(
    _,
    data_selected: dict,
    all_dates_data: list[str],
    all_class_name: list[str],
):
    today = date.today()
    start_date = data_selected.get("start-date")
    end_date = data_selected.get("end-date")

    if not start_date and not end_date:
        return [
            init_style_calendar(date_data, today) if date_data else None
            for date_data in all_dates_data
        ]

    selected_date_min = date.fromisoformat(start_date)
    selected_date_max = date.fromisoformat(end_date)

    for i, date_data in enumerate(all_dates_data):
        if not date_data:
            continue

        class_name_date = init_style_calendar(date_data, today)
        all_class_name[i] = class_name_date

        if class_name_date == "disabled-style":
            continue

        date_obj = date.fromisoformat(date_data)

        if selected_date_min < date_obj < selected_date_max:
            all_class_name[i] += " in-range-style"
        elif date_obj in (selected_date_min, selected_date_max):
            all_class_name[i] += " clicked-style"

    return all_class_name


if __name__ == "__main__":
    ...
