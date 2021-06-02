import flask
from flask import Flask, render_template, request, session
import requests
import os
import logging
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



@app.route('/')
@app.route('/index')
def index():
    return flask.render_template('index.html')

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
