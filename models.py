from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://twewxikheafkcm:0a85002e32d391f3878c7a30f7c2f1545825c06fa5ec1a7c7e86b6f942df5e76" \
                                        "@ec2-107-21-97-5.compute-1.amazonaws.com:5432/d2v3n5k0dhe10"
app.config['SECRET_KEY'] = "kursovahorodniukserhii"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):

    __tablename__ = 'orm_user'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(45), nullable=False)
    user_username = db.Column(db.String(45), nullable=False)
    user_password = db.Column(db.String(64), nullable=False)

    files = db.relationship('File')


class File(db.Model):

    __tablename__ = 'orm_file'

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(45), nullable=False)
    upload_time = db.Column(db.String(100), nullable=False)

    language_id = db.Column(db.Integer, db.ForeignKey('orm_language.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('orm_user.id'))


class Language(db.Model):

    __tablename__ = 'orm_language'

    id = db.Column(db.Integer, primary_key=True)
    language_name = db.Column(db.String(45), nullable=False)
    language_version = db.Column(db.String(20), nullable=False)
    language_release_date = db.Column(db.String(45), nullable=False)

    files = db.relationship('File')


class Documentation(db.Model):

    __tablename__ = 'orm_documentation'

    id = db.Column(db.Integer, primary_key=True)
    documentation_name = db.Column(db.String(100), nullable=False)

    file_id = db.Column(db.Integer, db.ForeignKey('orm_file.id'))


db.create_all()
