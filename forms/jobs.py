from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField, BooleanField
from wtforms.validators import DataRequired


class JobsForm(FlaskForm):
    team_leader = IntegerField("Team Leader id", validators=[DataRequired()])
    job = StringField("Job Title", validators=[DataRequired()])
    work_size = IntegerField("Work Size", validators=[DataRequired()])
    collaborators = StringField("Collaborators", validators=[DataRequired()])
    is_finished = BooleanField("Is job finished?")
    submit = SubmitField("Submit")