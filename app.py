from flask import Flask, render_template, request, flash, session, url_for, redirect
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from Forms import EventCreatorForm, ArtistCreatorForm, FestivalCreatorForm, SpotCreatorForm, RegistrationForm


with open('db_password.txt', 'r') as file:
    password_file = file.read()

app = Flask(__name__, static_url_path='/static/css')
app.config['SECRET_KEY'] = "3546wW#B$$%"
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{password_file}@localhost/koncertmistrz_db'
db = SQLAlchemy(app)
# migrate = Migrate(app, db)


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
    last_update_user_name = db.Column(db.Integer, nullable=False)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    login = db.Column(db.String(30), nullable=True, unique=True)
    password_hash = db.Column(db.String(500), nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow())

    @property
    def password(self):
        raise AttributeError('coś tam nie tak z tym hasełkiem')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Spot(db.Model):
    __tablename__ = 'spots'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    address = db.Column(db.String(200), nullable=True)
    description = db.Column(db.String(800), nullable=True)
    url_address = db.Column(db.String(200), nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow())
    last_update_user_name = db.Column(db.Integer, nullable=False)


class Festival(db.Model):
    __tablename__ = 'festivals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String(800), nullable=True)
    url_address = db.Column(db.String(200), nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow())
    address = db.Column(db.String(200), nullable=True)
    last_update_user_name = db.Column(db.Integer, nullable=False)


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


with app.app_context():
    db.create_all()
    db.session.commit()


class MainView(MethodView):
    @app.route("/", methods=["GET"])
    def main_view():
        if request.method == "GET":
            return render_template("home_page.html")

    @app.route("/user_site/", methods=["GET", "POST"])
    def user_site():
        if request.method == "GET":
            return render_template("user_site.html")
        else:
            pass

    @app.route("/user_settings_site/", methods=["GET", "POST"])
    def user_settings_site():
        if request.method == "GET":
            return render_template("user_settings_site.html")
        else:
            pass

    @app.route("/login_site/", methods=["GET", "POST"])
    def user_login_site():
        form = UserForm()
        if request.method == "GET":
            return render_template("login_site.html")
        else:

            user_data = db.session.query(User).filter(User.email == form.user_email.data).first()
            if user_data.password_hash == form.user_password_hash:
                pass

            return render_template("login_site.html", form=form)

    @app.route("/registration_site/", methods=["GET", "POST"])
    def user_registration_site():
        form = RegistrationForm()
        if request.method == "GET":
            return render_template("registration_site.html", form=form)
        elif form.validate_on_submit():
            user_by_email = db.session.query(User).filter(User.email == form.user_email.data).first()
            user_by_login = db.session.query(User).filter(User.login == form.user_login.data).first()
            if user_by_email is None and (user_by_login is None or user_by_login.login == ""):
                hashed_pw = generate_password_hash(form.user_password_hash.data)
                user = User(login=form.user_login.data, email=form.user_email.data,
                            password_hash=hashed_pw)

                # db.session.add(user)
                # db.session.commit()
                flash("Konto utworzono pomyślnie")
                return redirect(url_for("user_site"))
            else:
                if user_by_login.login != "":
                    flash("taki login jest już użyty")
                elif user_by_email:
                    flash("konto pod takim emailem już istnieje")

        return render_template("registration_site.html", form=form)





    @app.route("/creator_page_event/", methods=["GET", "POST"])
    def create_event():
        form = EventCreatorForm()
        if request.method == "GET":
            return render_template("creator_page_event.html", form=form)
        else:
            username_id = "1"
            event = Event(name=form.event_name.data, date=form.event_date.data, time=form.event_time.data,
                          description=form.event_description.data, url=form.event_url.data,
                          last_update_user_name=username_id)
            # db.session.add(event)
            # db.session.commit()

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
            return render_template("creator_page_festival.html", form=form)

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