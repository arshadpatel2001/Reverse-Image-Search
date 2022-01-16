import os

import cv2
from PIL import Image
from flask import Flask, render_template, request

from search.colordescriptor import ColorDescriptor
from search.searcher import Searcher

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

# create flask instance
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'database')
app.config['TEMP_UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}

INDEX = os.path.join(os.path.dirname(__file__), 'index.csv')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# main route
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        if 'query_img' not in request.files or request.files['query_img'].filename == '' or not allowed_file(
                request.files['query_img'].filename):
            return render_template('home.html')
        file = request.files['query_img']
        img = Image.open(file.stream)  # PIL image
        uploaded_img_path = os.path.join(THIS_FOLDER, app.config['TEMP_UPLOAD_FOLDER'], file.filename)
        img.save(uploaded_img_path)
        # initialize the image descriptor
        cd = ColorDescriptor((8, 12, 3))
        # load the query image and describe it
        query = cv2.imread(uploaded_img_path)
        features = cd.describe(query)
        # perform the search
        searcher = Searcher(INDEX)
        answers = searcher.search(features)
        # for i in answers:
        #     print(i)
        return render_template('home.html',
                               query_path=os.path.join(app.config['TEMP_UPLOAD_FOLDER'], file.filename),
                               answers=answers)
    else:
        return render_template('home.html')

# run!
if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
