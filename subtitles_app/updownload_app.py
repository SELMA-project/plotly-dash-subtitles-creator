import base64
import os
from urllib.parse import quote as urlquote

from flask import Flask, send_from_directory
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


APP_DATA_DIR = f"{os.environ['DATA_DIR']}/app_data"
SUBTITLES_DIR = f"{os.environ['DATA_DIR']}/subtitles_data"

if not os.path.exists(APP_DATA_DIR):
    os.makedirs(APP_DATA_DIR)

if not os.path.exists(SUBTITLES_DIR):
    os.makedirs(SUBTITLES_DIR)


# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
# server = Flask(__name__)
# app = dash.Dash(server=server)


def save_file(name, content, date):
    """Decode and store a file uploaded with Plotly Dash."""
    # print(f"date: {date}")
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(APP_DATA_DIR, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(APP_DATA_DIR):
        path = os.path.join(APP_DATA_DIR, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)


# html.Li(file_download_link(filename))
