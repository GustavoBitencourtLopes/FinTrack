import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db_session
from models.usuario import Usuario, Transacao

app = Flask(__name__)
# Em produção, a chave vem de uma variável de ambiente (mais seguro).
# Em desenvolvimento local, usa uma chave padrão só para não quebrar.
app.secret_key = os.environ.get("SECRET_KEY", "chave-de-desenvolvimento-trocar-depois")  # necessário para sessões e flash messages

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@app.teardown_appcontext
def shutdown_session(exception=None):
    """Fecha a sessão do banco automaticamente ao final de cada requisição."""
    db_session.remove()


@login_manager.user_loader
def load_user(user_id):
    return db_session.query(Usuario).get(int(user_id))


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        existe = db_session.query(Usuario).filter_by(email=email).first()
        if existe:
            flash("Já existe um usuário com esse email.")
            return redirect(url_for("cadastro"))

        novo_usuario = Usuario(nome=nome, email=email, renda_mensal=None)
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
            if usuario.precisa_definir_renda():
                return redirect(url_for("definir_renda"))
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


@app.route("/definir_renda", methods=["GET", "POST"])
@login_required
def definir_renda():
    if request.method == "POST":
        renda = float(request.form["renda_mensal"])
        current_user.renda_mensal = renda
        db_session.commit()
        return redirect(url_for("dashboard"))

    return render_template("definir_renda.html")


@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.precisa_definir_renda():
        return redirect(url_for("definir_renda"))
    return render_template("usuario.html", usuario=current_user)


@app.route("/adicionar_transacao", methods=["POST"])
@login_required
def adicionar_transacao():
    descricao = request.form["descricao"]
    valor = float(request.form["valor"])
    categoria = request.form.get("categoria") or "Outros"

    nova_transacao = Transacao(
        descricao=descricao,
        valor=valor,
        categoria=categoria,
        usuario_id=current_user.id
    )
    db_session.add(nova_transacao)
    db_session.commit()

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)