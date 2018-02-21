from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return "Sorry This site is not open to the public"
@app.route("/room/<room_id>")
def join_room(room_id):
    ctx = dict(
        username="Joran",
        room_name="Interview-Tyler"
    )
    return render_template("pages/index.html",**ctx)
@app.route('/join/<token>')
def join_with_token(token):
    pass



if __name__ == '__main__':
    app.run(debug=True)
