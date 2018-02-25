import base64
import traceback

from dateutil.parser import parse as dateparse
import datetime

from flask import request, session
from flask_socketio import SocketIO, disconnect, emit, join_room

# print(create_token("joran",1))
from flask_interviewpad.models import ActiveRoomUser, db
class AuthorizationError(Exception):
    pass

sock = SocketIO()
class SockAuth:
    @staticmethod
    def authorized_room(room_user):
        if not room_user:
            raise AuthorizationError("ERROR No User?")
        if not room_user.sid == request.sid:
            raise AuthorizationError("ERROR MISMATCH SID?")
        return room_user.room_id

    @staticmethod
    def required(fn):
        def __inner(payload,*args,**kwargs):
            try:
                room_user = ActiveRoomUser.query.filter_by(id=payload['auth']['user_id']).first()
            except:
                print("PAYLOAD CHECK:", payload)
                raise
            if (SockAuth.authorized_room(room_user) != payload['auth']['room_id']):
                raise AuthorizationError("Room Authorization mismatch")
            try:
                return fn(payload,room_user,*args,**kwargs)
            except:
                raise
        return __inner

class TokenManager:
    @staticmethod
    def inspect(token):
        try:
            keys = "user_id room_id issued_at".split()
            p2 = dict(zip(keys,base64.b64decode(token).decode("latin1").split("|")))
        except: # token needs to be [js] btoa("{ username }|{ room_id }|{ token_issued_at }") [/js]
            traceback.print_exc()
            print("Malformed token:",token)
            raise AuthorizationError('invalid token(malformed)!... reload page to re-acquire')

        try:
            issued_ago = datetime.datetime.now() - dateparse(p2['issued_at'])
        except: # see above about token
            raise AuthorizationError('invalid token issue date!... reload page to re-acquire')
        if issued_ago > datetime.timedelta(seconds=60*5):
            raise AuthorizationError('invite token expired... reload page to re-acquire')
    @staticmethod
    def exchange(token):
        TokenManager.inspect(token)
        room_user = ActiveRoomUser.query.filter_by(temporary_token=token).first()
        if not room_user:
            raise AuthorizationError('invite token user not found... reload page to re-acquire')
        return room_user
    @staticmethod
    def get_verified_user(token,username):
        room_user = TokenManager.exchange(token)
        if (room_user.nickname != username):
            raise AuthorizationError('invalid token username!... reload page to re-acquire')
        return room_user
def get_room_dict(room_user):
    return room_user.room.to_dict(users="all") if getattr(room_user,'is_admin',False) else room_user.room.to_dict(users="active")


# PUBLIC INTERFACE
@sock.on('connect')
def on_connect():
    print("OK USER CONNECTED... action pending",request.sid)
@sock.on("disconnect")
def on_disconnect():
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


# LOGGED IN INTERFACE
@sock.on("sync_request")
@SockAuth.required
def request_sync(payload,room_user):
    payload = {"room": get_room_dict(room_user), "current_user": room_user.to_dict()}
    emit('sync_result',payload,broadcast=False)

@sock.on("request_users")
@SockAuth.required
def request_users(payload,room_user):
    if room_user.is_admin:
        payload = {"user": room_user.to_dict(), "room": room_user.room.to_dict(users="all")}
    else:
        payload = {"user": room_user.to_dict(), "room": room_user.room.to_dict(users="active")}
    emit('users_list', payload, broadcast=False)


@sock.on('handshake')
def on_room_join(payload):
    token = payload.get('token',None)
    if not token:
        print("Reject Handshake: missing token?")
        emit('handshake_rejected', {'reason':"Missing Token"})
        return disconnect()
    else:
        try:
            room_user = TokenManager.get_verified_user(token,payload.get('username'))
        except AuthorizationError as e:
            print("Reject Handshake: %s? "%e)
            emit('handshake_rejected', {'reason':str(e)})
            return disconnect()


    room_user.sid = request.sid
    room_user.state = "active"
    db.session.commit()
    join_room("%s"%room_user.room_id)
    data = room_user.to_dict()
    payload = {"room":get_room_dict(room_user),"current_user":data}
    emit("handshake_accepted",payload,broadcast=False)
    emit('user_joined',data,room=str(room_user.room_id))

@sock.on("push_select")
@SockAuth.required
def on_push_select(payload,room_user):
    payload['user_color'] = room_user.user_color
    emit("notify_editor_select",payload,include_self=False,room=str(room_user.room_id))
@sock.on("push_change")
@SockAuth.required
def on_push_change(payload,room_user):
    payload['user_color'] = room_user.user_color
    room_user.room.apply_edit(payload['change'])
    emit('notify_editor_change',payload,room=str(room_user.room_id),include_self=False)

@sock.on('push_blur')
@SockAuth.required
def push_blur(payload,room_user):
    payload['user'] = room_user.to_dict()
    for u in room_user.room.active_admins():
        print("NOTIFY BLUR:",u.email)
        emit('notify_user_blur', payload, room=u.sid,)

@sock.on('push_unblur')
@SockAuth.required
def push_blur(payload,room_user):
    payload['user'] = room_user.to_dict()
    for u in room_user.room.active_admins():
        emit('notify_user_unblur', payload, room=u.sid,)

@sock.on('push_chat_message')
@SockAuth.required
def on_chat_message(payload,room_user):
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