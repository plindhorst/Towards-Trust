import json
import logging
import os
import shutil
import threading
from datetime import datetime
import glob

import numpy as np
import requests
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, send_file

'''
This file holds the code for the MATRX RESTful api. 
External scripts can send POST and/or GET requests to retrieve state, tick and other information, and send 
userinput or other information to MATRX. The api is a Flask (Python) webserver.

For visualization, see the seperate MATRX visualization folder / package.
'''
debug = True
templateType = ""
port = 3000
app = Flask(__name__, template_folder='templates')
running = False
# the path to the media folder of the user (outside of the MATRX package)
ext_media_folder = ""


#########################################################################
# Visualization server routes
#########################################################################

@app.route('/experiment')
def human_agent_view():
    requests.get("http://localhost:3001/start")

    global running
    running = True

    if templateType == "helper":
        return render_template('human_agent_helper.html', id="human_in_team")
    elif templateType == "friendly":
        return render_template('human_friendly_agent.html', id="human_in_team")
    elif templateType == "friendly-dutch":
        return render_template('human_friendly_agent_dutch.html', id="human_in_team")
    elif templateType == "tutorial-dutch":
        return render_template('human_agent_dutch.html', id="human_in_team")
    else:
        return render_template('human_agent.html', id="human_in_team")


@app.route('/god')
def god():  # TODO: remove this
    return render_template('god.html')


@app.route('/data')
def get_results():
    if not os.path.exists("./data"):
        return jsonify(False)
    shutil.make_archive('data', 'zip', "./data")
    if os.path.isfile('./data.zip'):
        return send_file('../data.zip')
    else:
        return jsonify(False)


@app.route('/consent_form')
def consent_form():
    file_name = "./world/visualizer/static/consent_form.pdf"
    if os.path.isfile(file_name):
        return send_file("static/consent_form.pdf")
    else:
        return jsonify(False)


@app.route('/')
def start_view():
    """
    Route for the 'start' view which shows information about the current scenario, including links to all agents.

    Returns
    -------
    str
        The template for this view.

    """
    global running
    if not running:
        return render_template('main.html')
    else:
        return render_template('error.html')


@app.route('/questionnaire')
def questionnaire():
    f = open('./trustworthiness/questionnaire.json')
    questionnaire_json = json.load(f)
    f.close()
    return render_template('questionnaire.html', data=questionnaire_json)


@app.route('/questionnaire_answers', methods=['GET', 'POST'])
def questionnaire_answers():
    answers = []
    for question in request.args:
        answers.append({question: request.args[question]})
    result_folder = os.getcwd() + "/data/questionnaire/"
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    list_of_files = glob.glob('./data/actions/*.pkl')
    if len(list_of_files) > 0:
        file_dates = []

        for file in list_of_files:
            file = file.replace("\\", "/")
            file_date = file[file.find("/") + 1:].replace(".pkl", "")
            file_date = file_date[file_date.find("_") + 1:].replace("-", "")
            file_dates.append(int(file_date))
        latest_file = list_of_files[np.argmax(file_dates)]

        file_name = latest_file.replace("\\", "/").split("/")[-1].replace(".pkl", ".json")
    else:
        file_name = "unknown_" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".json"

    if os.path.isfile(result_folder + file_name):
        file_name = "unknown_" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".json"

    print("Saved questionnaire: " + file_name)
    result_file = result_folder + file_name
    result_file = result_file.replace("\\", "/")
    with open(result_file, 'w+') as outfile:
        outfile.write(json.dumps(answers))

    return redirect('/done')


@app.route('/done')
def done():
    return render_template('done.html')


@app.route('/shutdown_visualizer', methods=['GET', 'POST'])
def shutdown():
    """ Shuts down the visualizer by stopping the Flask thread

    Returns
        True
    -------
    """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Unable to shutdown visualizer server. Not running with the Werkzeug Server')
    func()
    print("Visualizer server shutting down...")
    return jsonify(True)


@app.route('/is_done', methods=['GET', 'POST'])
def is_done():
    global running
    return jsonify(not running)


@app.route('/set_done')
def set_done():
    global running
    running = False
    return jsonify(True)


@app.route('/fetch_external_media/<path:filename>')
def external_media(filename):
    """ Facilitate the use of images in the visualization outside of the static folder

    Parameters
    ----------
    filename
        path to the image file in the external media folder of the user.

    Returns
    -------
        Returns the url (relative from the website root) to that file
    """
    return send_from_directory(ext_media_folder, filename, as_attachment=True)


#########################################################################
# Visualization Flask methods
#########################################################################

def _flask_thread():
    """
    Starts the Flask server on localhost:3000
    """
    if not debug:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


def run_matrx_visualizer(template, verbose, media_folder):
    """
    Creates a seperate Python thread in which the visualization server (Flask) is started, serving the JS visualization
    :return: MATRX visualization Python thread
    """
    global debug, ext_media_folder, templateType
    templateType = template

    debug = verbose
    ext_media_folder = media_folder

    print("Starting visualization server")
    print("Initialized app:", app)
    vis_thread = threading.Thread(target=_flask_thread)
    vis_thread.start()
    return vis_thread
