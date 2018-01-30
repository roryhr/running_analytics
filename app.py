# -*- coding: utf-8 -*-

# Usage:
# $ export FLASK_APP=plot_with_template.py
# $ flask run

# Thanks to SO for getting me started
# https://stackoverflow.com/questions/20107414/passing-a-matplotlib-figure-to-html-flask

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
from flask import Flask, make_response, send_file, render_template

app = Flask(__name__)

def generate_sample_plot():
    fig = plt.figure()
    ts = pd.Series(np.random.randn(1000), index=pd.date_range('1/1/2000', periods=1000))
    ts = ts.cumsum()
    ax_plot = ts.plot(ax=plt.gca())
    return fig

def figure_to_bytes(figure):
    """Convert a matplotlib figure to bytes"""
    image_bytes = io.BytesIO()
    figure.savefig(image_bytes)
    image_bytes.seek(0)
    return image_bytes

@app.route('/images/<cropzonekey>')
def images(cropzonekey):
    return render_template("images.html", title=cropzonekey)

@app.route('/fig/<cropzonekey>')
def fig(cropzonekey):
    fig = generate_sample_plot()
    return send_file(figure_to_bytes(fig), mimetype='image/png')

@app.route('/plot3')
def plot3():
    fig = generate_sample_plot()
    return send_file(figure_to_bytes(fig), mimetype='image/png')


if __name__ == "__main__":
    app.run()
