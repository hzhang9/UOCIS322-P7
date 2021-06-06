import flask
from flask import Flask,request
from flask_restful import Resource, Api
import pymongo
from pymongo import MongoClient
import os
from itsdangerous import (TimedJSONWebSignatureSerializer \
        as Serializer, BadSignature, \
        SignatureExpired)

app = Flask(__name__)
api = Api(app)
client= MongoClient('mongodb://'+os.environ['MONGODB_HOSTNAME'],27017)
db=client.tododb
app.secret_key='Default secret'

def verify_token(token):
#used to verify token that transfered from website
    s=Serializer(app.secret_key)
    try:
        data=s.loads(token)
    except SignatureExpired:
        return None
    except BadSignature:
        return None
    return "Success"

class listAJ(Resource):
    def get(self):
        headers=flask.request.headers#get headers
        if not headers.has_key('Authorization'):#if called by website, must have a key Authorization, if have not, means have not token also
            message="Token doesn't exist."
            return message,401
        token= headers['Authorization'][6:]#first 6 letter is Bearer, rest is token
        if verify_token(token)==None:#verify the token, if fail, raise error
            message="Token verify fail."
            return message,401
        #if pass above two check, token verify successfully, now can use function, and following all class use same method the check token
        top=request.args.get("top")#get top variable(get fail will became None)
        result=[]
        items=list(db.tododb.find())#take data in mongo to be list
        if top==None or len(items)<int(top):
        #if doesn't have top, default display all, or invalid num(bigger than # of instance in mongo)
            for item in items:
                result.append({'miles':item['miles'],'km':item['km'],'location':item['location'],'open':item['open'],'close':item['close']})
            return result
        else:
        #else, limit receieve # of data in mongo, only get depond on top
            for i in range(int(top)):
                result.append({'miles':items[i]['miles'],'km':items[i]['km'],'location':items[i]['location'],'open':items[i]['open'],'close':items[i]['close']})
            return result
        

class listOJ(Resource):
    #almost same with listAJ, but don't shows close times
    def get(self):
        headers=flask.request.headers
        if not headers.has_key('Authorization'):
            message="Token doesn't exist."
            return message,401
        token= headers['Authorization'][6:]
        if verify_token(token)==None:

            message="Token verify fail."
            return message,401
        top=request.args.get("top")
        result=[]
        items=list(db.tododb.find())
        if top==None or len(items)<int(top):
            for item in items:
                result.append({'miles':item['miles'],'km':item['km'],'location':item['location'],'open':item['open']})
            return result
        else:
            for i in range(int(top)):
                result.append({'miles':items[i]['miles'],'km':items[i]['km'],'location':items[i]['location'],'open':items[i]['open']})
            return result

class listCJ(Resource):
    #almost same with listAJ, but doesn't shows open times
    def get(self):
        headers=flask.request.headers
        if not headers.has_key('Authorization'):
            message="Token doesn't exist."
            return message,401
        token= headers['Authorization'][6:]
        if verify_token(token)==None:
            message="Token verify fail."
            return message,401
        top=request.args.get("top")
        result=[]
        items=list(db.tododb.find())
        if top==None or len(items)<int(top):
            for item in items:
                result.append({'miles':item['miles'],'km':item['km'],'location':item['location'],'close':item['close']})
            return result
        else:
            for i in range(int(top)):
                result.append({'miles':items[i]['miles'],'km':items[i]['km'],'location':items[i]['location'],'close':items[i]['close']})
            return result

class listAC(Resource):
    def get(self):
        #except change format to be csv, others almost same with listAJ
        headers=flask.request.headers
        if not headers.has_key('Authorization'):
            message="Token doesn't exist."
            return message,401
        token= headers['Authorization'][6:]
        if verify_token(token)==None:
            message="Token verify fail."
            return message,401
        top=request.args.get("top")
        result=[]
        items=list(db.tododb.find())
        headers='miles,km,location,open,close'
        result.append(headers)
        if top==None or len(items)<int(top):
            for item in items:
                values=','.join([item['miles'],item['km'],item['location'],item['open'],item['close']])#for format of csv
                result.append(values)
            return result
        else:
            for i in range(int(top)):
                values=','.join([items[i]['miles'],items[i]['km'],items[i]['location'],items[i]['open'],items[i]['close']])#for format of csv
                result.append(values)
            return result

class listOC(Resource):
    #almost same with listAC, but doesn't shows close times
    def get(self):
        headers=flask.request.headers
        if not headers.has_key('Authorization'):
            message="Token doesn't exist."
            return message,401
        token= headers['Authorization'][6:]
        if verify_token(token)==None:
            message="Token verify fail."
            return message,401
        top=request.args.get("top")
        result=[]
        items=list(db.tododb.find())
        headers='miles,km,location,open'
        result.append(headers)
        if top==None or len(items)<int(top):
            for item in items:
                values=','.join([item['miles'],item['km'],item['location'],item['open']])
                result.append(values)
            return result
        else:
            for i in range(int(top)):
                values=','.join([items[i]['miles'],items[i]['km'],items[i]['location'],items[i]['open']])
                result.append(values)
            return result

class listCC(Resource):
    #almost same with listAC, but doesn't shows open times
    def get(self):
        headers=flask.request.headers
        if not headers.has_key('Authorization'):
            message="Token doesn't exist."
            return message,401
        token= headers['Authorization'][6:]
        if verify_token(token)==None:
            message="Token verify fail."
            return message,401
        top=request.args.get("top")
        result=[]
        items=list(db.tododb.find())
        headers='miles,km,location,close'
        result.append(headers)
        if top==None or len(items)<int(top):
            for item in items:
                values=','.join([item['miles'],item['km'],item['location'],item['close']])
                result.append(values)
            return result
        else:
            for i in range(int(top)):
                values=','.join([items[i]['miles'],items[i]['km'],items[i]['location'],items[i]['close']])
                result.append(values)
            return result

# Create routes
# Another way, without decorators
api.add_resource(listAJ, '/listAll', '/listAll/json')
api.add_resource(listOJ, '/listOpenOnly', '/listOpenOnly/json')
api.add_resource(listCJ, '/listCloseOnly', '/listCloseOnly/json')
api.add_resource(listAC, '/listAll/csv')
api.add_resource(listOC, '/listOpenOnly/csv')
api.add_resource(listCC, '/listCloseOnly/csv')

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
