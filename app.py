import os
from datetime import datetime, timedelta
import os
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import Flask, request, make_response, jsonify, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__, template_folder="templates")
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:opensesame@127.0.0.1:5100/imageUploader'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False


#########token functions###################
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return make_response(jsonify({
                "msg": "Token is Missing"
            }), 404)

        try:
            data = jwt.decode(token, 'topSecret')
            print(data)
        except:
            return make_response(jsonify({
                "msg": "Token is Invalid"
            }), 403)
        return f(*args, **kwargs)

    return decorated


db = SQLAlchemy(app)


class User(db.Model):
    __name__ = 'user'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    pictures = db.relationship("Picture", backref='owner')

    def __init__(self, email, password, name, **kwargs):
        super(User, self).__init__(**kwargs)
        self.email = email
        self.password = password
        self.name = name


class Picture(db.Model):
    __name__ = 'picture'
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.uid'))
    picture_link = db.Column(db.String(255), nullable=False)
    is_private = db.Column(db.Boolean, default=False)
    picture_caption = db.Column(db.String(255))
    picture_description = db.Column(db.Text)

    def __init__(self, id, link, **kwargs):
        super(Picture, self).__init__(**kwargs)
        self.picture_link = link
        self.owner_id = id


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#
# @app.route('/')
# def index():
#     return render_template('upload.html')


@app.route('/image', methods=['POST'])
@token_required
def upload_image():
    # if "file" not in request.files:
    #     return make_response(jsonify({
    #         "msg": "Coudn't upload the file"
    #     }), 400)

    images = request.files
    permission = request.form
    imageList = []
    # keyList = sorted(images.keys())
    print(permission)
    # print(images['is_private0'])
    i = 0
    for key in images.keys():
        file = images[key]
        hardcoded_privacy_key = "is_private" + str(i)
        hardcoded_caption_key = "caption" + str(i)

        is_private = permission[hardcoded_privacy_key]
        caption = permission[hardcoded_caption_key]
        print(is_private + " " + caption)
        if file.filename == '':
            return make_response(jsonify({
                "msg": 'File name not found'
            }), 400)
        name = file.filename
        if allowed_file(file.filename):
            now = datetime.now()
            timestamp = str(datetime.timestamp(now))
            filename = file.filename.rsplit('.', 1)
            name = filename[0] + "-" + timestamp + '.' + filename[1]
            file.save(os.path.join(UPLOAD_FOLDER, name))
            path = 'http://127.0.0.1:5000' + url_for('static', filename=name)
            id = get_user_id(request.headers.get('Authorization'))
            if is_private == 'true':
                is_private = True
            else:
                is_private = False
            picture = Picture(id, path, is_private=is_private, picture_caption=caption)
            db.session.add(picture)
            db.session.commit()
            imageList.append(('http://127.0.0.1:5000' + url_for('static', filename=name)))
            i += 1
    return make_response(jsonify({
        'imageList': imageList
    }), 200)
    # else:
    #     return make_response(jsonify({
    #         "msg": 'Please Upload an Iamge. Supported file formats are jpg,jpeg,png.'
    #     }), 400)


@token_required
@app.route('/delete', methods=["POST"])
def delete():
    print("I'm in")
    user_id = get_user_id(request.headers.get('Authorization'))
    data = request.get_json()
    id = data['image_id']
    picture = get_picture_from_id(id)
    picture_owner_id = picture.owner_id

    if not user_id == picture_owner_id:
        return make_response(jsonify({
            "msg": "User is not authorised to delete this"
        }), 403)

    db.session.delete(picture)
    db.session.commit()
    return make_response(jsonify({
        "id": id
    }), 200)


@app.route('/showimages', methods=["GET"])
def show_images():
    print("I am in")
    imageList = []
    id = get_user_id(request.headers.get('Authorization'))
    pictures = Picture.query.filter_by(owner_id=id).all()

    for particular_picture in pictures:
        imageList.append({
            "image_id": particular_picture.pid,
            "link": particular_picture.picture_link})
    print(imageList)
    return make_response(jsonify({
        "imageList": imageList
    }), 200)


@app.route('/login', methods=["POST"])
def login():
    user_data = request.get_json()
    email = user_data['email']
    password = user_data['password']
    token = verify_user(email, password)

    if not token:
        return make_response(jsonify({
            "msg": "wrong credential"
        }), 403)
    return make_response(jsonify({
        "msg": token.decode()
    }), 200)


@app.route('/signup', methods=["POST"])
def signup():
    user_data = request.get_json()
    email = user_data['email']
    password = user_data['password']
    name = user_data['name']

    print(email)
    print(name)

    if email and password and name:
        user = User(email, password, name)
        db.session.add(user)
        db.session.commit()
        return make_response(jsonify({
            'msg': 'User registration successfull'
        }), 200)

    return make_response(jsonify({
        'msg': "User regitration failed"
    }), 403)


@app.route('/public', methods=["GET"])
def public_images():
    picturesList = get_public_pictures()
    # pictures = []
    # users = []
    # for picture in picturesList:
    #     if picture.name not in users:
    #         users.append(picture.name)
    #     pictures.append({
    #         "name": picture.name,
    #         "link": picture.picture_link
    #     })
    #
    # users.append(pictures[0])
    # print(users)
    #
    # users.append(pictures)
    #
    # # print(pictures)
    # print(users)

    return make_response(jsonify({
        "pictures": picturesList
    }), 200)


@app.route('/search', methods=["POST"])
def search():
    data = request.get_json()
    print(data)
    data = data["search"]
    if request.headers.get("Authorization"):
        images = search_dashboard(data)
        return make_response(jsonify({
        "images": images
        }), 200)
    else:
        images = search_public_pictures(data)
        return make_response(jsonify({
            "images": images
        }), 200)


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
    pictures = Picture.query.all()
    images = []
    for pic in pictures:
        if pic.picture_caption.lower().find(search_for.lower()) != -1 and not pic.is_private:
            images.append({"image_id": pic.pid, "caption": pic.picture_caption, "link": pic.picture_link})
    return images


if __name__ == '__main__':
    app.run(debug=True, threaded=True)

##########################Database Functions CRUD
