import dash
import dash_auth
import dash_bootstrap_components as dbc
from flask import Flask

from data_io.readwrite_files import read_jsonl

VALID_USERNAME_PASSWORD_PAIRS = {
    d["login"]: d["password"] for d in read_jsonl("credentials.jsonl")
}
server = Flask(__name__)
app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)
