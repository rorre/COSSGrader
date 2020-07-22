from flask import Blueprint, request, jsonify
from flask_login import current_user

from coss_grader.decorator import admin_only
from coss_grader.models import Quiz, Question, Submission, Report
from coss_grader.plugins import db

from typing import List, Dict, Any

blueprint = Blueprint("api", __name__, url_prefix="/api")


@blueprint.errorhandler(500)
def internal_server_error(e):
    return jsonify(err="A server error has occured.")


@blueprint.errorhandler(404)
def not_found(e):
    return jsonify(err="Resource not found.")


@blueprint.route("/quiz/new", methods=["POST"])
@admin_only
def new_quiz():
    json: Dict[str, Any] = request.json

    title: str = json.get("title", "Untitled quiz")
    info: str = json.get("info", "")
    questions: List[Dict[str, Any]] = json.get("questions")

    if not questions:
        return jsonify(err="No questions provided."), 400

    quiz = Quiz(name=title, info=info, owner_id=current_user.id)

    for q in questions:
        q_obj = Question(
            question=q.get("question"),
            is_essay=q.get("is_essay"),
            answer=q.get("answer"),
            options=q.get("options"),
            quiz=quiz,
        )
        quiz.questions.append(q_obj)
        db.session.add(q_obj)
    db.session.add(quiz)
    db.session.commit()

    return jsonify(msg="OK")


@blueprint.route("/play/<play_id>/save", methods=["POST"])
def save_progress(play_id):
    play = Submission.query.get(play_id)
    if not play:
        return jsonify(err="Cannot find that Play ID."), 400

    json: Dict[str, Any] = request.json
    questions = play.quiz.questions.all()
    play.options = json["answers"]
    judge_score(play, questions)
    db.session.commit()
    return jsonify(msg="OK")


@blueprint.route("/play/<play_id>/finish", methods=["POST"])
def finish_play(play_id):
    play = Submission.query.get(play_id)
    if not play:
        return jsonify(err="Cannot find that Play ID."), 400

    json: Dict[str, Any] = request.json
    questions = play.quiz.questions.all()
    play.options = json["answers"]
    play.is_done = True

    judge_score(play, questions)
    db.session.commit()
    return jsonify(msg="OK")


@blueprint.route("/play/<play_id>/set", methods=["POST"])
def set_score(play_id):
    play = Submission.query.get(play_id)
    if not play:
        return jsonify(err="Cannot find that Play ID."), 400

    json: Dict[str, Any] = request.json
    play.scores = json["scores"]
    db.session.commit()
    return jsonify(msg="OK")


@blueprint.route("/play/<play_id>/report", methods=["POST"])
def report_play(play_id):
    play = Submission.query.get(play_id)
    if not play:
        return jsonify(err="Cannot find that Play ID."), 400

    json: Dict[str, Any] = request.json
    data = json["data"]
    event = Report(event=data, quiz=play.quiz, submission=play)

    play.quiz.events.append(event)
    play.events.append(event)
    db.session.add(event)
    db.session.commit()
    return jsonify(msg="OK")


@blueprint.route("/quiz/<quiz_id>/reports")
@admin_only
def quiz_reports(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify(err="Cannot find that Quiz ID."), 400

    events = quiz.events.order_by(Report.datetime.desc()).limit(20).all()
    output = []
    for e in events:
        base_obj = {}
        base_obj["id"] = e.id
        base_obj["event"] = e.event
        base_obj["name"] = e.submission.owner.name
        base_obj["datetime"] = e.datetime.isoformat(timespec="seconds") + "Z"
        output.append(base_obj)
    return jsonify(*output)


# -------------
def judge_score(play, questions):
    questions_len = len(questions)
    play.scores = [""] * questions_len

    for i in range(questions_len):
        if questions[i].is_essay:
            score = -1
        else:
            if play.options[i] == questions[i].answer:
                score = 1
            else:
                score = 0
        play.scores[i] = score
