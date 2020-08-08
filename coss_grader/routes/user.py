from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, TextField, PasswordField, SelectField
from wtforms.validators import Required, EqualTo

from coss_grader.models import User, ClassEnum
from coss_grader.plugins import db

blueprint = Blueprint("user", __name__, url_prefix="/user")


class LoginForm(FlaskForm):
    username = TextField("Username", validators=[Required()])
    password = PasswordField("Password", validators=[Required()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    name = TextField("Name", validators=[Required()])
    classroom = SelectField("Class")
    username = TextField("Username", validators=[Required()])
    password = PasswordField(
        "Password",
        validators=[Required(), EqualTo("confirm", message="Passwords must match")],
    )
    confirm = PasswordField("Repeat Password")
    submit = SubmitField("Submit")


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.check_password(form.password.data):
            flash("Wrong username/password")
            return redirect(url_for("user.login"))

        login_user(user)
        return redirect(url_for("home.index"))
    return render_template("pages/login.html", form=form, title="Login")


@blueprint.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    form = RegisterForm()
    form.classroom.choices = [("", "Classroom")]
    for c in ClassEnum:
        if c.value == 99:
            continue
        form.classroom.choices.append((str(c.value), c.name.replace("_", " ")))

    if form.validate_on_submit():
        if not form.classroom.data.isnumeric():
            flash("Invalid classroom.")
            return render_template("pages/register.html", form=form, title="Register")

        new_user = User(
            name=form.name.data,
            username=form.username.data.lower(),
            classroom_=int(form.classroom.data),
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash("Registered.")
        return redirect(url_for("home.index"))
    return render_template("pages/register.html", form=form, title="Register")


@blueprint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home.index"))
