import datetime
import pytz
import uuid

from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import UUID

app = Flask(__name__)

POSTGRESQL_URI = 'postgresql://element:element@localhost:5432/element'

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRESQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)
# timezone
timezone = pytz.timezone('US/Eastern')


# Users Class/Model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.text('now()'))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    def __init__(self, user_id, name, email):
        self.id = user_id
        self.name = name
        self.email = email


# Product Schema
class UserSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ('id', 'name', 'email')


# Init Schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route('/users', methods=['GET'])
def get_users():
    all_users = User.query.filter(
        User.deleted_at == None
    ).order_by(User.created_at).all()

    result = users_schema.dump(all_users)

    return jsonify(result)


@app.route('/users/<uuid:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.filter(
        and_(
            User.deleted_at == None,
            User.id == user_id
        )
    ).first()

    if user is None:
        app.logger.warn(f"user with id:{user_id} not found")

        return '', 404

    return user_schema.jsonify(user)


@app.route('/users', methods=['POST'])
def add_user():
    name = request.json['name']
    email = request.json['email']

    taken_email = User.query.filter(
        and_(
            User.deleted_at == None,
            User.email == email
        )
    ).first()

    if taken_email is not None:
        app.logger.warn(f"user with email:{email} already exists")

        return '', 409

    new_user = User(uuid.uuid4(), name, email)

    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user), 201


@app.route('/users/<uuid:user_id>', methods=['PUT'])
def edit_user(user_id):
    name = request.json['name']
    email = request.json['email']

    user = User.query.filter(
        and_(
            User.deleted_at == None,
            User.id == user_id
        )
    ).first()

    if user is None:
        app.logger.warn(f"user with id:{user_id} not found")

        return '', 404

    taken_email = User.query.filter(
        and_(
            User.deleted_at == None,
            User.email == email, User.id != user_id
        )
    ).first()

    if taken_email is not None:
        app.logger.warn(f"user with email:{email} already exists")

        return '', 409

    user.name = name
    user.email = email
    user.updated_at = timezone.localize(datetime.datetime.now())

    db.session.commit()

    return user_schema.jsonify(user)


@app.route('/users/<uuid:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter(
        and_(
            User.deleted_at == None,
            User.id == user_id
        )
    ).first()

    if user is None:
        app.logger.warn(f"user with id:{user_id} not found")

        return '', 404

    user.deleted_at = timezone.localize(datetime.datetime.now())

    db.session.commit()

    return '', 204


if __name__ == '__main__':
    app.run()
