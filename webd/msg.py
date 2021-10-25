from flask import Flask, render_template,redirect,session
from flask.globals import request
from flask_socketio import SocketIO, emit
from webd import app,db
import json

from webd.decorator import login_required

socketio = SocketIO(app)

@app.route('/msg/getgrps')
def getgrps():
    user = dict(session).get('profile', None)
    email=user.get('email')
    grp=[]
    grps=db.execute("select group_id from group_users where user_id=:email",{"email":email}).fetchall()
    for row in grps:
        grp.append(list(row))
    grp=json.dumps(grp)
    return grp

@app.route('/msg/getfrnds')
def getfrnds():
    user = dict(session).get('profile', None)
    email=user.get('email')
    frnd=[]
    frnds=db.execute("select email from friends where email2=:email",{"email":email}).fetchall()
    for row in frnds:
        frnd.append(list(row))
    frnd=json.dumps(frnd)
    return frnd

@app.route('/msg/get_msgs')
def getmsgs():
    grp_id=request.args.get('id')
    print(grp_id)
    messages=db.execute("select * from messages").fetchall()
    msg=[]
    for row in messages:
        msg.append(list(row))
    msg=json.dumps(msg,default=str)
    return msg

@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': message['data']})

@socketio.on('my broadcast event')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect')
def test_connect():
    messages=db.execute("select * from messages").fetchall()
    msg=[]
    for row in messages:
        msg.append(list(row))
    msg=json.dumps(msg,default=str)
    print(msg)
    emit('initial connect',msg)

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app)