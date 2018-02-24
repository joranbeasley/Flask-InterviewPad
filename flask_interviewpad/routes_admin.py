from flask import Blueprint, render_template, request, json, flash
from flask_login import current_user, login_required

from flask_interviewpad.constants import COLOR_LIST
from flask_interviewpad.models import Room, User, ActiveRoomUser, db, CandidateEvaluation
from flask_interviewpad.models import create_invite_token
bp = Blueprint('admin','admin',url_prefix='/admin')

@bp.route("/")
@login_required
def index():
    ctx = dict(
        users=User.query.all(),
        rooms=Room.query.all(),
    )

    return render_template("admin-pages/app-admin.html",**ctx)
@bp.route("/room-evaluation/<room_id>")
def room_evaluation(room_id):
    ctx = dict(
        room = Room.query.filter_by(id=room_id),
        room_users = ActiveRoomUser.query.filter_by(room_id=room_id)
    )
    meta = {}

    for user in ctx['room_users']:
        if not user.is_admin:

            candidate = CandidateEvaluation.query.filter_by(candidate_id=user.id,reviewer_id=current_user.id).first()
            if not candidate:
                candidate = CandidateEvaluation(reviewer_id=current_user.id,candidate_id=user.id)
            meta[user.nickname] = {'grades': [], 'notes': candidate.notes or ''}

            meta[user.nickname]['grades'] =  [
                ('Culture Fit', 'culture_fit', candidate.culture_fit or -1),
                ('Technical Skills','technical_skills',candidate.technical_skills or -1),
                ('Enthusiasm to Learn','willingness_to_learn',candidate.willingness_to_learn or -1),
                ('Enthusiasm to Learn','willingness_to_learn',candidate.willingness_to_learn or -1),
                ('Problem Solving','problem_solving',candidate.problem_solving or -1),
                ('Creativity','creative',candidate.creative or -1),
                ('Organized','organized',candidate.organized or -1),
            ]
            ctx['meta']=meta
    return render_template("admin-pages/app-admin-review.html",**ctx)
@bp.route("/reinvite")
def reinvite_guest():
    room_id, user_id = request.args.get('room_id'),request.args.get('user_id')
    user = ActiveRoomUser.query.filter_by(room_id=room_id,id=user_id).first()
    if not user:
        print("Cannot find user:",request.args)
        return json.dumps({"result":"error","reason":"user %s not found in room %s"})
    user.refresh_invite_token()
    db.session.commit()
    return json.dumps({"result":"OK","user":user.to_dict()})
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