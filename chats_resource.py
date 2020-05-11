from flask_restful import reqparse, abort, Api, Resource
from data import db_session, chats, comment
from flask import jsonify


parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('is_private', required=True, type=bool)
parser.add_argument('user_id', required=True, type=int)


def abort_if_user_not_found(chats_id):
    session = db_session.create_session()
    user = session.query(chats.Chats).get(chats_id)
    if not user:
        abort(404, message=f"Chat {chats_id} not found")


class ChatsResource(Resource):
    def get(self, chats_id):
        abort_if_user_not_found(chats_id)
        session = db_session.create_session()
        chat = session.query(chats.Chats).get(chats_id)
        return jsonify({'chat': chat.to_dict(
            only=('id', 'title', 'is_private', 'user_id', 'created_date'))})

    def delete(self, chats_id):
        abort_if_user_not_found(chats_id)
        session = db_session.create_session()
        chat = session.query(chats.Chats).get(chats_id)
        for msg in session.query(comment.Comment).filter(comment.Comment.chat_id == chats_id):
            session.delete(msg)
        session.delete(chat)
        session.commit()
        return jsonify({'success': 'OK'})


class ChatsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        chat = session.query(chats.Chats).all()
        return jsonify({'chat': [item.to_dict(
            only=('id', 'title', 'is_private', 'user_id', 'created_date')) for item in chat]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        check_args = session.query(chats.Chats).filter(chats.Chats.title == args['title']).first()
        if not check_args:
            chat = chats.Chats(
                title=args['title'],
                is_private=args['is_private'],
                user_id=args['user_id']
            )
            session.add(chat)
            session.commit()
            return jsonify({'success': 'OK'})
        return jsonify({'message': 'This chat already exists'})