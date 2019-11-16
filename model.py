from myappmain import db


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

    def __init__(self, id, link, **kwargs):
        super(Picture, self).__init__(**kwargs)
        self.picture_link = link
        self.owner_id = id
