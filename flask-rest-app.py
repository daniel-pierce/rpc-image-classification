import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Gets rid of GPU errors from tensorflow

import numpy as np
from flask import Flask
from keras.models import load_model
from keras_preprocessing import image
from flask import flash, request, redirect
from werkzeug.utils import secure_filename
from werkzeug.middleware.shared_data import SharedDataMiddleware
from flask import render_template
from datetime import datetime


UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)           # initialize our Flask application
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

model = load_model('model.h5')  # Load the machine learning model globally


# Helper function
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Allows user to upload files in the browser if they want
@app.route('/client', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            img = image.load_img(filepath, target_size=(150, 150))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            images = np.vstack([x])
            classes = model.predict(images, batch_size=1)
            model_prediction = ""
            if str(classes[0]) == "[1. 0. 0.]":
                model_prediction = "paper"
            elif str(classes[0]) == "[0. 1. 0.]":
                model_prediction = "rock"
            elif str(classes[0]) == "[0. 0. 1.]":
                model_prediction = "scissors"
            return render_template('prediction.html', filename=filename, image_upload=filepath,
                                   prediction=model_prediction)
    return render_template('index.html')


# Setup for upload folder
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
})


# Route we will use for CLI file upload / server info component
@app.route("/", methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        posted_data = request.get_json()
        filepath = posted_data['image']
        img = image.load_img(filepath, target_size=(150, 150))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        images = np.vstack([x])
        classes = model.predict(images, batch_size=1)
        model_prediction = ""
        if str(classes[0]) == "[1. 0. 0.]":
            model_prediction = "paper"
        elif str(classes[0]) == "[0. 1. 0.]":
            model_prediction = "rock"
        elif str(classes[0]) == "[0. 0. 1.]":
            model_prediction = "scissors"
        json_prediction = {'prediction': model_prediction}
        return json_prediction
    else:
        server_info = {'title': "Rock,Paper and Scissors image classification server", 'name': "Daniel Pierce",
                       'date': datetime.today().strftime("%B %d, %Y")}
        return server_info


# Main thread / function to start the server
if __name__ == "__main__":
    app.run(debug=True)
    
