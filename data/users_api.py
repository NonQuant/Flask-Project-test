from datetime import datetime
import flask

from . import db_session
from .users import User
from flask import jsonify, make_response, request

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            "users": [user.to_dict(only=("id", "surname", "name", "age", "city_from",
                                         "position", "speciality", "address", "email", "modified_date")) for user in users]
        }
    )

@blueprint.route("/api/users/<int:user_id>")
def get_one_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify(
            {
                "error": "Not found"
            }
        )
    return jsonify(
        {
            "users": user.to_dict(only=("id", "surname", "name", "age", "city_from",
                                        "position", "speciality", "address", "email", "modified_date"))
        }
    )

@blueprint.route("/api/users", methods=["POST"])
def create_users():
    if not request.json:
        return jsonify({"error": "Empty request"})
    elif not all(key in request.json for key in 
                 ["surname", "name", "age", "city_from",
                  "position", "speciality", "address", "email", "password"]):
        return jsonify({"error": "Bad request"})
    db_sess = db_session.create_session()
    
    if request.json.get("id"):
        possible_user = db_sess.query(User).filter(User.id == request.json.get("id")).first()
        if possible_user:
            return jsonify({"error": "Id already exists"})
        users = User(id=request.json.get("id"))
    else:
        users = User()

    users.surname = request.json["surname"]
    users.name = request.json["name"]
    users.age = request.json["age"]
    users.position = request.json["position"]
    users.speciality = request.json["speciality"]
    users.address = request.json["address"]
    users.email = request.json["email"]
    users.city_from = request.json["city_from"]
    users.set_password(request.json["password"])

    if request.json.get("modified_date"):
        users.modified_date = request.json["modified_date"]
    else:
        users.modified_date = datetime.now()

    db_sess.add(users)
    db_sess.commit()
    return jsonify({"success": "OK"})

@blueprint.route("/api/users/<int:users_id>", methods=["DELETE"])
def delete_users(users_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.id == users_id).first()
    if not users:
        return jsonify({"error": "Not found"})
    db_sess.delete(users)
    db_sess.commit()
    return jsonify({"success": "OK"})


@blueprint.route("/api/users/<int:users_id>", methods=["PUT"])
def edit_users(users_id):
    data = request.json
    if not data:
        return jsonify({"error": "Empty request"})
    db_sess = db_session.create_session()
    user: User = db_sess.query(User).filter(User.id == users_id).first()
    if not user:
        return jsonify({"error": "Not found"})
    for i in data.keys():
        if i not in ("surname", "name", "age", "position", "speciality", "address", "email", "password", "city_from"):
            return jsonify({"error": "Bad request"})
        if i == "surname":
            user.surname = data[i]
        if i == "name":
            user.name = data[i]
        if i == "age":
            user.age = data[i]
        if i == "position":
            user.position = data[i]
        if i == "speciality":
            user.speciality = data[i]
        if i == "address":
            user.address = data[i]
        if i == "email":
            user.email = data[i]
        if i == "password":
            user.set_password(data[i])
        if i == "city_from":
            user.city_from = data[i]
    db_sess.commit()
    return jsonify({"success": "OK"})
