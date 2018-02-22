from flask import Blueprint, render_template, request, json, flash
from flask_login import current_user, login_required

from flask_interviewpad.constants import COLOR_LIST
from flask_interviewpad.models import Room, User, ActiveRoomUser, db

bp = Blueprint('admin','admin',url_prefix='/admin')

@bp.route("/")
@login_required
def index():
    ctx = dict(
        users=User.query.all(),
        rooms=Room.query.all(),
    )

    return render_template("admin-pages/app-admin.html",**ctx)

@bp.route("/create/<what>",methods=["POST"])
def create_item(what):
    my_id = 1 # current_user.id
    if what == "user":
        u = User(
            realname=request.form.get('realname'),
            nickname=request.form.get('nickname'),
            email=request.form.get('email'),
            password=request.form.get('password'),
        )
        db.session.add(u)
        db.session.commit()
        flash("USER CREATED!")
        print("Add User")
    elif what == "room":
        user_id = 1 # current_user.id
        r = Room(
                room_name=request.form.get('room_name'),
                owner_id=my_id,
                invite_only=bool(request.form.get('invite_only')),
            )
        db.session.add(r)
        db.session.commit()
        owner_invite = ActiveRoomUser(
            room_id=r.id,
            user_id=current_user.id,
        )
        print("Add Room/Session")
    elif what == "reportcard":
        print("Add ReportCard")
    elif what == "invitation":
        print("Add Invitation")
        print(request.form)
        room_invite = ActiveRoomUser(
            nickname=request.form.get('nickname'),
            realname=request.form.get('realname'),
            email=request.form.get('email'),
            room_id=request.form.get("room_id"),
            user_color=COLOR_LIST[ActiveRoomUser.query.filter_by(room_id=request.form.get('room_id')).count()%20]
        )
        db.session.add(room_invite)
        db.session.commit()
        return json.dumps(room_invite.to_dict())
    print(request.form)