from flask_restful import reqparse, abort, Api, Resource
from data import db_session, users
from flask import jsonify


parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('email', required=True)
parser.add_argument('password', required=True)


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(users.User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(users.User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('id', 'name', 'email', 'created_date'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(users.User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        user = session.query(users.User).all()
        return jsonify({'user': [item.to_dict(
            only=('id', 'name', 'email', 'created_date')) for item in user]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        check_args = session.query(users.User).filter((users.User.name == args['name']) | (users.User.email == args['email'])).first()
        print(check_args)
        if not check_args:
            user = users.User(
                name=args['name'],
                email=args['email']
            )
            user.set_password(args['password'])
            session.add(user)
            session.commit()
            return jsonify({'success': 'OK'})
        return jsonify({'message': 'This user already exists'})