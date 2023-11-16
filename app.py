from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo
from models import db, User, Feedback
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from forms import FeedbackForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abacaxisalgado' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

with app.app_context():
    db.create_all()

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Você já está logado.', 'info')
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data, password=form.password.data).first()
        
        if existing_user:
            login_user(existing_user)
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Cadastro inválido, senha ou usuário incorreto.', 'danger')
    # Se o formulário não for validado com sucesso ou se o usuário não existir
    return render_template("login.html", form=form)

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    form = RegistrationForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Nome de usuário já em uso. Escolha outro.', 'danger')
        else:
            new_user = User(username=form.username.data, password=form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça o login.', 'success')
            return redirect(url_for('login'))

    return render_template("cadastro.html", form=form)

@app.route("/feedback", methods=['GET', 'POST'])
@login_required
def feedback():
    form = FeedbackForm()  # Instanciando o FeedbackForm

    if form.validate_on_submit():
        titulo = form.titulo.data
        anotacao = form.anotacao.data

        new_feedback = Feedback(titulo=titulo, anotacao=anotacao, user_id=current_user.id)
        db.session.add(new_feedback)
        db.session.commit()
        flash('Feedback postado com sucesso!', 'success')
        return redirect(url_for('feed'))

    return render_template("feedback.html", form=form)

@app.route("/feed")
def feed():
    feedbacks = Feedback.query.all()
    return render_template("feed.html", feedbacks=feedbacks)

@app.route("/logout")
def logout():
    logout_user()
    flash('Logout bem-sucedido.', 'info')
    return redirect(url_for('index'))

@app.route("/editar/<int:feedback_id>", methods=['GET', 'POST'])
@login_required
def editar(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)

    # Verifique se o usuário logado é o autor do feedback
    if current_user.id != feedback.user_id:
        flash("Você não tem permissão para editar este feedback.", "danger")
        return redirect(url_for("feed"))

    if request.method == "POST":
        # Lógica para editar o feedback (atualizar título e anotação, por exemplo)
        feedback.titulo = request.form.get("novo_titulo")
        feedback.anotacao = request.form.get("nova_anotacao")
        db.session.commit()
        flash("Feedback editado com sucesso!", "success")
        return redirect(url_for("feed"))

    return render_template("editar.html", feedback=feedback)


@app.route("/excluir/<int:feedback_id>", methods=['GET', 'POST'])
@login_required
def excluir(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)

    # Verifique se o usuário logado é o autor do feedback
    if current_user.id != feedback.user_id:
        flash("Você não tem permissão para excluir este feedback.", "danger")
        return redirect(url_for("feed"))

    db.session.delete(feedback)
    db.session.commit()
    flash("Feedback excluído com sucesso!", "success")
    return redirect(url_for("feed"))

if __name__ == '__main__':
    app.run(debug=True)
