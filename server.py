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

# Cоздаём наше приложение + API
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

# Инициализируем LoginManager
login_manager = LoginManager()
login_manager.init_app(app)


# Формы
class LoginForm(FlaskForm):
    """Форма для авторизации"""
    email = EmailField('Введите почту', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class ChatsForm(FlaskForm):
    """"Форма для создания чата"""
    title = StringField("Тема", validators=[DataRequired()])
    is_private = BooleanField("Запретить комментраии")
    submit = SubmitField('Создать')


class RegisterForm(FlaskForm):
    """Форма для регистрации"""
    email = EmailField('Почта', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class CommentForm(FlaskForm):
    """Форма для создания комментария"""
    commentaries = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField('Добавить комментарий')


@app.errorhandler(404)
def not_found(error):
    """Обработчик ошибки 404"""
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(401)
def not_authenticated(error):
    """Обработчик ошибки 401"""
    return render_template('error.html', title='Ошибка', message='Авторизируйетесь для создания чата',
                           css_file=url_for('static', filename='css/style.css'))


@login_manager.user_loader
def load_user(user_id):
    """Функция получения пользователя"""
    new_session = db_session.create_session()
    return new_session.query(users.User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Обработчик авторизации"""
    form = LoginForm()
    if form.validate_on_submit():
        new_session = db_session.create_session()
        user = new_session.query(users.User).filter(users.User.email == form.email.data).first()
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
    """Обработчик выхода из аккаунта"""
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Обработчик регистрации"""
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают",
                                   css_file=url_for('static', filename='css/style.css'))
        new_session = db_session.create_session()
        if new_session.query(users.User).filter(users.User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть",
                                   css_file=url_for('static', filename='css/style.css'))
        if new_session.query(users.User).filter(users.User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Имя занято",
                                   css_file=url_for('static', filename='css/style.css'))
        user = users.User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        new_session.add(user)
        new_session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form,
                           css_file=url_for('static', filename='css/style.css'))


@app.route('/', methods=['GET', 'POST'])
def chats_list():
    """Обработчик главной страницы с чатами"""
    if request.method == "GET":
        new_session = db_session.create_session()
        get_chats = new_session.query(chats.Chats).all()
        return render_template('chats.html', chats=get_chats, title='LiteForum',
                               css_file=url_for('static', filename='css/style.css'))
    elif request.method == "POST":
        new_session = db_session.create_session()
        get_chats = new_session.query(chats.Chats).filter(chats.Chats.title.like('%Новый форум 3%'))
        return render_template('chats.html', chats=get_chats, title='LiteForum',
                               css_file=url_for('static', filename='css/style.css'))


@app.route('/chats', methods=['GET', 'POST'])
@login_required
def add_chat():
    """Обработчик создания чата"""
    form = ChatsForm()
    if form.validate_on_submit():
        new_session = db_session.create_session()
        # добавили чат
        get_chats = chats.Chats()
        get_chats.title = form.title.data
        if new_session.query(chats.Chats).filter(chats.Chats.title == form.title.data).first():
            return render_template('add_chat.html', title='Создание чата',
                                   form=form,
                                   message="Чат с такой темой существует",
                                   css_file=url_for('static', filename='css/style.css'))
        get_chats.is_private = form.is_private.data
        current_user.chats.append(get_chats)
        # добавили первое сообщение в этом чате
        new_session.merge(current_user)
        new_session.commit()
        get_chats = new_session.query(chats.Chats).filter(chats.Chats.title == form.title.data).first()
        return redirect(f'/{get_chats.id}')
    return render_template('add_chat.html', title='Создание чата',
                           form=form, css_file=url_for('static', filename='css/style.css'))


@app.route('/<int:id_chat>', methods=['GET', 'POST'])
def one_chat(id_chat):
    """Обработчик просмотра 1 чата"""
    new_session = db_session.create_session()
    get_chat = new_session.query(chats.Chats).filter(chats.Chats.id == id_chat).first()
    if get_chat:
        author_id, title, block_comm = get_chat.user_id, get_chat.title, get_chat.is_private
        get_comment = new_session.query(comment.Comment).filter(comment.Comment.chat_id == id_chat)
        return render_template('comm.html', title=title, is_private=block_comm, author_id=author_id, comm=get_comment,
                               id_chat=id_chat,
                               css_file=url_for('static', filename='css/style.css'))
    return render_template('error.html', title='Ошибка', message='Такого чата не существует', id_chat=id_chat,
                           css_file=url_for('static', filename='css/style.css'))


@app.route('/comment/<int:id_chat>', methods=['GET', 'POST'])
def add_comment(id_chat):
    """Обработчик создания комментария"""
    new_session = db_session.create_session()
    get_chat = new_session.query(chats.Chats).filter(chats.Chats.id == id_chat).first()
    if get_chat:
        if not get_chat.is_private or current_user.id == get_chat.user_id:
            form = CommentForm()
            if form.validate_on_submit():
                if not form.commentaries.data:
                    return render_template('add_comment.html', title='Создание комментария', form=form,
                                           message='Нельзя добавить пустой комментарий',
                                           css_file=url_for('static', filename='css/style.css'))
                new_session = db_session.create_session()
                get_comm = comment.Comment()
                get_comm.author = current_user.name
                get_comm.text = form.commentaries.data
                get_comm.chat_id = id_chat
                current_user.comment.append(get_comm)
                new_session.merge(current_user)
                new_session.commit()
                return redirect(f'/{id_chat}')
            return render_template('add_comment.html', title='Создание комментария', form=form,
                                   css_file=url_for('static', filename='css/style.css'))
        return render_template('error.html', title='Ошибка', message='Комментарии запрещены автором',
                               css_file=url_for('static', filename='css/style.css'))
    return render_template('error.html', title='Ошибка', message='Не существует чата',
                           css_file=url_for('static', filename='css/style.css'))


if __name__ == '__main__':
    # Подключение базы данных
    db_session.global_init("db/forum.sqlite")
    # Подключение users API
    api.add_resource(users_resource.UsersListResource, '/api/v1/users')
    api.add_resource(users_resource.UsersResource, '/api/v1/users/<int:user_id>')
    # Подключение chats API
    api.add_resource(chats_resource.ChatsListResource, '/api/v1/chats')
    api.add_resource(chats_resource.ChatsResource, '/api/v1/chats/<int:chats_id>')
    # Подключение comment API
    api.add_resource(comment_resource.CommentListResource, '/api/v1/comment')
    api.add_resource(comment_resource.CommentResource, '/api/v1/comment/<int:comment_id>')
    # Запуск сервера
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=port)
