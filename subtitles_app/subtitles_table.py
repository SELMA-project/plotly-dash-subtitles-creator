import json
from dataclasses import asdict
from datetime import timedelta

import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.dependencies import Output, Input, State, ALL
from dash.exceptions import PreventUpdate
from data_io.readwrite_files import write_json

from subtitles_app.app import app
from subtitles_app.common import get_letters_csv, build_json_name
from speech_to_text.create_subtitle_files import (
    TranslatedTranscript,
    segment_transcript_to_subtitle_blocks,
    SubtitleBlock,
)
from speech_to_text.transcribe_audio import TARGET_SAMPLE_RATE

process_button = dbc.Button(
    "create subtitles",
    id="process-texts-button",
    n_clicks=0,
    color="primary",
)


@app.callback(
    Output("load-dumped-data-signal", "data"),
    Output("subtitles-text-area", "children"),
    Output("subtitle-store", "data"),
    Input("process-texts-button", "n_clicks"),
    State("video-file-dropdown", "value"),
    State({"type": "transcript-text", "name": ALL}, "value"),
    State({"type": "transcript-text", "name": ALL}, "title"),
    State("asr-model-dropdown", "value"),
)
def dump_to_disk_process_subtitles(n_clicks, video_file, texts, titles, model_name):
    print(f"video_file:{video_file}")
    assert all((isinstance(s, str) for s in texts))
    if n_clicks > 0 and video_file is not None:
        data = {
            title: TranslatedTranscript(title, k, text)
            for k, (title, text) in enumerate(zip(titles, texts))
        }
        write_json(
            build_json_name(video_file, model_name),
            {name: asdict(v) for name, v in data.items()},
        )

        named_blocks = segment_transcript_to_subtitle_blocks(
            get_letters_csv(video_file, model_name), list(data.values())
        )
        subtitles = dbc.Row(
            [
                dash_table.DataTable(
                    columns=[{"id": cn, "name": cn} for cn in ["start-time"] + titles],
                    data=[
                        {
                            **{
                                name: "".join([l.letter for l in b[name]])
                                for name in titles
                            },
                            **{
                                "start-time": str(
                                    timedelta(
                                        milliseconds=round(
                                            1000
                                            * b[titles[0]][0].r_idx
                                            / TARGET_SAMPLE_RATE
                                        )
                                    )
                                )
                            },
                        }
                        for b in named_blocks
                    ],
                    style_table={
                        "height": 200 * len(titles),
                        "overflowY": "scroll",
                        "width": "100%",
                        "font-size": 9,
                    },
                    style_cell={
                        # "overflow": "hidden",
                        # "textOverflow": "ellipsis",
                        # "maxWidth": 0,
                        "textAlign": "left",
                        "height": "auto",
                    },
                ),
            ],
            style={"width": "100%"},
        )
        return (
            "content-of-this-string-does-not-matter",
            [subtitles],
            json.dumps(
                [asdict(SubtitleBlock.from_dict_letters(dl)) for dl in named_blocks]
            ),
        )
    else:
        print(f"DEBUG: prevented to update dump_to_disk_process_subtitles")
        raise PreventUpdate
