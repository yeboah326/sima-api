from flask import request, jsonify
from api import app
import jwt
from api.users.models import User
from functools import wraps
import os


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split()[1]

        if not token:
            return jsonify({"message": "Token is missing!"})

        try:
            data = jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=data["public_id"]).first()
        except:
            return jsonify({"message": "Token is invalid"}), 401
        return f(current_user, *args, **kwargs)

    return decorated
