import base64
import datetime
import traceback

from flask import Flask, render_template, request, flash, redirect, session
from flask_login import login_user, current_user, logout_user

from flask_interviewpad.constants import DB_URI
from flask_interviewpad.flask_filters import MyFilters
from flask_interviewpad.routes_admin import bp
from flask_interviewpad.routes_websocketio import sock
from flask_interviewpad.models import create_token, init_app, User, Room, ActiveRoomUser, db

app = Flask(__name__)
app.debug = True
app.secret_key = "A secret that should not B shared!"
app.register_blueprint(bp)
MyFilters.init_app(app)
@app.route("/")
def index():
    return "Sorry This site is not open to the public"
@app.route("/logout")
def logout():
    logout_user()
    del session['X-Auth']
    return redirect('/login')
@app.route("/room/<room_id>")
def join_room(room_id):
    room = Room.query.get(room_id)
    room_user=None
    if current_user and getattr(current_user,'is_admin',False):
        room_user = room.all_usersQ().filter_by(user_id=current_user.id).first()
        if not room_user:
            room_user = ActiveRoomUser(
                user_id=current_user.id,
                nickname=current_user.nickname,
                realname=current_user.realname,
                email=current_user.email,
                state="active",
                room_id=room_id,
                invite_expires=datetime.datetime.now()+datetime.timedelta(days=64)
            )
            db.session.add(room_user)
        room_user.temporary_token = room_user.make_temp_token()
        db.session.commit()
    else:
        try:
            auth = base64.b64decode(session.get('X-Auth')).decode('latin1')
        except:
            traceback.print_exc()
            return "Not Authorized (invalid invite)",405

        invite_code,room_user_id,auth_room_id = auth.split(":")
        if "%s"%room_id != "%s"%auth_room_id:
            return "Not Authorized(room mismatch!)",405
        try:
            room_user =  ActiveRoomUser.query.filter_by(id=room_user_id).first()
        except:
            raise
        else:
            if not room_user:
                return "Not Authorized (invalid options)", 405
            if room_user.invite_code != invite_code:
                return "Not Authorized (invalid code)",405
            elif room_user.invite_expires < datetime.datetime.now():

                return "Not Authorized (invite expired)",405
            else:
                room_user.temporary_token = room_user.make_temp_token()
                db.session.commit()
    ctx = dict(
        user=room_user,
        room=room,
    )
    return render_template("pages/index.html",**ctx)

@app.route('/join/<token>')
def join_with_token(token):
    user = ActiveRoomUser.query.filter_by(invite_code=token).first()
    if not user:
        return "Not authorized!",405
    if user.invite_expires < datetime.datetime.now():
        print("Token Expired at:", user.invite_expires)
        return "Invite Expired!",405
    print(user.to_dict())
    session['X-Auth'] = base64.b64encode(("%s:%s:%s"%(token,user.id,user.room_id)).encode("latin1"))
    return redirect("/room/%s"%user.room_id)


@app.route("/login",methods=["GET","POST"])
def login():
    if request.form:
        user = User.login(**request.form.to_dict())
        if user:
            flash("Login Success!")
            login_user(user)
            return redirect("/admin")
    return render_template('admin-pages/app-login.html')



if __name__ == '__main__':


    init_app(app,DB_URI)
    sock.init_app(app)
    # app.run(debug=True)
    sock.run(app)