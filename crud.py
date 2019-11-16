from flask import request

from model import User, Picture
from myappmain import app, db
import jwt
import os
from datetime import datetime, timedelta


def verify_user(email, password):
    print(email, password)
    user = User.query.filter_by(email=email).first()
    print(user)
    if user != None:
        if user.email == email and user.password == password:
            token = jwt.encode({"exp": datetime.utcnow() + timedelta(days=1), "iat": datetime.utcnow(),
                                'nbf': datetime.utcnow(), 'sub': user.uid}, 'topSecret', algorithm='HS256')
            return token
    return ''


def get_user_id(token):
    # print(token)
    # token = token.encode()
    token = jwt.decode(token, "topSecret", algorithm='HS256')
    id = token["sub"]
    return id


def get_picture_from_id(id):
    picture = Picture.query.filter_by(pid=id).first()
    return picture


def get_public_pictures():
    users = User.query.all()
    users = list(filter(lambda u: len(u.pictures) >= 0, users))
    print(users)
    all_public_images = {}
    for user in users:
        all_public_images[user.name] = [pic.picture_link for pic in user.pictures if not pic.is_private]
    return all_public_images


def search_dashboard(search_for):
    id = get_user_id(request.headers.get("Authorization"))
    user = User.query.get(id)
    print(user.name)
    images = []
    for pic in user.pictures:
        if pic.picture_caption.lower().find(search_for.lower()) != -1:
            print(pic.picture_caption)
            images.append({"image_id": pic.pid, "caption": pic.picture_caption, "link": pic.picture_link})
    return images


def search_public_pictures(search_for):
    pictures = db.session.execute(
        "SELECT * FROM picture WHERE is_private=false AND MATCH (picture_caption, picture_description) AND is_private=0 AGAINST ('" + search_for + "' IN NATURAL LANGUAGE MODE)")
    images = []
    for pic in pictures:
        images.append({"image_id": pic.pid, "caption": pic.picture_caption, "link": pic.picture_link})
    return images
