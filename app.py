# -*- coding: utf-8 -*-

# Usage:
# $ export FLASK_APP=plot_with_template.py
# $ flask run

# Thanks to SO for getting me started
# https://stackoverflow.com/questions/20107414/passing-a-matplotlib-figure-to-html-flask
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import io
import os
import pickle 
import pandas as pd
import numpy as np
import requests
from flask import Flask, make_response, send_file, render_template


METER_PER_SEC_TO_MILE_PER_MIN = 0.03728
TYPES = ','.join(['latlng', 'time', 'distance'])

app = Flask(__name__)

def poll_strava(activity_id):
    if os.environ.get('FLASK_DEBUG'):
        print('Debug: loading pickle')
        with open('1385640587.pickle', 'rb') as f:
            y = pickle.load(f)
    else:
        get_url = f'https://www.strava.com/api/v3/activities/{activity_id}/streams/{TYPES}'
        r = requests.get(get_url,
                         params={'access_token': os.environ.get('ACCESS_TOKEN')})
        y = r.json()
    return y 

def get_dist_df(activity_id):
    activity_stream = poll_strava(activity_id)

    # It's global!
    global dist_df
    dist_df = pd.DataFrame({
        'time': activity_stream[1]['data'],
        'distance': activity_stream[2]['data'],
        })
    dist_df['speed'] = dist_df.distance.diff()/dist_df.time.diff()
    dist_df['smoothed_speed'] = dist_df.speed.rolling(5).mean()

def figure_to_bytes(figure):
    """Convert a matplotlib figure to bytes"""
    image_bytes = io.BytesIO()
    figure.savefig(image_bytes, format='png')
    image_bytes.seek(0)

    return image_bytes

@app.route('/')
def home_message():
    message = """
    Welcome to my plots API. 
    Go to /activities/ACTIVITY_ID to see the magic.
    """
    return message

@app.route('/activities/<activity_id>')
def activities(activity_id):
    """Kick off the requests and the plots html template"""
    get_dist_df(activity_id)
    return render_template('plots.html', activity=activity_id)

@app.route('/paceplot')
def paceplot():
    """Generate pace plot"""
    pace_fig = plt.figure(figsize=(7,2))
    ax = pace_fig.add_subplot(111)
    # ax = dist_df.plot(x='time', y='smoothed_speed')
    ax.plot(dist_df['time']/60, dist_df['smoothed_speed'])
    # ax.legend_.remove()
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Pace (m/s)')

    return send_file(figure_to_bytes(pace_fig), mimetype='image/png')

@app.route('/pacehist')
def pacehist():
    fig, ax = plt.subplots()
    (1/(dist_df.smoothed_speed*METER_PER_SEC_TO_MILE_PER_MIN)).hist(bins=20, ax=ax)
    plt.xlabel('Pace (min/mile)')

    return send_file(figure_to_bytes(fig), mimetype='image/png')

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    # app.config['TEMPLATES_AUTO_RELOAD'] = True 
    app.run(debug=True, host='0.0.0.0')