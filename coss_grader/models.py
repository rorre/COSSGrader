import enum
from datetime import datetime

from coss_grader.plugins import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash


class ClassEnum(enum.IntEnum):
    No_Class = 99
    # I hate myself for this.
    X_MIA_1 = 0
    X_MIA_2 = 1
    X_MIA_3 = 2
    X_MIA_4 = 3
    X_MIA_5 = 4
    X_MIA_6 = 5
    X_MIA_7 = 6
    X_IIS_1 = 7
    X_IIS_2 = 8
    X_IIS_3 = 9
    X_IIS_4 = 10

    XI_MIA_1 = 11
    XI_MIA_2 = 12
    XI_MIA_3 = 13
    XI_MIA_4 = 14
    XI_MIA_5 = 15
    XI_MIA_6 = 16
    XI_IIS_1 = 17
    XI_IIS_2 = 18
    XI_IIS_3 = 19
    XI_IIS_4 = 20

    XII_MIA_1 = 21
    XII_MIA_2 = 22
    XII_MIA_3 = 23
    XII_MIA_4 = 24
    XII_MIA_5 = 25
    XII_MIA_6 = 26
    XII_MIA_7 = 27
    XII_IIS_1 = 28
    XII_IIS_2 = 29
    XII_IIS_3 = 30
    XII_IIS_4 = 31
    XII_IIS_5 = 32


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    event = db.Column(db.String)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"))
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"))


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    options = db.Column(db.ARRAY(db.String))
    scores = db.Column(db.ARRAY(db.Integer))
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    is_done = db.Column(db.Boolean, default=False)

    events = db.relationship(
        "Report",
        backref="submission",
        lazy="dynamic",
        primaryjoin="Report.submission_id == Submission.id",
    )


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    is_essay = db.Column(db.Boolean, nullable=False)
    options = db.Column(db.ARRAY(db.String))
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"))


class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    info = db.Column(db.Text, nullable=False)
    submissions = db.relationship(
        "Submission",
        backref="quiz",
        lazy="dynamic",
        primaryjoin="Submission.quiz_id == Quiz.id",
    )
    questions = db.relationship(
        "Question",
        backref="quiz",
        lazy="dynamic",
        primaryjoin="Question.quiz_id == Quiz.id",
    )
    events = db.relationship(
        "Report",
        backref="quiz",
        lazy="dynamic",
        primaryjoin="Report.quiz_id == Quiz.id",
    )
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    open_time = db.Column(db.DateTime)
    close_time = db.Column(db.DateTime)

    show_results = db.Column(db.Boolean, default=False)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True, nullable=False, unique=True)
    password_hash = db.Column(db.String)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    name = db.Column(db.Text)
    quizzes = db.relationship(
        "Quiz", backref="owner", lazy="dynamic", primaryjoin="Quiz.owner_id == User.id"
    )
    submissions = db.relationship(
        "Submission",
        backref="owner",
        lazy="dynamic",
        primaryjoin="Submission.owner_id == User.id",
    )
    classroom_ = db.Column("classroom", db.Integer, nullable=False, default=99)

    @staticmethod
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    is_active = True
    is_authenticated = True
    is_anonymous = False
    is_admin = db.Column(db.Boolean, default=False)

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def classroom(self):
        return ClassEnum(self.classroom_)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, unique=True)
    color = db.Column(db.String, index=True)
    users = db.relationship(
        "User", backref="role", lazy="dynamic", primaryjoin="User.role_id == Role.id"
    )
