from flask_restful import reqparse, abort, Api, Resource
from data import db_session, comment, users, chats
from flask import jsonify


parser = reqparse.RequestParser()
parser.add_argument('author', required=True)
parser.add_argument('text', required=True)
parser.add_argument('chat_id', required=True, type=int)


def abort_if_user_not_found(comment_id):
    session = db_session.create_session()
    user = session.query(comment.Comment).get(comment_id)
    if not user:
        abort(404, message=f"Comment {comment_id} not found")


class CommentResource(Resource):
    def get(self, comment_id):
        abort_if_user_not_found(comment_id)
        session = db_session.create_session()
        comm = session.query(comment.Comment).get(comment_id)
        return jsonify({'comment': comm.to_dict(
            only=('id', 'id_author', 'author', 'text', 'chat_id', 'created_date'))})

    def delete(self, comment_id):
        abort_if_user_not_found(comment_id)
        session = db_session.create_session()
        comm = session.query(comment.Comment).get(comment_id)
        session.delete(comm)
        session.commit()
        return jsonify({'success': 'OK'})


class CommentListResource(Resource):
    def get(self):
        session = db_session.create_session()
        comm = session.query(comment.Comment).all()
        return jsonify({'comment': [item.to_dict(
            only=('id', 'id_author', 'author', 'text', 'chat_id', 'created_date')) for item in comm]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        check_args_user = session.query(users.User).filter(users.User.name == args['author']).first()
        check_args_chats = session.query(chats.Chats).filter(chats.Chats.id == args['chat_id']).first()
        if check_args_user and check_args_chats:
            comm = comment.Comment(
                author=args['author'],
                text=args['text'],
                chat_id=args['chat_id'],
                id_author=check_args_user.id
            )
            session.add(comm)
            session.commit()
            return jsonify({'success': 'OK'})
        return jsonify({'message': 'This chat or user does not exist'})