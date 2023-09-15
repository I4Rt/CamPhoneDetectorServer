from flask import Flask, request, make_response, render_template, redirect, url_for
from time import time
from flask_jwt_extended import *
from flask_cors import CORS, cross_origin
from FileUtil import *
from datetime import datetime
import json
import os
import flask_login
import shutil

directory = os.getcwd()

app = Flask(__name__, template_folder='templates', static_folder='images',static_url_path = '')

# auth
app.secret_key = 'U wont guess it'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


app.config['TIME'] = time()
app.config['CORS_HEADERS'] = 'Content-Type'
UPLOAD_FOLDER = directory + '/images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

cors = CORS(app)

users = {'admin': {'password': 'password'}}
class User(flask_login.UserMixin):
    pass

def deleteForce(path):
    for root, dirs, files in os.walk(path, topdown=False):
        print(len(dirs), len(files))
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))



@login_manager.user_loader
def user_loader(login):
    if login not in users:
        return
    user = User()
    user.id = login
    return user

@login_manager.request_loader
def request_loader(request):
    login = request.form.get('login')
    if login not in users:
        return
    user = User()
    user.id = login
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', class_ ='', message='')

    login = request.form['login']
    if login in users and request.form['password'] == users[login]['password']:
        user = User()
        user.id = login
        flask_login.login_user(user)
        return redirect(url_for('getMain'))
    return render_template('login.html', class_ ='text-danger', message='Неверные данные')

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('login.html', class_ ='text-dark', message='Вы вышли из аккаунта')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('login.html', class_ ='', message='')

@cross_origin
@app.route('/setWarning', methods=['get', 'post'])
def setWarning():
    now = datetime.now()
    curTime = now.strftime("%d_%m_%Y___%H_%M_%S")
    print(curTime)
    try:
        
        sender = request.remote_addr
        # sender.replace('.', '_')
        userName = request.json['clientName']
        encImg = request.json['img']
    except Exception:
        print({'Message': 'Json is not valid'})
        return make_response({'Message': 'Json is not valid'})
    
    try:
        image = FileUtil.convertBytesToImg(encImg)
        if image is None:
            return make_response({'Message': 'Image decoding error'})
    except:
        return make_response({'Message': 'Image invalid encoding'})
    
    # Path 
    path = os.path.join(directory, 'images')
    path = os.path.join(path, sender) 
    if not os.path.exists(path):
        os.mkdir(path)
        with open(directory + f'/images/{path}/data.txt', 'w') as file:
            file.write(json.dumps({'userName': userName}))
    # print(path)
    # print(sender)
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

# page
@app.route('/main')
@flask_login.login_required
def getMain():
    try:
        # request.json['param']
        selected = request.args.get('selectedUser')
    except:
        selected = None
    try:
        selectedWarn = request.args.get('warnName')
    except:
        selectedWarn = None
    print(selectedWarn)
    
    userList = []
    for path in os.listdir(os.path.join(directory, 'images')):
        try:
            if path != "sys":
                with open(directory + f'/images/{path}/data.txt', 'r') as file:
                    data = json.loads(file.read())
                user = [path, data['userName']] 
                userList.append(user)
        except Exception as e:
            print(e)
            
    warns = []
    imgSrc = ""
    if selected != None:
        warns = [[path, f'{path[0:2]}/{path[3:5]}/{path[6:10]} {path[13:15]}:{path[16:18]}:{path[19:21]}'] for path in os.listdir(os.path.join(directory, f'images/{selected}/images'))]
        if selectedWarn != None:
            imgSrc = f'{selected}/images/{selectedWarn}'
            
    return render_template('main.html', users = userList, warnings = warns, curUser=selected,img=imgSrc)

@app.route('/del')
def delete():
    try:
        # request.json['param']
        imgPath = request.args.get('imgPath')
        print(f'removing: {directory + "/images/" +imgPath}')
        os.remove(directory + '/images/' +imgPath)
        print('len is', len(os.listdir(os.path.join(directory, 'images/' + imgPath[:-25]))), directory + '/images/' + imgPath[:-25])
        if len(os.listdir(os.path.join(directory, 'images/' + imgPath[:-25]))) == 0:
            print(directory + '/images/' + imgPath[:-32])
            shutil.rmtree(directory + '/images/' + imgPath[:-32])
            return redirect(url_for('getMain'))
        return getMain()
    except Exception as e:
        print(e)
        return """
                <html>
                    <head>
                        title>Опаньки...</title>
                    </head>
                    <body>
                        <h3>Что-то пошло не так...</h3>
                        <p>Мы уже работаем над этим</p>
                        <a href='/main'>Назад</a>
                    </body>
               """
    
        
    

with app.app_context():
    app.run(host='0.0.0.0', debug=True)
            
    
    #image = cv2.imread('test.jpg')
    # vidcap = cv2.VideoCapture(0)
    # success,image = vidcap.read()
    # with open('data.json', 'w') as file:
    #     file.write(json.dumps({'ip':'192.168.0.127', 'img':convertImageToBytes(image)}))
    # vidcap.release()
    