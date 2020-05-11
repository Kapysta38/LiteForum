import os
from flask import Flask, url_for, request, render_template, json, redirect, make_response, session, abort, jsonify
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from data import db_session, users, chats, comment
from flask_restful import Api
import users_resource
import chats_resource
import comment_resource

# создаём наше приложение
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


class LoginForm(FlaskForm):
    email = EmailField('Введите почту', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class ChatsForm(FlaskForm):
    title = StringField("Тема", validators=[DataRequired()])
    is_private = BooleanField("Запретить комментраии")
    submit = SubmitField('Создать')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class CommentForm(FlaskForm):
    commentaries = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField('Добавить комментарий')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(401)
def not_authenticated(error):
    return render_template('error.html', title='Ошибка', message='Авторизируйетесь для создания чата',
                           css_file=url_for('static', filename='css/style.css'))


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(users.User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def chats_list():
    if request.method == "GET":
        session = db_session.create_session()
        get_chats = session.query(chats.Chats).all()
        return render_template('chats.html', chats=get_chats, title='LiteForum',
                               css_file=url_for('static', filename='css/style.css'))
    elif request.method == "POST":
        session = db_session.create_session()
        get_chats = session.query(chats.Chats).filter(chats.Chats.title.like('%Новый форум 3%'))
        return render_template('chats.html', chats=get_chats, title='LiteForum',
                               css_file=url_for('static', filename='css/style.css'))


@app.route('/chats', methods=['GET', 'POST'])
@login_required
def add_chat():
    form = ChatsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        # добавили чат
        get_chats = chats.Chats()
        get_chats.title = form.title.data
        if session.query(chats.Chats).filter(chats.Chats.title == form.title.data).first():
            return render_template('add_chat.html', title='Создание чата',
                                   form=form,
                                   message="Чат с такой темой существует",
                                   css_file=url_for('static', filename='css/style.css'))
        get_chats.is_private = form.is_private.data
        current_user.chats.append(get_chats)
        # добавили первое сообщение в этом чате
        session.merge(current_user)
        session.commit()
        get_chats = session.query(chats.Chats).filter(chats.Chats.title == form.title.data).first()
        return redirect(f'/{get_chats.id}')
    return render_template('add_chat.html', title='Создание чата',
                           form=form, css_file=url_for('static', filename='css/style.css'))


@app.route('/comment/<int:id>', methods=['GET', 'POST'])
def add_comment(id):
    session = db_session.create_session()
    get_chat = session.query(chats.Chats).filter(chats.Chats.id == id).first()
    if get_chat:
        if not(get_chat.is_private) or current_user.id == get_chat.user_id:
            form = CommentForm()
            if form.validate_on_submit():
                if not form.commentaries.data:
                    return render_template('add_comment.html', title='Создание комментария', form=form,
                                           message='Нельзя добавить пустой комментарий',
                                           css_file=url_for('static', filename='css/style.css'))
                session = db_session.create_session()
                get_comm = comment.Comment()
                get_comm.author = current_user.name
                get_comm.text = form.commentaries.data
                get_comm.chat_id = id
                current_user.comment.append(get_comm)
                session.merge(current_user)
                session.commit()
                return redirect(f'/{id}')
            return render_template('add_comment.html', title='Создание комментария', form=form,
                                   css_file=url_for('static', filename='css/style.css'))
        return render_template('error.html', title='Ошибка', message='Комментарии запрещены автором',
                           css_file=url_for('static', filename='css/style.css'))
    return render_template('error.html', title='Ошибка', message='Не существует чата',
                           css_file=url_for('static', filename='css/style.css'))


@app.route('/<int:id>', methods=['GET', 'POST'])
def one_chat(id):
    session = db_session.create_session()
    get_chat = session.query(chats.Chats).filter(chats.Chats.id == id).first()
    if get_chat:
        author_id, title, block_comm = get_chat.user_id, get_chat.title, get_chat.is_private
        get_comment = session.query(comment.Comment).filter(comment.Comment.chat_id == id)
        return render_template('comm.html', title=title, is_private=block_comm, author_id=author_id, comm=get_comment,
                               id_chat=id,
                               css_file=url_for('static', filename='css/style.css'))
    return render_template('error.html', title='Ошибка', message='Такого чата не существует', id_chat=id,
                           css_file=url_for('static', filename='css/style.css'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(users.User).filter(users.User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильная почта или пароль",
                               form=form,
                               css_file=url_for('static', filename='css/style.css'))
    return render_template('login.html', title='Авторизация', form=form,
                           css_file=url_for('static', filename='css/style.css'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают",
                                   css_file=url_for('static', filename='css/style.css'))
        session = db_session.create_session()
        if session.query(users.User).filter(users.User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть",
                                   css_file=url_for('static', filename='css/style.css'))
        if session.query(users.User).filter(users.User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Имя занято",
                                   css_file=url_for('static', filename='css/style.css'))
        user = users.User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form,
                           css_file=url_for('static', filename='css/style.css'))


if __name__ == '__main__':
    db_session.global_init("db/forum.sqlite")

    api.add_resource(users_resource.UsersListResource, '/api/v1/users')
    api.add_resource(users_resource.UsersResource, '/api/v1/users/<int:user_id>')

    api.add_resource(chats_resource.ChatsListResource, '/api/v1/chats')
    api.add_resource(chats_resource.ChatsResource, '/api/v1/chats/<int:chats_id>')

    api.add_resource(comment_resource.CommentListResource, '/api/v1/comment')
    api.add_resource(comment_resource.CommentResource, '/api/v1/comment/<int:comment_id>')

    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=port)
