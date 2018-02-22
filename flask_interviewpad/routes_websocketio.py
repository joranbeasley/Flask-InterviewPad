import base64
from dateutil.parser import parse as dateparse
import datetime
from flask_socketio import SocketIO, disconnect, emit



# print(create_token("joran",1))
sock = SocketIO()
@sock.on('connect')
def on_connect():
    print("OK USER CONNECTED... action pending")

@sock.on('join_room')
def on_room_join(payload):
    try:
        keys = "username room_id issued_at".split()
        p2 = dict(zip(keys,base64.b64decode(payload.get('token')).decode("latin1").split("|")))
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
    if (p2['username'] != payload['username']):
        emit('error', 'invalid token username!... reload page to re-acquire')

    print("issued:",issued_ago)
    print("User wishes to join room",p2)