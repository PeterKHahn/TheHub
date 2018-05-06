import sys
import os

from flask import Flask, render_template, jsonify, request
import flask
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import date

import google.oauth2.credentials
import google_auth_oauthlib.flow


from oauth2client import file, client, tools


import cafe
import calendar_update
import gmail



# https://developers.google.com/api-client-library/python/auth/web-app
app = Flask(__name__)

today = date.today().day

#cafe.write_to_file()
menu = cafe.read_from_file()

CLIENT_SECRETS_FILE = "secrets/client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/gmail.readonly']

app.secret_key = os.urandom(24)



def init():
    """
    Initializes the server by relading the menu, starting the scheduler, and
    any other initializations that need to be made
    """
    print("Starting...")
    reload_menu()
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        func=reload_menu,
        trigger=CronTrigger(minute="*"),
        id='menu_job',
        name='reload the menu every hour',
        replace_existing=True)

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

@app.route("/")
def server():
    """
    Returns the main page, at index.html, that the server is based at
    """
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    return render_template('index.html')

def get_creds():
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])
    return credentials


@app.route('/authorize')
def authorize():
    # Use the client_secret.json file to identify the application requesting
    # authorization. The client ID (from that file) and access scopes are required.
    #gmail = 'https://www.googleapis.com/auth/gmail'
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'secrets/client_secret.json',
        scopes=SCOPES)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state
    return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():

  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      'secrets/client_secret.json', scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  print("Putting credentials in flask.session")
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('server'))


@app.route("/get_menu", methods=["POST"])
def get_menu():
    """
    A call to this post method returns a jsonified version of the menu that
    can be parsed from the javascript to be displayed on the webpage
    """
    #reload_menu()
    return jsonify(menu)

@app.route("/add_to_calendar", methods=['POST'])
def add_to_calendar():
    """
    A POST method that, given queries for 'eventName' and 'when', will add
    the post to the event calendar. Returns a String of the success of the
    posting of the calendar event
    """
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    event_name = request.form.get("eventName")
    when = request.form.get("when")
    creds = get_creds()
    return calendar_update.add_to_calendar(creds, event_name, when)

@app.route("/retrieve_calendar", methods=['POST'])
def retrieve_calendar():
    if 'credentials' not in flask.session:
        print("Inside if statement...")
        return flask.redirect('authorize')
    print("Getting creds...")
    creds = get_creds()
    return jsonify(calendar_update.retrieve_calendar_events(creds, 20))
@app.route("/retrieve_piazza", methods=['POST'])
def piazza():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    creds = get_creds()
    res = gmail.get_piazza(creds)
    return jsonify(res)

def reload_menu():
    """
    Reloads the menu by writing to the file from cafe by querying the
    Brown Dining JSON, and then sets menu to the value of menu
    """
    global today

    if not today  == date.today().day:
        today = date.today().day
        print("Reloading menu")
        cafe.write_to_file()
        global menu
    menu = cafe.read_from_file()

def credentials_to_dict(credentials):
  print(credentials.client_id)
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


if __name__ == "__main__":
    print("Starting server from main...")
    init()
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    #piazza()

    app.run()
