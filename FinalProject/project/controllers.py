from flask import jsonify, request, abort
from jsonschema import validate # to validate the request body
from project import app, db
from project.models import User, Account
from project.schemas import UserSchema, AccountSchema # to serialize our Db Models

# Request body validation schemas
user_schema ={
     "type" : "object",
     "properties" : {
         "name" : {"type" : "string"},
         "pin" : {"type" : "number"},
     },
}
account_schema ={
     "type" : "object",
     "properties" : {
         "balance" : {"type" : "number"},
         "ownerId" : {"type" : "number"},
     },
}


@app.route('/', methods=['GET'])
def root():
    return  jsonify(
        {'message':'You call root url'}
        )

### USER ###

# helper method
def get_user_by_name(name):
    user = User.query.filter_by(name=name).first()
    if user:
        user_schema = UserSchema()  
        output = user_schema.dump(user).data
        return jsonify(output)
    else:
        abort(404, 'User does not exist')

# http://127.0.0.1:5000/users
# request body sample : {
# 	"name":"Sureyya",
# 	"pin": 1234
# }
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json(force=True) # force=True will make sure this works even if a client does not specify application/json
    validate(instance=data, schema=user_schema)
    user_name= data['name']
    pin = data['pin']
    user = User.query.filter_by(name=user_name).first()
    if user:
        abort(400, description='User is already exist') # for now we will abort, then work on exception handling
    else:
        user = User(name = user_name, pin = pin)
        db.session.add(user)
        db.session.commit()
        response = get_user_by_name(user_name)
    return response

# http://127.0.0.1:5000/users
# no request body
@app.route('/users', methods=['GET','PUT'])
def get_users():
    users = User.query.all()
    user_schema = UserSchema(many=True)  
    output = user_schema.dump(users).data
    return jsonify(output)

# http://127.0.0.1:5000/users
# no request body
@app.route('/users/prety', methods=['GET','PUT'])
def get_users_prety():
    users = User.query.all()
    user_schema = UserSchema(many=True)  
    output = user_schema.dump(users).data
    return str(users[0].account[0].balance)

# http://127.0.0.1:5000/users/1 
# no request body
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        user_schema = UserSchema()  
        output = user_schema.dump(user).data
        return jsonify(output)
    else:
        abort(404, 'User does not exist')

# http://127.0.0.1:5000/users
# request body sample : {
# 	"name":"Sureyya",
# 	"pin": 1111
# }
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json(force=True) # force=True will make sure this works even if a client does not specify application/json 
    validate(instance=data, schema=user_schema)
    user_name= data['name']
    pin = data['pin']
    user = User.query.filter_by(id=user_id).first()
    if user:
        user.name = user_name
        user.pin = pin
        db.session.commit()
        response = get_user_by_name(user_name)
    else:
        abort(404, description='User does not exist') # for now we will abort, then work on exception handling
    return response

# http://127.0.0.1:5000/users/1
# no request body
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return '', 204
    else:
        abort(404, 'User not found')


### ACCOUNT ###

# http://127.0.0.1:5000/users/accounts
# request body sample : 
# {
# 	"balance": 1500,
# 	"ownerId": 1
# }
@app.route('/users/accounts', methods=['POST'])
def create_account():
    data = request.get_json(force=True) # force=True will make sure this works even if a client does not specify application/json
    validate(instance=data, schema=account_schema)
    balance = data['balance']
    owner_id = data['ownerId']
    user = User.query.filter_by(id=owner_id).first()
    if user:
        account = Account(balance = balance, owner_id = owner_id)
        db.session.add(account)
        db.session.commit()
        return jsonify(data)
    else:
         abort(404, description='Owner does not exist') # for now we will abort, then work on exception handling
