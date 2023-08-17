from flask import Flask, request, make_response
from time import time
from flask_jwt_extended import *
from flask_cors import CORS, cross_origin
from FileUtil import *
from datetime import datetime
import json
import os
directory = os.getcwd()
app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path = '')
app.config['TIME'] = time()
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app)

@cross_origin
@app.route('/setWarning', methods=['get', 'post'])
def setWarning():
    now = datetime.now()
    curTime = now.strftime("%d_%m_%Y___%H_%M_%S")
    print(curTime)
    try:
        
        sender = request.remote_addr
        sender.replace('.', '_')
        encImg = request.json['img']
    except Exception:
        print({'Message': 'Json is not valid'})
        return make_response({'Message': 'Json is not valid'})
    
    try:
        image = convertBytesToImg(encImg)
        if image is None:
            return make_response({'Message': 'Image decoding error'})
    except:
        return make_response({'Message': 'Image invalid encoding'})
    
    # Path 
    path = os.path.join(directory, 'images')
    path = os.path.join(path, sender) 
    if not os.path.exists(path):
        os.mkdir(path)
    print(path)
    print(sender)
    try:
        result = cv2.imwrite(f'images/{sender}/{curTime}.jpg', image)
        if not result:
            print({'Message': 'Image saving error'})
            return make_response({'Message': 'Image saving error'})
    except Exception:
        print({'Message': 'Image saving error'})
        return make_response({'Message': 'Image saving error'})
    print({'Message': 'The warning has been added'})
    return make_response({'Message': 'The warning has been added'})

with app.app_context():
    app.run(host='0.0.0.0', debug=True)
    #image = cv2.imread('test.jpg')
    # vidcap = cv2.VideoCapture(0)
    # success,image = vidcap.read()
    # with open('data.json', 'w') as file:
    #     file.write(json.dumps({'ip':'192.168.0.127', 'img':convertImageToBytes(image)}))
    # vidcap.release()
    