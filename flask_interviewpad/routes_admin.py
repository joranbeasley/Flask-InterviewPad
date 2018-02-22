from flask import Blueprint, render_template

bp = Blueprint('admin','admin',url_prefix='/admin')

@bp.route("/")
def index():
    return render_template("admin-pages/app-admin.html")