from datetime import datetime
from config import db, ma
from marshmallow import fields


class Person(db.Model):
    __tablename__ = "person"
    person_id = db.Column(db.Integer, primary_key=True)
    lname = db.Column(db.String(32))
    fname = db.Column(db.String(32))
    display_name = db.Column(db.String(64))
    email_id = db.Column(db.String(32))
    last_login = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    hunts = db.relationship(
        "HuntPerson",
        backref="huntperson",
        cascade="all, delete, delete-orphan",
        single_parent=True,
        order_by="desc(Hunt.start_time)",
    )


class Hunt(db.Model):
    __tablename__ = "hunt"
    hunt_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    title = db.Column(db.String(32))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    location = db.Column(db.Text)
    pass_code = db.Column(db.String,  default=lambda: str(db.uuid.uuid4()), unique=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.person_id'))
    timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    questions = db.relationship(
        "Question",
        backref="hunt",
        cascade="all, delete, delete-orphan",
        single_parent=True,
        order_by="desc(Question.order)",
    )


class Image(db.Model):
    __tablename__ = "image"
    image_id = db.Column(db.Integer, primary_key=True)
    hint = db.Column(db.Text)
    url = db.Column(db.Text)
    lat = db.Column(db.Float)
    long = db.Column(db.Float)


class Question(db.Model):
    __tablename__ = "question"
    question_id = db.Column(db.Integer, primary_key=True)
    hunt_id = db.Column(db.Integer, db.ForeignKey("hunt.hunt_id"))
    title = db.Column(db.String(128))
    description = db.Column(db.Text)
    max_score = db.Column(db.Integer, default=100)
    image_id = db.Column(db.Integer, db.ForeignKey('image.image_id'))
    order = db.Column(db.Integer)
    options = db.relationship(
        "Option",
        backref="question",
        cascade="all, delete, delete-orphan",
        single_parent=True,
    )


class Option(db.Model):
    __tablename__ = "option"
    option_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.question_id"))
    description = db.Column(db.String(64))
    is_correct = db.Column(db.Boolean, default=False)


class HuntPerson(db.Model):
    __tablename__ = "huntperson"
    hunt_id = db.Column(db.Integer, db.ForeignKey('hunt.hunt_id'))
    person_id = db.Column(db.Integer, db.ForeignKey('person.person_id'))
    score = db.Column(db.Integer, default=0)
    rank = db.Column(db.Integer, default=-1)
    start_time = db.Column(
        db.DateTime, default=datetime.utcnow
    )
    end_time = db.Column(
        db.DateTime, default=datetime.utcnow
    )
    attempt = db.Column(db.Text)

    __table_args__ = (
        db.PrimaryKeyConstraint(
            hunt_id,
            person_id),
        {})


class PersonSchema(ma.ModelSchema):
    def __init__(self, **kwargs):
        super().__init__(strict=True, **kwargs)

    class Meta:
        model = Person
        sqla_session = db.session

    hunts = fields.Nested("PersonHuntPersonSchema", default=[], many=True)


class OptionSchema(ma.ModelSchema):
    def __init__(self, **kwargs):
        super().__init__(strict=True, **kwargs)

    class Meta:
        model = Option
        sqla_session = db.session


class ImageSchema(ma.ModelSchema):
    def __init__(self, **kwargs):
        super().__init__(strict=True, **kwargs)

    class Meta:
        model = Image
        sqla_session = db.session


class HuntSchema(ma.ModelSchema):
    def __init__(self, **kwargs):
        super().__init__(strict=True, **kwargs)

    class Meta:
        model = Hunt
        sqla_session = db.session

    questions = fields.Nested("HuntQuestionSchema", default=[], many=True)


class QuestionSchema(ma.ModelSchema):
    def __init__(self, **kwargs):
        super().__init__(strict=True, **kwargs)

    class Meta:
        model = Question
        sqla_session = db.session

    options = fields.Nested("QuestionOptionSchema", default=[], many=True)
    image = fields.Nested("QuestionImageSchema", default=None)


class HuntQuestionSchema(ma.ModelSchema):
    """
    This class exists to get around a recursion issue
    """
    def __init__(self, **kwargs):
        super().__init__(strict=True, **kwargs)

    hunt_id = fields.Int()
    question_id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    location = fields.Str()
    pass_code = fields.Str()
    timestamp = fields.DateTime()


class PersonHuntPersonSchema(ma.ModelSchema):
    def __init__(self, **kwargs):
        super().__init__(strict=True, **kwargs)

    person_id = fields.Int()
    hunt_id = fields.Int()
    score = fields.Int()
    rank = fields.Int()
    start_time = fields.DateTime


class QuestionOptionSchema(ma.ModelSchema):
    """
    This class exists to get around a recursion issue
    """
    def __init__(self, **kwargs):
        super().__init__(strict=True, **kwargs)

    option_id = fields.Int()
    question_id = fields.Int()
    description = fields.Str()
    is_correct = fields.Bool()


class QuestionImageSchema(ma.ModelSchema):
    """
        This class exists to get around a recursion issue
        """

    def __init__(self, **kwargs):
        super().__init__(strict=True, **kwargs)

    image_id = fields.Int()
    hint = fields.Str()
    url = fields.Str()
    lat = fields.Float()
    long = fields.Float()


class HuntPersonSchema(ma.ModelSchema):
    def __init__(self, **kwargs):
        super().__init__(strict=True, **kwargs)

    class Meta:
        model = HuntPerson
        sqla_session = db.session
