from Devinci.handlers import *
from psutil import Process, cpu_percent
from os import getpid
from flask_login import login_required, current_user
from flask import Blueprint, Response, render_template, request

from Devinci.analysis.ROC import colourspace_similarity_test, ROC, _select_optimal_bounds, _optimaldict_vis
from Devinci.analysis.extract import Colour_Tag, _is_image
from Devinci.analysis.distribution import create

views = Blueprint("views", __name__)

JACCARDS = {name: None for name in camera_model.names()}
OPTIMALS = {name: None for name in camera_model.names()}

@views.route("/about", methods=['GET'])
def about() -> Response:
    return render_template("about.html", user = current_user)

@views.route('/system-info')
def system_info() -> Response:
    """
    Memory info and cpu usage in json return.
    """
    pid = getpid()
    memory_usage = f"{Process(pid).memory_info().rss / (1024 ** 2):.2f}"  # in MB
    cpu_usage = f"{cpu_percent():.2f}"
    return jsonify(memory_usage=memory_usage, cpu_usage=cpu_usage)

@views.route("/", methods=['GET', 'POST'])
# @login_required
def index():
    global JACCARDS
    global OPTIMALS
    
    jaccard = {"None":None}
    optimal = {"None": {"bound":None, "AUC": None}}
    cammodels = [camera_model.DSLR.name, camera_model.OV5640.name]
    
    if request.method == "POST":
        camera_str = request.form.get('camera-model-select')
        
        if not camera_str or camera_str != camera_model.UNKNOWN.name:
            model = camera_model.match(camera_str)
            CAM = Camera(model)
            
            histogram_paths = [os.path.join("..", "static", "Graphs", model.value, "hist", filename, ) for filename in os.listdir(CAM.histogram_folder) if _is_image(filename)]
            if len(histogram_paths) < 2:
                create(CAM, [Colour_Tag.HSV, Colour_Tag.YCRCB, Colour_Tag.RGB])
                histogram_paths = [os.path.join("..", "static", "Graphs", model.value, "hist", filename, ) for filename in os.listdir(CAM.histogram_folder) if _is_image(filename)]
            
            if not JACCARDS[model.name]:
                jaccard = colourspace_similarity_test(CAM, Colour_Tag.members())
                JACCARDS[model.name] = jaccard 
            else:
                jaccard = JACCARDS[model.name]
            
            if OPTIMALS[model.name] is None:
                roc = ROC(cam = model, jaccard = jaccard, STRATA_COUNT = 60, STRATA_SIZE = 30, SAMPLE_POINTS = None)
                optimal = _select_optimal_bounds(DATA = roc)
                OPTIMALS[model.name] = optimal
            else: 
                optimal = OPTIMALS[model.name]

        return render_template("index_selected.html",
                                user=current_user,
                                camera_models = cammodels,
                                selected_model = camera_str if camera_str else camera_model.DSLR.name,
                                jaccard = jaccard,
                                optimal = optimal,
                                histograms = histogram_paths
                            )
    
    elif request.method == "GET":
        return render_template("index.html",
                                user=current_user,
                                camera_models = cammodels,
                                selected_model = camera_model.DSLR.name,
                            )
