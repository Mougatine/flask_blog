import datetime

from flask_security.utils import encrypt_password

from app import db


roles_users = db.Table('roles_users',
                       db.Column('user_id',
                                 db.Integer(),
                                 db.ForeignKey('user.id')),
                       db.Column('role_id',
                                 db.Integer(),
                                 db.ForeignKey('role.id')))


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(64), index=False, unique=False)
    authenticated = db.Column(db.Boolean, default=False)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __init__(self, username, password):
        self.username = username
        self.password = encrypt_password(password)

    @classmethod
    def get_user(cls, username, password):
        return cls.query.filter_by(username=username,
                                   password=encrypt_password(password)).first()

    def is_password(self, password):
        return encrypt_password(password) == self.password

    def set_password(self, password):
        self.password = encrypt_password(password)

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.username


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True)
    content = db.Column(db.Text)
    intro = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
 #   author = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % self.title

    @classmethod
    def get_post(cls, title):
        return cls.query.filter_by(title=title).first_or_404()
