from flask_restful import Resource
from flask import abort, jsonify
from . import db_session
from .users import User
from .user_parser import parser
from datetime import datetime


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=("id", "surname", "name", "age", "city_from",
                  "position", "speciality", "address", "email", "modified_date"))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [user.to_dict(only=("id", "surname", "name", "age", "city_from",
                                                    "position", "speciality", "address", "email", "modified_date")) for user in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            position=args["position"],
            speciality=args['speciality'],
            address=args['address'],
            email=args['email'],
            city_from=args['city_from']
        )
        user.set_password(args["password"])
        if args.get("modified_date"):
            user.modified_date = args["modified_date"]
        else:
            user.modified_date = datetime.now()
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})