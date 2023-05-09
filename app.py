from enum import unique
from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_bootstrap import BOOTSTRAP_VERSION, Bootstrap

from werkzeug.security import generate_password_hash, check_password_hash
import os

import datetime
import pytz
from io import BytesIO
from moviepy.editor import *
from pytube import YouTube
import pytube


#インスタンス化
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    #動画の開始時刻，終了時刻
    start = db.Column(db.Time, nullable=False)
    end = db.Column(db.Time, nullable=False)
    
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(12))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'GET':
        posts = Post.query.all()
        return render_template('index.html', posts=posts)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User(username=username, password=generate_password_hash(password, method='sha256'))

        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    else:
        return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect('/')
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        start = request.form.get('start')
        end = request.form.get('end')
        #文字列からdatetime型に変換
        new_start = datetime.datetime.strptime(start,"%H:%M:%S").time()
        new_end = datetime.datetime.strptime(end, '%H:%M:%S').time()
        post = Post(title=title, body=body, start=new_start, end=new_end)
        #dbに格納
        db.session.add(post)
        db.session.commit()

        return redirect('/')
    else:
        return render_template('create.html')
    
@app.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.title = request.form.get('title')
        post.body = request.form.get('body')

        post.start = request.form.get('start')
        post.end = request.form.get('end')
        new_start = datetime.datetime.strptime(post.start,"%H:%M:%S").time()
        new_end = datetime.datetime.strptime(post.end,"%H:%M:%S").time()
        
        post.start=new_start
        post.end=new_end
        
        db.session.commit()
        return redirect('/')

@app.route('/<int:id>/delete', methods=['GET'])
@login_required
def delete(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect('/')

@app.route('/<int:id>/save', methods=['GET','POST'])
@login_required
def save(id):
    post = Post.query.get(id)
    #秒数の取得
    start_seconds = post.start.hour * 3600 + post.start.minute * 60 + post.start.second
    end_seconds = post.end.hour * 3600 + post.end.minute * 60 + post.end.second
    video = VideoFileClip("/Users/yoshito0121/研究室/B4/卒業研究/ホッケー/Video/hockey_game.mp4")
    #動画の切り抜き
    clip_video =video.subclip(start_seconds, end_seconds)  
    #動画の保存
    clip_video.write_videofile("/Users/yoshito0121/研究室/B4/卒業研究/ホッケー/Analysis/result/" + str(post.body) + ".mp4")
    return redirect('/')

