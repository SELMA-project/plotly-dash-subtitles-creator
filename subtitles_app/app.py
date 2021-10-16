import dash
import dash_auth
import dash_bootstrap_components as dbc
from flask import Flask
from util import data_io

VALID_USERNAME_PASSWORD_PAIRS = {
    d["login"]: d["password"] for d in data_io.read_jsonl("credentials.jsonl")
}
server = Flask(__name__)
app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)
