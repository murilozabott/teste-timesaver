from flask import Blueprint, redirect, render_template, url_for

webui_bp = Blueprint("webui", __name__, template_folder="templates", static_folder="static")


@webui_bp.route("/")
def index():
    return redirect(url_for("webui.login"))


@webui_bp.route("/login")
def login():
    return render_template("webui/login.html")


@webui_bp.route("/doctors")
def doctors():
    return render_template("webui/doctors.html")


@webui_bp.route("/patients")
def patients():
    return render_template("webui/patients.html")


@webui_bp.route("/appointments")
def appointments():
    return render_template("webui/appointments.html")


def init_app(app):
    from flask_bootstrap import Bootstrap5

    Bootstrap5(app)
    app.register_blueprint(webui_bp)
