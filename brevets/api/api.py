import flask
from flask import Flask,request,redirect, url_for, flash, abort
from flask_restful import Resource, Api
import pymongo
from pymongo import MongoClient
import os
from flask_login import (LoginManager, current_user, login_required, login_user, logout_user, UserMixin, confirm_login, fresh_login_required)
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, validators
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer \
                          as Serializer, BadSignature, \
                          SignatureExpired)
import time
from urllib.parse import urlparse,urljoin

app = Flask(__name__)
api = Api(app)
login_manager= LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"
client= MongoClient('mongodb://'+os.environ['MONGODB_HOSTNAME'],27017)
db=client.tododb
users=db.usersdb
app.secret_key='Default secret'

def generate_token(uid,expiration=600):
    s=Serializer(app.secret_key,expires_in=expiration)
    token=s.dumps({'id':uid})
    return {'token':token,'duration':expiration}

def verify_token(token):
    s= Serializer(app.secret_key)
    try:
        data= s.loads(token)
    except SignatureExpired:
        return None
    except BadSignature:
        return None
    return "Success"

def hash_password(password):
    return pwd_context.encrypt(password)

def verify_password(password, hashVal):
    return pwd_context.verify(password, hashVal)

def is_safe_url(target):
    ref_url=urlparse(request.host_url)
    test_url=urlparse(urljoin(request.host_url,target))
    return test_url.scheme in ('http','https') and ref_url.netloc == test_url.netloc

class RegisterForm(Form):
    username= StringField('Username',[
        validators.Length(min=2,max=25,message=u"Little too short for a username."),
        validators.InputRequired(u"Forget something?")])
    password= StringField('Password',[
        validators.Length(min=2,max=25,message=u"Little too short for a username."),
        validators.InputRequired(u"Forget something?")])

class LoginForm(Form):
    username= StringField('Username',[
        validators.Length(min=2,max=25,message=u"Little too short for a username."),
        validators.InputRequired(u"Forget something?")])
    password= StringField('Password',[
        validators.Length(min=2,max=25,message=u"Little too short for a username."),
        validators.InputRequired(u"Forget something?")])
    remember= BooleanField('Remember me')

class User(UserMixin):
    def __init__(self, uid):
        self.id = uid

@login_manager.user_loader
def load_user(user_id):
    user=usersdb.user.find_one(user_id)
    if user=='' or user==None:
        return None
    else:
        return User(user)

@app.route('/')
@app.route('/index')
def index():
    return flask.render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()
    return None

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    return None

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("index"))

@app.route('/token')
def token():
   return None 

@app.errorhandler(400)
def error_400(e):
    return flask.render_template('400.html'),400

@app.errorhandler(401)
def error_401(e):
    return flask.render_template('401.html'),401

class listAJ(Resource):
    def get(self):
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
