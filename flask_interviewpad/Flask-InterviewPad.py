from flask import Flask, render_template

from flask_interviewpad.routes_admin import bp
from flask_interviewpad.routes_websocketio import sock
from flask_interviewpad.models import create_token

app = Flask(__name__)
app.debug = True
app.secret_key = "A secret that should not B shared!"
app.register_blueprint(bp)

@app.route("/")
def index():
    return "Sorry This site is not open to the public"

@app.route("/room/<room_id>")
def join_room(room_id):
    ctx = dict(
        username="Joran",
        room_name="Interview-Tyler",
        auth_token=create_token(1,1)
    )
    return render_template("pages/index.html",**ctx)

@app.route('/join/<token>')
def join_with_token(token):
    pass

@app.route("/login")
def login():
    return render_template('admin-pages/app-login.html')



if __name__ == '__main__':



    sock.init_app(app)
    # app.run(debug=True)
    sock.run(app)