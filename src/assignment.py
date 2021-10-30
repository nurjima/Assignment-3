from datetime import datetime, timedelta
from functools import wraps
from flask import Flask
from flask.helpers import make_response
from flask import request
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
import jwt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@localhost/Python'
app.config['SECRET_KEY'] = 'flask_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    tablename = 'userr'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50))
    password = db.Column(db.String(50))
    token = db.Column(db.String(50))

    def __init__(self, id, login, password, token):
        self.id = id
        self.login = login
        self.password = password
        self.token = token

    def __repr__(self):
        return '<Task %r>' % self.id


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        try:
            data = jwt.decode(token.app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Could not verify the token'}), 403

        return f(*args, **kwargs)
    return decorated


@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(id=data['id'], login=data['login'], password=data['password'], token=data['token'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'You created the new user!'})


@app.route('/protected')
@token_required
def protected():
    return jsonify({'message': 'Hello, token which is provided is correct'})


@app.route('/login')
def login():
    auth = request.authorization
    user = User.query.filter_by(login=auth.username).first()
    if not user:
        return make_response('There is no such users: ' + auth.username, 401)

    if user.password == auth.password:
        token = jwt.encode({'user': auth.username, 'exp': datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'])

        user.token = token
        return jsonify({'token': token})

    return make_response('There is no such users: ' + auth.username, 401)


if __name__ == '__main__':
    app.run(debug=True)
