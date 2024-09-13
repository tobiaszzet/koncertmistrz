from wtforms import Form, validators, StringField, SubmitField, URLField, TextAreaField, PasswordField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length, Email, InputRequired
from wtforms.fields import DateField
from wtforms_components import TimeField, DateTimeField
from flask_wtf import FlaskForm


class EventCreatorForm(FlaskForm):
    event_name = StringField("Nazwa wydarzenia", render_kw={'class': 'form-control'},
                             validators=[validators.DataRequired(), validators.length(max=120)])
    event_date = DateField("Data", format="%Y-%m-%d", validators=[validators.DataRequired()],
                           render_kw={'class': 'col-md-3 mb-3'})
    event_time = TimeField("Godzina", format="%H:%M", validators=[validators.DataRequired()],
                           render_kw={'class': 'col-md-3 mb-3'})
    event_description = TextAreaField("Opis wydarzenia", render_kw={'class': 'form-control', 'rows': '8'})
    event_url = URLField("Link do wydarzenia", render_kw={'class': 'form-control'},
                         validators=[validators.DataRequired()])
    event_artist = StringField("Wykonawca", validators=[validators.DataRequired()])
    submit = SubmitField("Utwórz")


class ArtistCreatorForm(FlaskForm):
    artist_name = StringField("Nazwa artysty/zespołu", render_kw={'class': 'form-control'},
                              validators=[validators.DataRequired()])
    artist_description = TextAreaField("Opis", render_kw={'class': 'form-control', 'rows': '8'})
    submit = SubmitField("Utwórz")


class FestivalCreatorForm(FlaskForm):
    festival_name = StringField("Nazwa festiwalu", render_kw={'class': 'form-control'},
                                validators=[validators.DataRequired()])
    festival_description = TextAreaField("Opis", render_kw={'class': 'form-control', 'rows': '8'})
    festival_event = StringField("Koncerty wchodzące w skład festiwalu. Zawsze można dodać je później).",
                                 render_kw={'class': 'form-control', 'rows': '8'})
    festival_url = URLField("Link do wydarzenia", render_kw={'class': 'form-control'},
                            validators=[validators.DataRequired()])
    submit = SubmitField("Utwórz")


class SpotCreatorForm(FlaskForm):
    spot_name = StringField("Nazwa miejsca", render_kw={'class': 'form-control'},
                                validators=[validators.DataRequired()])
    spot_description = TextAreaField("Opis", render_kw={'class': 'form-control', 'rows': '8'})
    spot_url = URLField("Link do miejsca", render_kw={'class': 'form-control'},
                            validators=[validators.DataRequired()])
    submit = SubmitField("Utwórz")


class RegistrationForm(FlaskForm):
    user_login = StringField("nazwa użytkownika")
    user_email = StringField("email", validators=[DataRequired(), Email(message="oj nie wygląda to na maila")])
    user_password_hash = PasswordField("hasło",
                                       validators=[DataRequired(),
                                                   EqualTo('user_password_hash2',
                                                           message='hasełka nie wyglądają na takie same'),
                                                   Length(min=8, max=30, message="za krótko")])
    user_password_hash2 = PasswordField("Potwierdź hasło")
    submit = SubmitField("Utwórz konto")

    def validate_email(self, email, table_name):
        if table_name.query.filter_by(email=email.data).first():
            raise ValidationError("użytkownik o takim adresie email już istnieje")



