import flask
from flask import Flask, render_template, request, session
import requests
import os
import logging
import pymongo
from pymongo import MongoClient
from flask_login import (LoginManager, current_user, login_required, login_user, logout_user, UserMixin, confirm_login, fresh_login_required)
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, validators
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer \
                          as Serializer, BadSignature, \
                          SignatureExpired)
import time
from urllib.parse import urlparse,urljoin
import random


ADDR= os.environ['BACKEND_ADDR']#respti
PORT= os.environ['BACKEND_PORT']#port
app = Flask(__name__)
login_manager= LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"
client= MongoClient('mongodb://'+os.environ['MONGODB_HOSTNAME'],27017)
users=client.usersdb
app.secret_key='Default secret'

@login_required
def generate_token(uid,expiration=600):
    s=Serializer(app.secret_key,expires_in=expiration)
    token=s.dumps({'id':uid})
    return {'token':token,'duration':expiration}

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
        validators.InputRequired(u"Must input username")])
    password= StringField('Password',[
        validators.Length(min=2,max=25,message=u"Little too short for a password."),
        validators.InputRequired(u"Must input password")])


class LoginForm(Form):
    username= StringField('Username',[
        validators.Length(min=2,max=25,message=u"Little too short for a username."),
        validators.InputRequired(u"Must input username")])
    password= StringField('Password',[
        validators.Length(min=2,max=25,message=u"Little too short for a password."),
        validators.InputRequired(u"Must input password")])
    remember= BooleanField('Remember me')

class User(UserMixin):
    def __init__(self, uid):
        self.id = uid

@login_manager.user_loader
def load_user(user_id):
    user=users.usersdb.find_one(user_id)
    if user=='' or user==None:
        return None
    else:
        return User(user)

@app.route('/')
@app.route('/main')
def main():
    return flask.render_template('main.html')


@app.route('/index')
#@login_required
def index():
    return flask.render_template('index.html')


