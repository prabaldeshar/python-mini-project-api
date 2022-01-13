from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
app = Flask(__name__)
#Adding database
app.config['SECRET_KEY'] = 'thisissecret'
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


# @app.route('/user', methods=['GET'])
# def get_all_users():
#     return ''

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        public_key = open('key/jwt-key.pub').read()
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            print(f'printing new token--->{type(token)}')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, public_key, algorithms=["RS256"])
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
@token_required
def create_user(current_user):
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "New User Created"})

@app.route('/user/<user_id>', methods=['PUT'])
def promote_user():
    return ''

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
    auth = request.authorization
    private_key = open('key/jwt-key').read()
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.public_id}, private_key, algorithm="RS256")
        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

if __name__ == "__main__":
    app.run(debug=True)


