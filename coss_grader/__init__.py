__version__ = "0.1.0"

import json

from flask import Flask, flash, redirect, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


def create_app(config_file="config.json"):
    with open(config_file, "r") as f:
        data = json.load(f)

    if "SENTRY_URL" in data:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        sentry_sdk.init(dsn=data["SENTRY_URL"], integrations=[FlaskIntegration()])

    app = Flask(__name__, static_url_path="", static_folder="public")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config.from_mapping(data)

    # Plugins init
    # ---------------------------------------
    from coss_grader.plugins import (
        admin,
        db,
        login_manager,
        md,
        migrate,
    )

    admin.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    app.jinja_env.filters["md"] = md

    # AdminView init
    # ---------------------------------------
    from coss_grader.models import Submission, Question, Quiz, User, Role

    admin.add_views(
        AdminView(Question, db.session),
        AdminView(Quiz, db.session, endpoint="quiz-admin"),
        AdminView(Role, db.session),
        AdminView(Submission, db.session),
        AdminView(User, db.session, endpoint="user-admin"),
    )

    # Blueprints
    # ---------------------------------------
    from coss_grader.routes import api, home, quiz, user

    app.register_blueprint(api.blueprint)
    app.register_blueprint(home.blueprint)
    app.register_blueprint(quiz.blueprint)
    app.register_blueprint(user.blueprint)

    @app.before_first_request
    def init_db():
        db.create_all()

    return app


class AdminView(ModelView):
    column_exclude_list = ["password_hash"]

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash("You must be an admin to see this page.", "negative")
        return redirect(url_for("home.index"))
