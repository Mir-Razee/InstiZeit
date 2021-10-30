from flask import Flask, render_template,redirect,session
from flask.globals import request
from flask.helpers import url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from webd import app,db
import json

from webd.decorator import login_required

socketio = SocketIO(app)

@app.route('/msg/name')
def getname():
    email1=request.args.get("email1")
    email2=request.args.get("email2")
    grp_id=request.args.get("grp_id")
    user = dict(session).get('profile', None)
    email=user.get('email')
    if email1==email:
        name=db.execute("select name from profile where email=:email",{"email":email2}).fetchone()
    else:
        name=db.execute("select name from profile where email=:email",{"email":email1}).fetchone()
    name=list(name)
    name.append(grp_id)
    data=json.dumps(name)
    return data

@app.route('/msg/getgrps')
def getgrps():
    user = dict(session).get('profile', None)
    email=user.get('email')
    grps=[]
    grp=db.execute("select group_id from group_users where user_id=:email",{"email":email}).fetchall()
    for row in grp:
        grp_name=db.execute("select * from group_chat where group_id=:group_id",{"group_id":list(row)[0]}).fetchone()
        grps.append(list(grp_name))
    grps=json.dumps(grps)
    return grps

@app.route('/msg/get_msgs')
def getmsgs():
    grp_id=request.args.get('id')
    # user = dict(session).get('profile', None)
    # email=user.get('email')
    # msg_id=db.execute("select msg_id from friend_msgs where email1=:email and email2=:grp_id",{"email":email,"grp_id":grp_id}).fetchall()
    msg_id=db.execute("select msg_id from group_msgs where group_id=:grp_id",{"grp_id":grp_id}).fetchall()
    msg_id=list(msg_id)
    msg=[]
    for i in range(len(msg_id)):
        messages=db.execute("select * from messages where message_id=:msg_id",{"msg_id":msg_id[i][0]}).fetchone()
        msg.append(list(messages))
        name=db.execute("select name from profile where email=:email",{"email":msg[2*i][1]}).fetchone()
        msg.append(list(name))
    # grps=db.execute("select group_id from group_users where user_id=:grp_id",{"grp_id":grp_id}).fetchall()
    # for row in grps:
    #     grp=db.execute("select group_id from group_users where group_id=:grp_id and user_id=:user",{"grp_id":list(row)[0],"user":email}).fetchone()
    # grp=list(grp)
    # msg_id=db.execute("select msg_id from group_msgs where group_id=:grp",{"grp":grp}).fetchall()
    # msg_id=list(msg_id)
    # msg=[]
    # for i in range(len(msg_id)):
    #     messages=db.execute("select * from messages where message_id=:msg_id",{"msg_id":msg_id[i][0]}).fetchone()
    #     msg.append(list(messages))
    msg=json.dumps(msg,default=str)
    return msg

@socketio.on('my event')
def test_message(message):
    grp_id=message['grp']
    text=message['message']
    date=message['date']
    time=message['time']
    user = dict(session).get('profile', None)
    email=user.get('email')
    db.execute("insert into messages (from_user_id,message,msg_date,msg_time) values (:email,:text,:date,:time)",{"email":email,"text":text,"date":date,"time":time})
    msg_id=db.execute("select max(message_id) from messages").fetchone()
    msg_id=list(msg_id)
    msg_id=msg_id[0]
    db.execute("insert into group_msgs values(:msg_id,:group_id)",{"msg_id":msg_id,"group_id":grp_id})
    db.commit()

    messages=db.execute("select * from messages where message_id=:msg_id",{"msg_id":msg_id}).fetchall()
    msg=[]
    for row in messages:
        msg.append(list(row))
        name=db.execute("select name from profile where email=:email",{"email":list(row)[1]}).fetchone()
        msg.append(list(name))
    msg=json.dumps(msg,default=str)
    emit('my response', msg, to=grp_id)

@socketio.on('join_room')
def on_join(data):
    user = dict(session).get('profile', None)
    email=user.get('email')
    room = data['room']
    join_room(room)
    print("kek")
    send(email + ' has entered the room.', to=room)

@socketio.on('leave_room')
def on_leave(data):
    user = dict(session).get('profile', None)
    email=user.get('email')
    room = data['room']
    leave_room(room)
    send(email + ' has left the room.', to=room)

@socketio.on('connect')
def test_connect():
    # messages=db.execute("select * from messages").fetchall()
    msg=[]
    # for row in messages:
    #     msg.append(list(row))
    msg=json.dumps(msg,default=str)
    emit('initial connect',msg)

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app)