import json
import os
from json import load
from typing import Dict, Optional
from flask import Flask, request, redirect, render_template, send_file
from flask.helpers import flash, url_for
from werkzeug.utils import secure_filename
import tool
import splitter as dv
import encryption as enc
import decryption as dec
import rebuild as rst


from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)

UPLOAD_FOLDER = './uploads/'
UPLOAD_KEY = './key/'
ALLOWED_EXTENSIONS = set(['pem'])

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", default="secret_key_example")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_KEY'] = UPLOAD_KEY

login_manager = LoginManager(app)


users: Dict[str, "User"] = {}


class User(UserMixin):
    def __init__(self, id: str, username: str, password: str):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id: str) -> Optional["User"]:
        return users.get(user_id)

    def __str__(self) -> str:
        return f"<Id: {self.id}, Username: {self.username}>"

    def __repr__(self) -> str:
        return self.__str__()

with open("users.json") as file:
    data = load(file)
    for key in data:
        users[key] = User(
            id=key,
            username=data[key]["username"],
            password=data[key]["password"],
        )

@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    return User.get(user_id)

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def start_encryption(username):
	file_name = dv.divide(username)
	tool.empty_folder('uploads')
	enc.encryption(file_name)
	return render_template('success.html')

def start_decryption(file_name, username):
	is_same_user = check_user(file_name, username)
	if is_same_user:			
		dec.decryption()
		tool.empty_folder('key')
		rst.restore()
		return render_template('restore_success.html')
	return "<h1>Invalid user</h1>"

def check_user(filename, username):
	filename = filename.split(".")[0]
	with open('file_details/meta_data.txt','r') as file_data:
		lines = list(file_data)
		is_same_user = False
		for i in range(0, len(lines), 3):
			fname, user = lines[i].split("=")[1].split(".")[0], lines[i+2].split("=")[1].split(".")[0].strip()
			if fname == filename and user == username:
				is_same_user = True
				break
	return is_same_user

def append_user(user, password):
	id = str(len(users))
	user_data = User(id, user, password)
	json_user = {id: {
        "username": user,
        "password": password
    }}
	with open("users.json", "r+") as file:
		data = json.load(file)
		data.update(json_user)
		file.seek(0)
		json.dump(data, file)
	users[id] = user_data
	return user_data

@app.route('/return-key/My_Key.pem')
@login_required
def return_key():
	list_directory = tool.list_dir('key')
	filename = './key/' + list_directory[0]
	return send_file(filename, attachment_filename=list_directory[0])

@app.route('/return-file/')
@login_required
def return_file():
	list_directory = tool.list_dir('restored_file')
	filename = './restored_file/' + list_directory[0]
	print("****************************************")
	print(list_directory[0])
	print("****************************************")
	return send_file(filename, attachment_filename=list_directory[0], as_attachment=True)

@app.route('/download/')
@login_required
def downloads():
	return render_template('download.html')

@app.route('/upload')
@login_required
def call_page_upload():
	return render_template('upload.html')

@app.route('/home')
@login_required
def back_home():
	tool.empty_folder('key')
	tool.empty_folder('rebuild_file')
	return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route("/signup/pass", methods=['POST'])
def signup_data():
	if request.method == 'POST':
		user = request.form.get("name")
		password = request.form.get("password")
		user_data = append_user(user, password)
		login_user(user_data)
		return redirect(url_for("index"))
	return "<h1>Invalid user id or password</h1>"



@app.route("/login/pass", methods=['POST'])
def login_data():
	if request.method == 'POST':
		user_id = request.form.get("id")
		password = request.form.get("password")
		user_file = User.get(user_id)
		if user_file and user_file.password == password:
			login_user(user_file)
			return redirect(url_for("index"))
	return "<h1>Invalid user id or password</h1>"


@app.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/index')
@login_required
def index():
	return render_template('index.html')

@app.route('/data', methods=['GET', 'POST'])
@login_required
def upload_file():
	curr_user = current_user.username
	tool.empty_folder('uploads')
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			flash('No selected file')
			return 'NO FILE SELECTED'
		if file:
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
			return start_encryption(curr_user)
		return 'Invalid File Format !'
	
@app.route('/download_data', methods=['GET', 'POST'])
@login_required
def upload_key():
	curr_user = current_user.username
	tool.empty_folder('key')
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			flash('No selected file')
			return 'NO FILE SELECTED'
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_KEY'], file.filename))
			return start_decryption(filename, curr_user)
		return 'Invalid File Format !'

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8000, debug=True)
	