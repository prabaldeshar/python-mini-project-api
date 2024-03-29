from flask import Flask, request, jsonify, make_response
import json
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
# import jwt
import datetime
from functools import wraps
from jwt_helper import generate_token, decode_token
app = Flask(__name__)

#Adding database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    email = db.Column(db.String(100))

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # public_key = open('key/jwt-key.pub').read()
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            print(f'printing new token--->{type(token)}')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = decode_token(token)
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except Exception as e:
            return jsonify({'message': str(e)}), 401

        return f(current_user, *args, **kwargs)   

    return decorated

@app.route("/")
def hello_world():
    return "<h1> Hello world </h1>"
    
@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['email'] = user.email
        output.append(user_data)
    
    return jsonify({'users': output})

@app.route('/user/profile/', methods=['GET'])
@token_required
def get_one_user(current_user):
    # user = User.query.filter_by(public_id=public_id).first()
    if not current_user:
        return jsonify({'message': 'No user found'})
    
    # print(f"Printing current user{current_user.name}")
    user_data = {}
    user_data['name'] = current_user.name
    user_data['email'] = current_user.email

    return jsonify({'user': user_data})

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "New User Created"})

@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"meassage": "User does not exist"})
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User has been deleted'})         

@app.route('/login')
def login():
    print("login")
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    user = User.query.filter_by(name=auth.username).first()
    if not user:
        print("user")
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    if check_password_hash(user.password, auth.password):
        payload = {'public_id' : user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}
        token = generate_token(payload)
        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

@app.route('/jwks')
@token_required
def get_jwks(current_user):
    with open('jwks.json', 'r') as f:
        public_k = json.load(f)
    return public_k

if __name__ == "__main__":
    app.run(debug=True)


