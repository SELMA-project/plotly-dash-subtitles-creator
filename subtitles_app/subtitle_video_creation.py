import json
import subprocess
from pathlib import Path
from pprint import pprint
from tempfile import NamedTemporaryFile
import dash_html_components as html

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dash_app.app import app
from dash_app.common import get_store_data
from dash_app.updownload_app import APP_DATA_DIR
from speech_to_text.create_subtitle_files import (
    create_ass_file,
    SubtitleBlock,
    StyleConfig,
)
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from urllib.parse import quote as urlquote

burn_video_div = html.Div(id="burn_into_video_form")


@app.callback(
    Output("burn_into_video_form", "children"),
    Input("subtitle-store", "data"),
)
def update_radio_selection(store_s):
    subtitle_blocks = [SubtitleBlock(**d) for d in json.loads(store_s)]
    options = [{"label": name, "value": name} for name in subtitle_blocks[0].names]
    assert len(options) > 0
    burn_into_video_form = dbc.Row(
        [
            dbc.Col(
                [
                    html.H5("Choose transcripts"),
                    dcc.Checklist(id="transcripts-radio-selection", options=options),
                ]
            ),
            dbc.Col(
                dbc.Button(
                    "burn into video",
                    id="burn-into-video-button",
                    n_clicks=0,
                    color="primary",
                )
            ),
        ]
    )

    return burn_into_video_form


@app.callback(
    Output("video-player-subs", "children"),
    Input("burn-into-video-button", "n_clicks"),
    State("subtitle-store", "data"),
    State("transcripts-radio-selection", "value"),
    State("video-file-dropdown", "value"),
)
def burn_into_video_button(n_clicks, store_s, selection, video_file_name):
    if store_s is None or n_clicks == 0:
        raise PreventUpdate

    video_file = Path(f"{APP_DATA_DIR}/{video_file_name}")
    video_subs_file_name = (
        f"{Path(video_file_name).stem}_{'_'.join(selection)}_subs.mp4"
    )

    def select(sb: SubtitleBlock, selection):
        sb.name_texts = [(n, t) for n, t in sb.name_texts if n in selection]
        return sb

    subtitle_blocks = [
        select(SubtitleBlock(**d), selection) for d in json.loads(store_s)
    ]

    with NamedTemporaryFile(suffix=".ass") as f:
        create_ass_file(
            subtitle_blocks,
            f.name,
            styles={name: StyleConfig(fontsize=20.0) for name in selection},
        )
        subprocess.check_output(
            f"/usr/bin/ffmpeg -y -i '{video_file}' -vf ass={f.name} '{APP_DATA_DIR}/{video_subs_file_name}'",
            shell=True,
        )
    return [
        html.H5(f"{video_subs_file_name}"),
        html.Video(
            controls=True,
            id="movie_player",
            src=f"/files/{video_subs_file_name}",
            autoPlay=False,
            style={"width": "100%"},
        ),
        html.Li(
            html.A(
                "download video-file",
                href=f"/download/{urlquote(video_subs_file_name)}",
            )
        ),
    ]
