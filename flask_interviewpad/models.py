import base64
import datetime
import time
import hashlib
import random

from flask import request, session
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_interviewpad.constants import COLOR_LIST
db = SQLAlchemy()
login_manager = LoginManager()
def create_invite_token():
    return hashlib.md5(("%s-@XKCD!-%s"%(time.time(),random.random())).encode('latin1')).hexdigest()
def after_n_minutes(n):
    return lambda:datetime.datetime.now()+datetime.timedelta(seconds=int(n*60))

def create_token(user_id,room_id):
    token_fmt= "{user_id}|{room_id}|{issued_at}"
    plain = token_fmt.format(user_id=user_id,room_id=room_id,issued_at=datetime.datetime.now())
    return base64.b64encode(plain.encode('latin1')).decode('latin1')

def init_app(app,db_uri=None):
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri or app.config.get('SQLALCHEMY_DATABASE_URI','sqlite:///./test.db')
    db.app = app
    db.init_app(db.app)
    login_manager.init_app(app)

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
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref=db.backref('my_rooms', lazy=True))
    room_name=db.Column(db.String(40))
    invite_only = db.Column(db.Boolean,default=True)
    editing_enabled = db.Column(db.Boolean,default=True)
    language = db.Column(db.String(20), default="python")
    is_active = db.Column(db.Boolean,default=True)
    current_text=db.Column(db.Text(),default="")
    created=db.Column(db.DateTime,default=datetime.datetime.now)
    def to_dict(self):
        return {
            "room_name":self.room_name,
            "language":self.language,
            "current_text":self.current_text,
            "users":self.all_users(True)
        }
    def active_usersQ(self):
        in_room = ActiveRoomUser.state.in_(("active", "inactive"))
        return self.all_usersQ().filter(in_room)
    def active_users(self,as_dict=False):
        users = self.active_usersQ().all()
        if as_dict:
            return [u.to_dict() for u in users]
        return users
    def active_users_count(self):
        return self.active_usersQ().count()

    def all_usersQ(self):
        return ActiveRoomUser.query.filter_by(room_id=self.id)
    def all_users(self,as_dict=False):
        users = self.all_usersQ().all()
        if as_dict:
            return [u.to_dict() for u in users]
        return users
    def all_users_count(self):
        return self.all_usersQ().count()

    def get_users_nicknames(self):
        return [self.owner.nickname,] + [u.nickname for u in self.invited_users]
    def is_owner(self):
        return current_user.is_authenticated and current_user.id == self.owner_id
    def verify_allowed(self):
        return current_user.is_authenticated or ActiveRoomUser.query.filter_by(room_id=self.id,email=current_user.email).first()

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(80),unique=True)
    realname = db.Column(db.String(80))
    nickname = db.Column(db.String(20))
    Xpassword = db.Column(db.String(80))
    # optional parameters
    sid = db.Column(db.String(50),default=None, nullable=True)
    ip_address = db.Column(db.String(20),default=None, nullable=True)
    reset_token = db.Column(db.String(80),default=None,nullable=True)
    is_active = db.Column(db.Boolean,default=True)
    is_anonymous=False
    is_real_user=True
    is_admin = True
    # def to_dict(self):
    #     return user2dict(self)
    @property
    def is_authenticated(self):
        return bool(self.id) and self.id == current_user.id
    @staticmethod
    def exchange_token(ident_token):
        invite = ActiveRoomUser.query.filter_by(invite_code=ident_token).first()
        if not invite:
            return False
        if invite.invite_expires < datetime.datetime.now():
            print("Invitation Expired At:%s"%invite.invite_expires)
        session["X-authentication"] = ident_token
        session["X-email"]=invite.email
        session["X-room_id"]=invite.room_id
        return invite.to_user()

    @staticmethod
    def alternate_user_loader():
        invite_tok = session.get('X-authentication', None)
        invite_email = session.get('X-email', None)
        invite_room_id = session.get('X-room_id', None)
        if not invite_tok or not invite_email:
            return None
        invite = ActiveRoomUser.query.filter_by(token_invite=invite_tok,email=invite_email,room_id=invite_room_id).first()
        if not invite:
            return None
        return invite.to_user()
    @staticmethod
    @login_manager.user_loader
    def user_loader(id):
        return User.query.filter_by(id=id).first() or User.alternate_user_loader()



    @classmethod
    def login(cls,username,password):
        return User.query.filter_by(email=username,Xpassword=User.pw_enc(password)).first()
    def get_id(self):
        return self.id
    @classmethod
    def pw_enc(cls,pw):
        if not isinstance(pw,bytes):
            pw = pw.encode('latin1')
        return hashlib.sha256(pw).hexdigest()
    def __init__(self,**kwargs):
        if 'Xpassword' in kwargs:
            raise Exception("Do not pass in Xpassword... pass in password")
        if 'password' in kwargs:
            kwargs['Xpassword'] = self.pw_enc(kwargs.pop('password'))
        db.Model.__init__(self,**kwargs)
    @property
    def password(self):
        return "Nope, that wont work!"
    @password.setter
    def set_password(self,password):
        self.Xpassword = self.pw_enc(password)

