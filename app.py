from flask import Flask, render_template, request, flash, session, url_for, redirect, current_app, abort
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from Forms import (EventCreatorForm, ArtistCreatorForm, FestivalCreatorForm, SpotCreatorForm,
                   RegistrationForm, SignInForm, EventBrowser)
from flask_login import UserMixin, LoginManager, login_required, logout_user, current_user, login_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import mailtrap as mt

with open('db_password.txt', 'r') as file:
    password_file = file.read()
with open('pw_config.txt', 'r') as file:
    pw_config = file.read()
with open('mailtrap_token.txt', 'r') as file:
    token = file.read()


def mail_verification(to, link):
    mail_form = mt.Mail(
        sender=mt.Address(email="mailtrap@demomailtrap.com", name="Mailtrap Test"),
        to=[mt.Address(email=to)],
        subject="weryfikacja konta",
        text= f"kliknij w ten link aby aktywować konto {link}",
        category="Verification email",
    )
    client = mt.MailtrapClient(token=f"{token}")
    response = client.send(mail_form)
    print(response)


app = Flask(__name__, static_url_path='/static/css')
app.config['SECRET_KEY'] = f"{pw_config}"
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{password_file}@localhost/koncertmistrz_db'
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)
mail = Mail(app)
s = URLSafeTimedSerializer(f'{password_file}')
# migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = u"Musisz być zalogowany, aby wejść na tę stronę."
login_manager.login_view = "user_login_site"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    description = db.Column(db.String(800), nullable=True)
    url_address = db.Column(db.String(120), nullable=False)
    festival_id = db.Column(db.Integer, nullable=True)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    last_update_username = db.Column(db.Integer)
    created_by = db.Column(db.Integer)


class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String(1800), nullable=True)
    last_update = db.Column(db.DateTime, default=datetime.utcnow())
    last_update_username = db.Column(db.Integer)
    created_by = db.Column(db.Integer)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    login = db.Column(db.String(30), nullable=True)
    password_hash = db.Column(db.String(500), nullable=False)
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    is_admin = db.Column(db.Boolean,  nullable=False, default=False)
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
    last_update_username = db.Column(db.Integer)
    created_by = db.Column(db.Integer)


class Festival(db.Model):
    __tablename__ = 'festivals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String(800), nullable=True)
    url_address = db.Column(db.String(200), nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow())
    last_update_username = db.Column(db.Integer)
    created_by = db.Column(db.Integer)


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


class UserFestival(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    festival_id = db.Column(db.Integer, db.ForeignKey('festivals.id'))


class UserSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    spot_id = db.Column(db.Integer, db.ForeignKey('spots.id'))


class EventFestival(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    festival_id = db.Column(db.Integer, db.ForeignKey('festivals.id'))


class ArtistFestival(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    festival_id = db.Column(db.Integer, db.ForeignKey('festivals.id'))


with app.app_context():
    #db.session.query(User).filter(User.email == "t.zajusz@gmail.com").delete()
    db.create_all()
    db.session.commit()


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.route("/", methods=["GET"])
def main_view():
    if request.method == "GET":
        return render_template("home_page.html")


@app.route("/user_site/", methods=["GET", "POST"])
@login_required
def user_site():
    if request.method == "GET":
        return render_template("user_site.html")
    else:
        pass


@app.route("/event_browser/", methods=["GET", "POST"])
@login_required
def event_browser():
    form = EventBrowser()
    if request.method == "GET":
        return render_template("event_browser.html", form=form)
    else:


        pass


@app.route("/user_settings_site/", methods=["GET", "POST"])
@login_required
def user_settings_site():
    if request.method == "GET":
        return render_template("user_settings_site.html")
    else:
        pass


@app.route("/login_site/", methods=["GET", "POST"])
def user_login_site():
    form = SignInForm()
    if request.method == "GET":
        return render_template("login_site.html", form=form)
    elif request.method == "POST":
        email = form.user_email.data
        password = form.user_password.data
        user = User.query.filter_by(email=email).first()
        try:
            passed = check_password_hash(user.password_hash, password)
        except AttributeError:
            return render_template("login_site.html", form=form)
        if passed and user.is_confirmed:
            session["logged_in"] = True
            if user.login == "":
                session["username"] = user.email
            else:
                session["username"] = user.login
            login_user(user)
            return redirect(url_for("user_site"))
        elif not passed:
            flash("złe hasło. Wpisz dobre")
        elif not user.is_confirmed:
            flash("Konto nie jest jeszcze aktywowane.")
        else:
            flash("Wystąpił problem. Proszę postępować tak, aby problem nie występował.")
    return render_template("login_site.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    session['logged_in'] = False
    session.clear()
    flash("Zostałeś pomyślnie wylogowany")
    return redirect(url_for("user_login_site"))


@app.route("/registration_site/", methods=["GET", "POST"])
def user_registration_site():
    form = RegistrationForm()
    if request.method == "GET":
        return render_template("registration_site.html", form=form)
    elif form.validate_on_submit():
        user_by_email = db.session.query(User).filter(User.email == form.user_email.data).first()
        user_by_login = db.session.query(User).filter(User.login == form.user_login.data).first()
        if user_by_email is None and (user_by_login is None or user_by_login.login == ""):
            email = form.user_email.data
            print(session)
            token = s.dumps(email, salt='email-confirm')
            link = url_for('confirm_email', token=token, _external=True)
            # mail_verification(email, link)
            hashed_pw = generate_password_hash(form.user_password_hash.data)
            user = User(login=form.user_login.data,
                        email=form.user_email.data,
                        password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
            flash(f"Konto utworzono pomyślnie. Wysłaliśmy link aktywacyjny na {email}")
            return redirect(url_for("user_login_site"))
        else:
            if user_by_login.login != "":
                flash("taki login jest już użyty")
            elif user_by_email:
                flash("konto pod takim emailem już istnieje")
    return render_template("registration_site.html", form=form)


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
        print(email)
        user = db.session.query(User).filter(User.email == email).first()
        user.is_confirmed = True
        db.session.add(user)
        db.session.commit()
    except SignatureExpired:
        return '<h3> token wygasł, spróbuj zarejestrować się jeszcze raz</h3>'
    return '<h3> stworzyłeś konto </h3>'


@app.route("/creator_page_event/", methods=["GET", "POST"])
@login_required
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
@login_required
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
@login_required
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
@login_required
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
