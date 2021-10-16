import os
from dataclasses import asdict
from pathlib import Path

import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from tilosutils import data_io

from subtitles_app.app import app
from subtitles_app.common import get_letters_csv, raw_transcript_name, get_store_data
from subtitles_app.subtitles_table import process_button
from subtitles_app.updownload_app import APP_DATA_DIR, SUBTITLES_DIR
from speech_to_text.create_subtitle_files import TranslatedTranscript
from speech_to_text.subtitle_creation import convert_to_wav_transcribe
from speech_to_text.transcribe_audio import SpeechToText

NO_NAME = "enter some name here"

transcribe_button = dbc.Button(
    "transcribe",
    id="create-raw-transcripts-button",
    n_clicks=0,
    color="primary",
)

new_text_area_form = dbc.Form(
    [
        dbc.FormGroup(
            [
                dbc.Label("Name", className="mr-2"),
                dbc.Input(type="name", id="new-transcript-name", placeholder=NO_NAME),
            ],
            className="mr-3",
        ),
        dbc.Button("create new transcript", id="new-transcript-button"),
    ],
    inline=True,
)


def create_or_load_raw_transcript(video_file, model_name) -> str:
    file = Path(f"{APP_DATA_DIR}/{video_file}")
    raw_transcript_file = (
        f"{SUBTITLES_DIR}/{file.stem}_{raw_transcript_name(model_name)}.txt"
    )
    if not os.path.isfile(raw_transcript_file):
        asr = SpeechToText(
            model_name=model_name,
        ).init()
        transcript = convert_to_wav_transcribe(asr, str(file))
        data_io.write_lines(
            get_letters_csv(video_file, model_name),
            [f"{l.letter}\t{l.r_idx}" for l in transcript.letters],
        )

        raw_transcript = "".join([l.letter for l in transcript.letters])
        data_io.write_lines(
            raw_transcript_file,
            [raw_transcript],
        )
    else:
        raw_transcript = list(data_io.read_lines(raw_transcript_file))[0]
    return raw_transcript


@app.callback(
    Output("raw-transcript", "children"),
    Input("create-raw-transcripts-button", "n_clicks"),
    State("video-file-dropdown", "value"),
    State("asr-model-dropdown", "value"),
)
def calc_raw_transcript(
    n_clicks, video_file, asr_model
):

    if n_clicks > 0:
        raw_transcript = create_or_load_raw_transcript(video_file, asr_model)
    else:
        print(f"DEBUG: not updating raw_transcript")
        raise PreventUpdate
    return raw_transcript
    # html.H2("raw transcript"),
    # dbc.Row(, style={"padding-top": 20}),


@app.callback(
    Output("dependent_on_raw_transcript", "children"),
    Input("raw-transcript", "children"),
)
def dependent_on_raw_transcript(_):
    return [
        dbc.Row(html.H2("transcript alignment"), style={"padding-top": 20}),
        dbc.Row(dbc.Col(process_button, width={"size": 6, "offset": 4})),
        dbc.Row(id="subtitles-text-area", style={"padding-top": 20}),
        dbc.Row(dbc.Col(id="languages-text-areas"), style={"padding-top": 20}),
        dbc.Row(
            new_text_area_form,
            style={"padding-top": 20},
        ),
    ]


@app.callback(
    Output("languages-text-areas", "children"),
    Input("transcripts-store", "data"),
    Input("new-transcript-button", "n_clicks"),
    Input("raw-transcript", "children"),
    State("new-transcript-name", "value"),
    State("asr-model-dropdown", "value"),
)
def update_text_areas(store_s: str, n_clicks, raw_transcript, new_name, asr_model):
    store_data = get_store_data(store_s)
    print(f"store-data: {[asdict(v) for v in store_data.values()]}")

    if "spoken" in store_data.keys():
        transcripts = list(store_data.values())
    elif raw_transcript is not None:
        transcripts = [TranslatedTranscript("spoken", 0, raw_transcript)]
    else:
        print(f"DEBUG: not updating text_areas")
        raise PreventUpdate

    if new_name is not None and new_name != NO_NAME:
        transcripts.append(
            TranslatedTranscript(new_name, len(transcripts), "enter text here")
        )

    rows = []
    for sd in sorted(transcripts, key=lambda x: x.order):
        rows.append(dbc.Row(html.H5(sd.name)))
        rows.append(
            dbc.Row(
                dbc.Textarea(
                    title=sd.name,
                    id={"type": "transcript-text", "name": sd.name},
                    value=sd.text,
                    style={"width": "90%", "height": 200, "fontSize": 11},
                )
            )
        )
    return rows
