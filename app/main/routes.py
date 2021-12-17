from app.main.forms import *
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.models import Admin, User
from werkzeug.urls import url_parse
from app.functions import send_post
from app.main import bp
from telebot import TeleBot
from flask import current_app

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(username=form.username.data).first()
        if user is None or not user.password == form.password.data:
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title=('Sign In'), form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    user_count = User.query.count()
    if form.validate_on_submit():
        print(type(form.image.data))
        photo = None
        if form.image.data:
            with open(f'app/telegram_images/{form.image.data.filename}', 'wb') as f:
                f.write(form.image.data.stream.read())
            photo = f'app/telegram_images/{form.image.data.filename}'
        send_post(form.body.data, photo)
        flash('Рассылка началась')
        return redirect(url_for('main.index'))
    return render_template('index.html', title='Home', form=form, user_count=user_count)
