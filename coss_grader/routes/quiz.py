from datetime import datetime, timedelta

from flask import abort, Blueprint, render_template, url_for, request, redirect, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms.fields import (
    SubmitField,
    TextField,
    TextAreaField,
    DateTimeField,
    BooleanField,
)
from wtforms.validators import Required

from coss_grader.models import Quiz, Submission, Report
from coss_grader.decorator import admin_only, authenticated_only
from coss_grader.plugins import db

blueprint = Blueprint("quiz", __name__, url_prefix="/quiz")
blueprint.before_request(authenticated_only)


class ManageQuizForm(FlaskForm):
    name = TextField("Name", validators=[Required()])
    info = TextAreaField("Information")
    open_time = DateTimeField(format="%d-%m-%Y %H:%M:%S")
    close_time = DateTimeField(format="%d-%m-%Y %H:%M:%S")
    show_results = BooleanField()
    submit = SubmitField()


@blueprint.route("/list")
def listing():
    page = request.args.get("page", 1, type=int)
    quizzes = Quiz.query.order_by(Quiz.id.desc()).paginate(page, 10, False)
    next_url = (
        url_for("quiz.listing", page=quizzes.next_num) if quizzes.has_next else None
    )
    prev_url = (
        url_for("quiz.listing", page=quizzes.prev_num) if quizzes.has_prev else None
    )
    return render_template(
        "pages/listing.html",
        quizzes=quizzes.items,
        next_url=next_url,
        prev_url=prev_url,
        title="Quiz listing",
    )


@blueprint.route("/results/<quiz_id>")
def result(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if not quiz.show_results and not current_user.is_admin:
        return abort(403)

    results = quiz.submissions.all()
    if not results:
        flash("No one has submitted.", "error")
        return redirect(url_for("quiz.listing"))
    results.sort(key=lambda s: sum(s.scores))
    return render_template(
        "pages/quiz/results.html", results=results, title="Quiz result"
    )


@blueprint.route("/manage/<quiz_id>", methods=["GET", "POST"])
@admin_only
def manage(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = ManageQuizForm()
    form.open_time.default = quiz.open_time
    form.close_time.default = quiz.close_time
    form.name.default = quiz.name
    form.info.default = quiz.info
    form.show_results.default = quiz.show_results

    if form.validate_on_submit():
        quiz.open_time = form.open_time.data
        quiz.close_time = form.close_time.data
        quiz.name = form.name.data
        quiz.info = form.info.data
        quiz.show_results = form.show_results.data

        error = False
        if form.show_results.data:
            plays = quiz.submissions.all()
            for play in plays:
                for score in play.scores:
                    if score < 0:
                        flash(f"{play.owner.name} have not been judged.", "error")
                        error = True
                        break
        if not error:
            db.session.commit()
    else:
        form.process()
    return render_template(
        "pages/quiz/manage.html", form=form, scripts=["manage.js"], title="Manage quiz"
    )


@blueprint.route("/new")
@admin_only
def new():
    q = Quiz(name="New quiz", info="", questions=[])
    return render_template(
        "pages/quiz/editor.html", quiz=q, title="New quiz", scripts=["editor.js"]
    )


@blueprint.route("/play/<quiz_id>")
def play(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    current_time = datetime.utcnow()
    if quiz.open_time and current_time < quiz.open_time:
        flash("Quiz hasn't yet opened.")
        return redirect(url_for("quiz.intro", quiz_id=quiz_id))
    if quiz.close_time and current_time > quiz.close_time:
        flash("Quiz has been closed.")
        return redirect(url_for("quiz.intro", quiz_id=quiz_id))

    play = Submission.query.filter_by(owner_id=current_user.id, quiz_id=quiz.id).first()
    if not play:
        play = Submission(owner_id=current_user.id, quiz_id=quiz.id)
        db.session.add(play)
        db.session.commit()

    if play.is_done:
        flash("You've already done that quiz.")
        return redirect(url_for("quiz.listing"))
    time_left = (timedelta(hours=2) - (datetime.utcnow() - play.start_time)).seconds

    return render_template(
        "pages/quiz/player.html",
        play=play,
        quiz=quiz,
        time_left=time_left,
        title=quiz.name,
        scripts=["play.js", "watcher.js"],
    )


@blueprint.route("/intro/<quiz_id>")
def intro(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template(
        "pages/quiz/intro.html",
        info=quiz.info,
        quiz_id=quiz.id,
        title="Quiz information",
    )


@blueprint.route("/judge/<play_id>")
@admin_only
def judge(play_id):
    play = Submission.query.get_or_404(play_id)
    if not play.is_done:
        flash("Player is not done with their play.")
        return redirect(url_for("home.index"))

    quiz = play.quiz
    events = play.events.all()
    return render_template(
        "pages/quiz/judger.html",
        JUDGING_MODE=True,
        events=events,
        title="Judge play",
        quiz=quiz,
        play=play,
        scripts=["judger.js"],
    )


@blueprint.route("/result/<play_id>")
def play_result(play_id):
    play = Submission.query.get_or_404(play_id)
    if not play.is_done:
        flash("Player is not done with their play.")
        return redirect(url_for("home.index"))
    if play.owner_id != current_user.id or not current_user.is_admin:
        flash("You are not the owner of the play.")
        return redirect(url_for("home.index"))

    quiz = play.quiz
    return render_template(
        "pages/quiz/judger.html",
        JUDGING_MODE=False,
        title="Results",
        quiz=quiz,
        play=play,
        scripts=["judger.js"],
    )


@blueprint.route("/reports/<quiz_id>")
@admin_only
def see_reports(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    events = quiz.events.order_by(Report.datetime.desc()).all()
    return render_template(
        "pages/quiz/reports.html",
        title="Reports",
        events=events,
        quiz_id=quiz.id,
        scripts=["reports.js"],
    )


@blueprint.route("/result/mine")
def mine_result():
    return render_template("pages/results.html", title="Results")
