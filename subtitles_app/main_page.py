import json
import os
from pathlib import Path

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

from subtitles_app.app import app
from subtitles_app.common import LANGUAGE_TO_MODELNAME, build_json_name
from subtitles_app.subtitle_video_creation import burn_video_div
from subtitles_app.transcript_text_areas import transcribe_button
from subtitles_app.updownload_app import (
    save_file,
    uploaded_files,
    APP_DATA_DIR,
)
from data_io.readwrite_files import read_json

upload_data = "upload-data"
video_file_dropdown = "video-file-dropdown"
video_selection_upload = dbc.Row(
    [
        dbc.Col(
            html.Div(
                id="output-data-upload",
                children=[
                    html.Label(
                        [
                            "video-files",
                            dcc.Dropdown(id=video_file_dropdown),
                        ],
                        style={"width": "100%"},
                    )
                ],
            )
        ),
        dbc.Col(
            dcc.Upload(
                id=upload_data,
                children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                # Allow multiple files to be uploaded
                multiple=True,
            )
        ),
    ]
)
page_content = [
    html.H1("subtitles creator"),
    html.H5("select video-file in dropdown, if not there upload it!"),
    video_selection_upload,
    dbc.Row(
        [
            dbc.Col(
                html.Div(id="video-player"),
            ),
            dbc.Col(dbc.Spinner(html.Div(id="video-player-subs"))),
        ]
    ),
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Label("language"),
                    dcc.Dropdown(
                        id="asr-model-dropdown",
                        options=[
                            {"label": k, "value": v}
                            for k, v in LANGUAGE_TO_MODELNAME.items()
                        ],
                        value=LANGUAGE_TO_MODELNAME["spanish"],
                    ),
                ]
            ),
            dbc.Col(
                transcribe_button,
                style={"width": "100%", "padding-top": 40},
            ),
            dbc.Col(
                burn_video_div,
                style={"width": "100%"},
            ),
        ]
    ),
    dbc.Spinner(html.Div(id="raw-transcript", style={"fontSize": 10})),
    html.Div(id="dependent_on_raw_transcript"),
]

# @app.callback(
#     Output("language_dropdown", "children"),
#     Input("video-file-dropdown", "value"),
# )
# def update_language_dropdown(video_file):
#     language_dropdown = [
#         html.Label("language"),
#         dcc.Dropdown(
#             id="asr-model-dropdown",
#             options=[
#                 {"label": k, "value": v}
#                 for k, v in LANGUAGE_TO_MODELNAME.items()
#             ],
#             value=LANGUAGE_TO_MODELNAME["spanish"],
#         ),
#     ]
#     return language_dropdown

@app.callback(
    Output("transcripts-store", "data"),
    Input(video_file_dropdown, "value"),
    Input("load-dumped-data-signal", "data"),
    Input("asr-model-dropdown", "value"), # TODO: stuff this in some store!?
)
def update_store_data(video_file, _, model_name):
    print(f"DEBUG: update_store_data with video_file={video_file}")
    if video_file is not None and os.path.isfile(build_json_name(video_file, model_name)):
        return json.dumps(read_json(build_json_name(video_file, model_name)))
    else:
        raise PreventUpdate


@app.callback(
    Output(video_file_dropdown, "options"),
    Input(upload_data, "contents"),
    State(upload_data, "filename"),
    State(upload_data, "last_modified"),
)
def update_video_file_dropdown(contents, names, dates):
    if contents is not None:
        for name, data, date in zip(names, contents, dates):
            save_file(name, data, date)
    options = [
        {"label": Path(f).stem, "value": f}
        for f in uploaded_files()
        if not f.endswith("_subs.mp4")
    ]
    return options


@app.callback(
    Output("video-player", "children"),
    Input(video_file_dropdown, "value"),
)
def update_video_player(file):
    if file is not None:
        fullfile = f"{APP_DATA_DIR}/{file}"
        return [
            html.H5(f"{Path(fullfile).name}"),
            html.Video(
                controls=True,
                id="movie_player",
                src=f"/files/{file}",
                autoPlay=False,
                style={"width": "100%"},
            ),
        ]
    else:
        raise PreventUpdate