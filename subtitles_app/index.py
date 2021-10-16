import sys

sys.path.append(".")

from subtitles_app.main_page import page_content
from subtitles_app.app import server, app

import dash_core_components as dcc
import dash_html_components as html
from flask import send_from_directory
import dash_bootstrap_components as dbc

from subtitles_app.updownload_app import (
    APP_DATA_DIR,
)


@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(APP_DATA_DIR, path, as_attachment=True)


@server.route("/files/<path:path>")
def serve_static(path):
    return send_from_directory(APP_DATA_DIR, path, as_attachment=False)


app.layout = html.Div(
    [
        dbc.Container(
            page_content,
        ),
        dcc.Store(id="transcripts-store"),
        dcc.Store(id="subtitle-store"),
        dcc.Store(id="load-dumped-data-signal"),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
