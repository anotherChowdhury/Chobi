from myappmain import app
from app import token_required
from flask import request, jsonify, make_response, url_for
from model import User, Picture
from crud import *
from uploads import *


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
            "link": particular_picture.picture_link,
            "caption": particular_picture.picture_caption})
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