@app.route('/register',methods=['GET','POST'])
def register():
    form= RegisterForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        udata=users.usersdb.find_one({"username":username})
        uid=random.randint(1,9999999)
        if udata!=None:
            message="Already exist given username"
            return flask.render_template('400_r.html',message=message),400
        hashp=hash_password(password)
        user={'id':uid,'username':username,'password':hashp}
        users.usersdb.insert_one(user)
        session['token']=None
        return flask.render_template('register_suc.html',data=user),201
    return flask.render_template('register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        password= form.password.data
        remember=form.remember.data
        udata=users.usersdb.find_one({"username":username})
        if udata==None:
            message="Username doesn't exist"
            return flask.render_template('400_l.html',message=message),400
        hashp=udata['password']
        if verify_password(password,hashp)==False:
            message="Password wrong"
            return flask.render_template('400_l.html',message=message),400
        uid=udata['id']
        class_u=User(uid)
        if login_user(class_u,remember):
            session['id']=current_user.id
            token=generate_token(uid)
            t=token['token'].decode('utf-8')
            session['token']=t
            user={'id':uid,'username':username,'password':hashp,'remember':remember}
            return flask.render_template('login_suc.html',data=user)
            #next=request.args.get('next')
            #if not is_safe_url(next):
            #    message="Next doesn't safe"
            #    return flask.render_template('400_l.html',message=message),400
            #return redirect(next or url_for('index'))
    return flask.render_template('login.html',form=form)

@app.route('/logout')
#@login_required
def logout():
    logout_user()
    return flask.render_template('logout_suc.html')

@app.route('/listAJ',methods=['POST'])
def listAJ():
    top=request.form['top']#get top from input
    if top==None or top.isdigit()==False:
    #doesn't find top, or top invalid, just display all
        r = requests.get('http://{}:{}/listAll/json'.format(ADDR,PORT))
    else:
    #else have top, add top in the link used in requests.get
        r = requests.get('http://{}:{}/listAll/json?top={}'.format(ADDR,PORT,top))
    app.logger.debug(r.content)
    result="ACP Brevet Times (json):\n"
    c_c=0#count comma number
    for i in r.text:
        if str(i)!='[' and str(i)!=']' and str(i)!='{' and str(i)!='}':#better to don't show consurme unnecessary symbol like []{}
        #get response and change to string(.text), 
            if c_c==4 and str(i)==",":
            #if c_c is 4, already display a group,ignore the comma behild the group, and inital c_c
                c_c=0
                continue
            else:
                result+=str(i)
        if i==",":
        #update c_c
            c_c+=1
    result=result.replace('\n','<br/>')#for \n can be see as line break
    logout_user()
    return result #result now is json format string, return

@app.route('/listOJ',methods=['POST'] )
def listOJ():
    #almost same with listAJ, but doesn't shows close
    top=request.form['top']
    if top==None or top.isdigit()==False:
        r = requests.get('http://{}:{}/listOpenOnly/json'.format(ADDR,PORT))
    else:
        r = requests.get('http://{}:{}/listOpenOnly/json?top={}'.format(ADDR,PORT,top))
    app.logger.debug(r.content)
    result="ACP Brevet Open Times (json):\n"
    c_c=0
    for i in r.text:
        if str(i)!='[' and str(i)!=']' and str(i)!='{' and str(i)!='}':
            if c_c==3 and str(i)==",":
                c_c=0
                continue
            else:
                result+=str(i)
        if i==",":
            c_c+=1
    result=result.replace('\n','<br/>')
    return result

@app.route('/listCJ',methods=['POST'])
def listCJ():
    #almost same with listAJ, but doesn't shows open
    top=request.form['top']
    if top==None or top.isdigit()==False:
        r = requests.get('http://{}:{}/listCloseOnly/json'.format(ADDR,PORT))
    else:
        r = requests.get('http://{}:{}/listCloseOnly/json?top={}'.format(ADDR,PORT,top))
    app.logger.debug(r.content)
    result="ACP Brevet Close Times (json):\n"
    c_c=0
    for i in r.text:
        if str(i)!='[' and str(i)!=']' and str(i)!='{' and str(i)!='}':
            if c_c==3 and str(i)==",":
                c_c=0
                continue
            else:
                result+=str(i)
        if i==",":
            c_c+=1
    result=result.replace('\n','<br/>')
    return result

@app.route('/listAC',methods=['POST'])
def listAC():
    #almost same with listAJ, but call /csv, and a little different in achieve csv format
    top=request.form['top']
    if top==None or top.isdigit()==False:
        r = requests.get('http://{}:{}/listAll/csv'.format(ADDR,PORT))
    else:
        r = requests.get('http://{}:{}/listAll/csv?top={}'.format(ADDR,PORT,top))
    result="ACP Brevet Times (csv):\n"
    counter=0#count comma #
    for i in r.text:
        if str(i)!='[' and str(i)!=']' and str(i)!='{' and str(i)!='}' and str(i)!='"':#filter unnecessnary data to user
            if str(i)==',' and counter==4:#remove comma between instance
                counter=0
                continue
            else:
                result+=str(i)
            if str(i)==",":
            #update counter
                counter+=1
    result=result.replace('\n','<br/>')#same as listAJ
    return result#result now is csv format string, return to web


@app.route('/listOC',methods=['POST'])
def listOC():
    #almost same with listAC, but doesn't shows close time 
    top=request.form['top']
    if top==None or top.isdigit()==False:
        r = requests.get('http://{}:{}/listOpenOnly/csv'.format(ADDR,PORT))
    else:
        r = requests.get('http://{}:{}/listOpenOnly/csv?top={}'.format(ADDR,PORT,top))
    result="ACP Brevet Open Times (csv):\n"
    counter=0
    for i in r.text:
        if str(i)!='[' and str(i)!=']' and str(i)!='{' and str(i)!='}' and str(i)!='"':
            if str(i)==',' and counter==3:
                counter=0
                continue
            else:
                result+=str(i)
            if str(i)==",":
                counter+=1
    result=result.replace('\n','<br/>')
    return result

@app.route('/listCC',methods=['POST'])
def listCC():
    #almost same with listAC, but doesn't shows close time 
    top=request.form['top']
    if top==None or top.isdigit()==False:
        r = requests.get('http://{}:{}/listCloseOnly/csv'.format(ADDR,PORT))
    else:
        r = requests.get('http://{}:{}/listCloseOnly/csv?top={}'.format(ADDR,PORT,top))
    result="ACP Brevet Close Times (csv):\n"
    counter=0
    for i in r.text:
        if str(i)!='[' and str(i)!=']' and str(i)!='{' and str(i)!='}' and str(i)!='"':
            if str(i)==',' and counter==3:
                counter=0
                continue
            else:
                result+=str(i)
            if str(i)==",":
                counter+=1
    result=result.replace('\n','<br/>')
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
