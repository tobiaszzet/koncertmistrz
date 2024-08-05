from flask import Flask, render_template, request, flash, session, url_for
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import Form, validators, StringField, SubmitField, URLField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.fields import DateField
from wtforms_components import TimeField, DateTimeField


with open('db_password.txt', 'r') as file:
    password = file.read()

app = Flask(__name__, static_url_path='/static/css')
app.config['SECRET_KEY'] = "3546wW#B$$%"
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{password}@localhost/koncertmistrz_db'
db = SQLAlchemy(app)


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    description = db.Column(db.String(800), nullable=True)
    url = db.Column(db.String(120), nullable=False)
    festival_id = db.Column(db.Integer, nullable=True)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    last_update_user_name = db.Column(db.Integer, nullable=False)


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String(1800), nullable=True)
    last_update = db.Column(db.DateTime, default=datetime.utcnow())
    # last_update_user_name = db.Column(db.Integer, nullable=False)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    login = db.Column(db.String(30), nullable=True, unique=True)
    password = db.Column(db.String(120), nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow())


class Spot(db.Model):
    __tablename__ = 'spots'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    address = db.Column(db.String(200), nullable=True)
    description = db.Column(db.String(800), nullable=True)
    url_address = db.Column(db.String(200), nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow())
    # last_update_user_name = db.Column(db.Integer, nullable=False)


class Festival(db.Model):
    __tablename__ = 'festivals'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String(800), nullable=True)
    url_address = db.Column(db.String(200), nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow())
    # address = db.Column(db.String(200), nullable=True)
    # last_update_user_name = db.Column(db.Integer, nullable=False)


class UserEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))


class ArtistEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))


class UserArtist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))


class SpotEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('spots.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))


class SpotFestival(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('spots.id'))
    festivals_id = db.Column(db.Integer, db.ForeignKey('festivals.id'))


class EventCreatorFrom(FlaskForm):
    event_name = StringField("Nazwa wydarzenia", render_kw={'class': 'form-control'},
                             validators=[validators.DataRequired()])
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



with app.app_context():
    db.create_all()
    db.session.commit()


class MainView(MethodView):
    @app.route("/", methods=["GET"])
    def main_view():
        if request.method == "GET":
            return render_template("home_page.html")

    @app.route("/creator_page_event/", methods=["GET", "POST"])
    def create_event():
        form = EventCreatorFrom()
        if request.method == "GET":
            return render_template("creator_page_event.html", form=form)
        else:
            username_id = "1"
            event = Event(name=form.event_name.data, date=form.event_date.data, time=form.event_time.data,
                          description=form.event_description.data, url=form.event_url.data,
                          last_update_user_name=username_id)
            # db.session.add(event)
            # db.session.commit()

            # form.event_date.data = ""
            # form.event_name.data = ""
            # form.event_time.data = ""
            # form.event_description.data = ""
            # form.event_url.data = ""
            flash("Utworzyłeś nowe wydarzenie.")
            return render_template("creator_page_event.html", form=form)

    @app.route("/creator_page_artist/", methods=["GET", "POST"])
    def create_artist():
        form = ArtistCreatorForm()
        if request.method == "GET":
            return render_template("creator_page_artist.html", form=form)
        else:
            artist = Artist(name=form.artist_name.data, description=form.artist_description.data)
            # db.session.add(artist)
            # db.session.commit()

            form.artist_name.data = ""
            form.artist_description.data = ""
            flash("Utworzyłeś profil artysty.")
            return render_template("creator_page_artist.html", form=form)

    @app.route("/creator_page_festival/", methods=["GET", "POST"])
    def create_festival():
        form = FestivalCreatorForm()
        if request.method == "GET":
            return render_template("creator_page_festival.html", form=form)
        else:
            festival = Festival(name=form.festival_name.data, description=form.festival_description.data,
                                url_address= form.festival_url.data)
            # db.session.add(festival)
            # db.session.commit()

            flash("Utworzyłeś profil festiwalu")
            return (render_template("creator_page_festival.html", form=form))

    @app.route("/creator_page_spot/", methods=["GET", "POST"])
    def create_spot():
        form = SpotCreatorForm()
        if request.method == "GET":
            return render_template("creator_page_spot.html", form=form)
        else:
            spot = Spot(name=form.spot_name.data, description=form.spot_description.data,
                        url_address=form.spot_url.data)
            # db.session.add(spot)
            # db.session.commit()

            flash("Utworzyłeś profil festiwalu")
            return render_template("creator_page_spot.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
