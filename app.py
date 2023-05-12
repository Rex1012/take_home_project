from flask import Flask, redirect, url_for, session, request, jsonify, abort
from flask_oauthlib.client import OAuth


app = Flask(__name__)
app.config['GOOGLE_ID'] = "167568365839-7spds4ucsbm8drtms59dujibsav9c3vb.apps.googleusercontent.com"
app.config['GOOGLE_SECRET'] = "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"
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)


google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_ID'),
    consumer_secret=app.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.route('/')
def index():
    return "Hello World <a href='/login'><button>Login</button></a>"


@app.route('/login')
def login():
    redirect_uri = url_for('authorized', _external=True)
    return google.authorize(redirect_uri)


@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")


@app.route("/protected_area")
@login_is_required
def protected_area():
    return f"Hello Guest! Logged in successfully <br/> <a href='/logout'><button>Logout</button></a>"


@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_id'] = (resp['access_token'], '')
    return redirect("/protected_area")


if __name__ == '__main__':
    app.run()
