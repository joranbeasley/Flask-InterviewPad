import base64
from dateutil.parser import parse as dateparse
import datetime

from flask import request, session
from flask_socketio import SocketIO, disconnect, emit, join_room

# print(create_token("joran",1))
from flask_interviewpad.models import ActiveRoomUser, db

sock = SocketIO()
@sock.on('connect')
def on_connect():
    print("OK USER CONNECTED... action pending")
@sock.on("disconnect")
def on_disconnect():
    print("User Disconnect?",request.sid)

    users_matching = ActiveRoomUser.query.filter_by(sid=request.sid)
    if users_matching.count()>1:
        print("WARNING FOUND MORE THAN 1 USER WITH SID ONLY DEALING WITH FIRST")
    user = users_matching.first()
    if not user:
        print("ERROR USER NOT FOUND!!!... this is troubling")
    user.session_ended = datetime.datetime.now()
    user.state = "disconnected"
    db.session.commit()
    emit('user_left',user.to_dict(),room=str(user.room_id))

@sock.on("sync_request")
def request_sync(payload):
    room_user = ActiveRoomUser.query.filter_by(sid=request.sid).first()
    room = room_user.room
    payload = {"user":room_user.to_dict(),"room":room.to_dict()}
    emit('sync_result',payload,broadcast=False)

@sock.on('join_room')
def on_room_join(payload):
    try:
        token = payload.get('token')
        keys = "user_id room_id issued_at".split()
        p2 = dict(zip(keys,base64.b64decode(token).decode("latin1").split("|")))

    except: # token needs to be [js] btoa("{ username }|{ room_id }|{ token_issued_at }") [/js]
        emit('error','invalid token!... reload page to re-acquire')
        return disconnect()
    try:
        issued_ago = datetime.datetime.now() - dateparse(p2['issued_at'])
    except: # see above about token
        emit('error', 'invalid token issue date!... reload page to re-acquire')
        return disconnect()
    if issued_ago > datetime.timedelta(seconds=60*5):
        emit('error','invite token expired... reload page to re-acquire')
        return disconnect()

    room_user= ActiveRoomUser.query.filter_by(temporary_token=token).first()
    if not room_user:
        emit('error', 'invite token not found... reload page to re-acquire')
        return disconnect()
    if (room_user.nickname != payload['username']):
        emit('error', 'invalid token username!... reload page to re-acquire')
    print("USER:",room_user.to_dict())
    print("issued:",issued_ago)
    print("User wishes to join room",p2)
    room_user.sid = request.sid
    room_user.state = "active"
    db.session.commit()
    join_room("%s"%room_user.room_id)
    request_sync({})
    data = room_user.to_dict()

    emit('user_joined',data,room=str(room_user.room_id))
@sock.on("push_select")
def on_push_select(payload):
    room_user = ActiveRoomUser.query.filter_by(id=payload['user_id']).first()
    if not room_user:
        print("ERROR No User?")
        return;
    if not room_user.sid == request.sid:
        print("ERROR MISMATCH SID?")
        return
    if not room_user.room_id == payload['room_id']:
        print("Error mismatch room!")
        return
    payload['user_color'] = room_user.user_color
    emit("notify_editor_select",payload,include_self=False,room=str(room_user.room_id))
@sock.on("push_change")
def on_push_change(payload):
    room_user = ActiveRoomUser.query.filter_by(id=payload['user_id']).first()
    if not room_user:
        print("ERROR No User?")
        return;
    if not room_user.sid == request.sid:
        print("ERROR MISMATCH SID?")
        return
    if not room_user.room_id == payload['room_id']:
        print("Error mismatch room!")
        return
    payload['user_color'] = room_user.user_color
    room_user.room.apply_edit(payload['change'])
    emit('notify_editor_change',payload,room=str(room_user.room_id),include_self=False)

@sock.on('push_blur')
def push_blur(payload):
    room_user = ActiveRoomUser.query.filter_by(id=payload['user_id']).first()
    if not room_user:
        print("ERROR No User?")
        return;
    if not room_user.sid == request.sid:
        print("ERROR MISMATCH SID?")
        return
    if not room_user.room_id == payload['room_id']:
        print("Error mismatch room!")
        return
    payload['user'] = room_user.to_dict()
    for u in room_user.room.active_admins():
        print("NOTIFY BLUR:",u.email)
        emit('notify_user_blur', payload, room=u.sid,)

@sock.on('push_unblur')
def push_blur(payload):
    room_user = ActiveRoomUser.query.filter_by(id=payload['user_id']).first()
    if not room_user:
        print("ERROR No User?")
        return;
    if not room_user.sid == request.sid:
        print("ERROR MISMATCH SID?")
        return
    if not room_user.room_id == payload['room_id']:
        print("Error mismatch room!")
        return
    payload['user'] = room_user.to_dict()
    for u in room_user.room.active_admins():
        print("NOTIFY UNBLUR:",u.email)
        emit('notify_user_unblur', payload, room=u.sid,)

@sock.on('push_chat_message')
def on_chat_message(payload):
    room_user = ActiveRoomUser.query.filter_by(id=payload['user_id']).first()
    if not room_user:
        print("ERROR No User?")
        return;
    if not room_user.sid == request.sid:
        print("ERROR MISMATCH SID?")
        return
    if not room_user.room_id == payload['room_id']:
        print("Error mismatch room!")
        return
    payload['user'] = room_user.to_dict()
    emit("notify_chat_message",payload,room=str(payload['room_id']))