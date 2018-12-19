import os
import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=["GET", "POST"])
def index():
	if request.method == 'POST':
	    session.pop('user', None)
	if 'user' in session:
		return redirect(url_for('chats'))
	return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form.get("username")
		password = request.form.get("password")
		login = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone()
		if login == []:
			return render_template("bad.html")
		else:
			session['user'] = username
			session['id'] = login.id
			return redirect(url_for('chats'))
	return render_template("login.html")

@app.route("/registration", methods=['GET', 'POST'])
def registration():
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password")
		login = db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": username, "password": password})
		db.commit()
		return render_template("success.html")
	return render_template("registration.html")

@app.route("/chats")
def chats():
		mychats = db.execute("SELECT * FROM chats WHERE creatorid = :creatorid", {"creatorid": session.get('id')}).fetchall()
		notmychats = db.execute("SELECT * FROM chats WHERE addedid = :addedid", {"addedid": session.get('id')}).fetchall()
		return render_template("chats.html",  mychats=mychats, notmychats=notmychats, username=session.get('user', ''))


@app.route("/addchat", methods=['GET', 'POST'])
def addchat():
		if request.method == 'POST':
			add = db.execute("SELECT id FROM users WHERE username = :username", {"username": request.form.get("add")}).fetchone()
			name = request.form.get("name")
			me = session.get("id")
			#print(me, name, add.id)
			db.execute("INSERT INTO chats (name, creatorid, addedid) VALUES (:name, :creatorid, :addedid)", {"name": name, "creatorid": me, "addedid": add.id})
			db.commit()
			return redirect(url_for('chats'))
		return render_template("addchat.html") 


@app.route("/chat/<chat_id>")
def chat(chat_id):
	chat = db.execute("SELECT name, creatorid, addedid FROM chats WHERE id = :chat_id", {"chat_id": chat_id}).fetchone()
	for cha in chat:
		print(cha)
	masseges = db.execute("SELECT * FROM masseges WHERE chat_id = :chat_id", {"chat_id": chat_id}).fetchall()
	#for massege in masseges:
	#	print(massege)
	return render_template("chat.html", username=session.get('user', ''), chat_id=chat_id, chat=chat, masseges=masseges)

@socketio.on("send message")
def vote(data):
    user = session.get('user').lower() #data["user"]
    text = data["text"]
    chat_id = data["chat_id"]
    userid = db.execute("SELECT * FROM users WHERE username = :username", {"username": user}).fetchone()
    print(userid.id)
    db.execute("INSERT INTO masseges (chat_id, sender_id, text) VALUES (:chat_id, :sender_id, :text)", {"chat_id": chat_id, "sender_id": userid.id, "text": text})
    db.commit()
    emit("return massege", {'user': user, 'text': text, 'chat_id': chat_id}, broadcast=True)



