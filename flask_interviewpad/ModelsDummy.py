import datetime
import time
import hashlib

from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import current_user, random

db = SQLAlchemy()
def create_invite_token():
    return hashlib.md5(b"%s-@XKCD!-%s"%(time.time(),random.random())).hexdigest()
def after_n_minutes(n):
    return lambda:datetime.datetime.now()+datetime.timedelta(seconds=int(n*60))

class CandidateEvaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reviewer = db.relationship('User', backref=db.backref('my_candidates', lazy=True))
    candidate_id = db.Column(db.Integer, db.ForeignKey('active_room_user.id'))
    candidate = db.relationship('ActiveRoomUser', backref=db.backref('my_reviewers', lazy=True))
    notes = db.Column(db.Text,nullable=True,default="")
    technical_skills = db.Column(db.Integer,nullable=True,default=None)
    willingness_to_learn = db.Column(db.Integer,nullable=True,default=None)
    culture_fit = db.Column(db.Integer,nullable=True,default=None)
    problem_solving = db.Column(db.Integer,nullable=True,default=None)
    creative = db.Column(db.Integer,nullable=True,default=None)
    organized = db.Column(db.Integer,nullable=True,default=None)



class Room(db.Model):
    pass
class User(db.Model):
    pass
class ProblemStatement(db.Model):
    pass
class ProblemStatementTestCase(db.Model):
    pass

class UserSolutions(db.Model):
    solution = db.Column(db.Text())


class ActiveRoomUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(20))
    realname = db.Column(db.String(20))
    email = db.Column(db.String(80))
    room_id = db.Column(db.Integer,db.ForeignKey('room.id'))
    room = db.relationship('Room', backref=db.backref('active_users', lazy=True))
    sid = db.Column(db.String(80))
    is_admin = db.Column(db.Boolean,default=False)
    is_active = db.Column(db.Boolean,default=True)
    state = db.Column(db.String(10),default="pending")
    invite_code = db.Column(db.String(80),default=create_invite_token)
    invite_expires = db.Column(db.DateTime,default=after_n_minutes(80))
    session_started = db.Column(db.DateTime,default=datetime.datetime.now)
    session_ended = db.Column(db.DateTime, default=None,nullable=True)
    def is_alive(self):
        if self.is_admin:
            return True
        if self.is_active:
            if not self.session_ended and self.invite_expires < datetime.datetime.now():
                return True
            if (datetime.datetime.now()-self.session_ended) < datetime.timedelta(minutes=30):
                return True



    def to_dict(self):
        return {
            "email":self.email,
            "room_name":self.room.room_name,
            "nickname":self.nickname,
            "username":self.nickname,
            "state":self.state,
            "is_admin":self.is_admin,
            "session_started":self.session_started.isoformat(),
            "session_ended":self.session_ended.isoformat() if self.session_ended else None,
            "is_active":self.is_active
        }
    @staticmethod
    def leave_room(room=None):
        my_active_users = ActiveRoomUser.query.filter_by(sid=request.sid)
        if room:
            my_active_users = my_active_users.filter_by(room_id=room.id)
        my_active_users.update(session_ended=datetime.datetime.now(),state="disconnected")
        db.session.commit()

    @staticmethod
    def join_room(room):
        existing_session = ActiveRoomUser.query.filter_by(room_id=room.id,email=current_user.email).order_by('-id').first()
        if existing_session:
            if not existing_session.session_ended:
                raise ValueError("User Is Already In this room!")
            else:
                timedelta = datetime.datetime.now() - existing_session.session_ended
                if timedelta < datetime.timedelta(hours=1) and existing_session.is_active:
                    existing_session.session_ended = None
                    existing_session.state = 'active'
                    existing_session.sid = request.sid
                    db.session.commit()
                    return
                else:
                    raise ValueError("Sorry This Session is Expired")
        is_admin = False
        if current_user.is_authenticated and getattr(current_user,'is_real_user',False):
            is_admin = True
        active_user = ActiveRoomUser(room_id=room.id,
                                     email=current_user.email, nickname=current_user.nickname,
                                     sid=request.sid, is_admin=is_admin)
        db.session.add(active_user)
        print("Session Joined")
        db.session.commit()