class ProblemStatement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    difficulty=db.Column(db.Integer)
    problem_markdown=db.Column(db.Text)
    category=db.Column(db.String(30),default="python")
    initial_text = db.Column(db.String(120),default="#solution below")

class ProblemStatementTestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem_statement.id'))
    problem = db.relationship('ProblemStatement', backref=db.backref('testcases', lazy=True))
    testcase_code = db.Column(db.String(80))

class UserSolution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer,db.ForeignKey('active_room_user.id'))
    candidate = db.relationship('ActiveRoomUser', backref=db.backref('candidate_solutions', lazy=True))
    language = db.Column(db.String(20), default="python")
    solution_code = db.Column(db.Text)
    correct = db.Column(db.Boolean,default=False)
    letter_grade = db.Column(db.String(1),default="I")


def get_random_color():
    return random.choice(COLOR_LIST)

class ActiveRoomUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(10))
    realname = db.Column(db.String(60))
    email = db.Column(db.String(80))
    room_id = db.Column(db.Integer,db.ForeignKey('room.id'))
    room = db.relationship('Room', backref=db.backref('active_users', lazy=True))
    sid = db.Column(db.String(80),nullable=True,default=None)
    user_id = db.Column(db.Integer,default=None,nullable=True)
    is_active = db.Column(db.Boolean,default=True)
    state = db.Column(db.String(10),default="pending")
    user_color = db.Column(db.String,default=get_random_color)
    temporary_token  = db.Column(db.String(60),default="")
    invite_code = db.Column(db.String(80),default=create_invite_token)
    invite_expires = db.Column(db.DateTime,default=after_n_minutes(80))
    session_started = db.Column(db.DateTime,default=datetime.datetime.now)
    session_ended = db.Column(db.DateTime, default=None,nullable=True)
    @property
    def is_admin(self):
        return self.user_id
    def make_temp_token(self):
        self.temporary_token = create_token(self.user_id,self.room_id)
        return self.temporary_token
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
            "url":request.host_url+"join/"+self.invite_code,
            "is_admin":self.is_admin,
            "user_color":self.user_color,
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
    def join_room(token):
        try:
            keys = "user_id room_id issued_at".split()
            p2 = dict(zip(keys, base64.b64decode(token).decode("latin1").split("|")))
        except:  # token needs to be [js] btoa("{ username }|{ room_id }|{ token_issued_at }") [/js]
            raise Exception("invalid token!")


if __name__ == "__main__":
    import flask
    from flask_interviewpad.constants import DB_URI, COLOR_LIST

    app = flask.Flask(__name__)
    init_app(app,DB_URI)
    db.create_all()
