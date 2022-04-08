from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from wtforms.fields import EmailField


class DepartmentsForm(FlaskForm):
    chief = IntegerField("Chief id", validators=[DataRequired()])
    title = StringField("Title of department", validators=[DataRequired()])
    members = StringField("Members list", validators=[DataRequired()])
    email = EmailField("Email of department", validators=[DataRequired()])
    submit = SubmitField("Submit")