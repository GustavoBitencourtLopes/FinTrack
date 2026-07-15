from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db_session
from models.usuario import Usuario, Transacao

app = Flask(__name__)
app.secret_key = "troque-essa-chave-depois"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@login_manager.user_loader
def load_user(user_id):
    return db_session.query(Usuario).get(int(user_id))


@app.route("/")
def home():
    return "<h1>Bem-vindo ao FinTrack!</h1><p><a href='/cadastro'>Cadastrar</a> | <a href='/login'>Login</a></p>"


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]
        renda = float(request.form["renda_mensal"])

        existe = db_session.query(Usuario).filter_by(email=email).first()
        if existe:
            flash("Já existe um usuário com esse email.")
            return redirect(url_for("cadastro"))

        novo_usuario = Usuario(nome=nome, email=email, renda_mensal=renda)
        novo_usuario.set_senha(senha)
        db_session.add(novo_usuario)
        db_session.commit()

        flash("Cadastro feito com sucesso! Faça login.")
        return redirect(url_for("login"))

    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        usuario = db_session.query(Usuario).filter_by(email=email).first()

        if usuario and usuario.checar_senha(senha):
            login_user(usuario)
            return redirect(url_for("dashboard"))
        else:
            flash("Email ou senha incorretos.")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("usuario.html", usuario=current_user)


if __name__ == "__main__":
    app.run(debug=True)