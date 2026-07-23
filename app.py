import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db_session
from models.usuario import Usuario, Cenario, Transacao

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave-de-desenvolvimento-trocar-depois")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@login_manager.user_loader
def load_user(user_id):
    return db_session.query(Usuario).get(int(user_id))


def get_cenario_do_usuario_ou_404(cenario_id):
    """
    Busca um cenário pelo id, mas só devolve se ele pertencer ao usuário
    logado. Isso evita que uma pessoa acesse /cenarios/5 e veja os dados
    financeiros de outra pessoa só trocando o número na URL.
    """
    cenario = db_session.query(Cenario).get(cenario_id)
    if cenario is None or cenario.usuario_id != current_user.id:
        abort(404)
    return cenario


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

        novo_usuario = Usuario(nome=nome, email=email)
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
            return redirect(url_for("painel"))
        else:
            flash("Email ou senha incorretos.")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/painel")
@login_required
def painel():
    return render_template("painel.html")


@app.route("/cenarios")
@login_required
def cenarios():
    """Lista todos os cenários do usuário logado, com opção de criar um novo."""
    return render_template("cenarios.html", cenarios=current_user.cenarios)


@app.route("/cenarios/novo", methods=["GET", "POST"])
@login_required
def novo_cenario():
    if request.method == "POST":
        nome = request.form.get("nome") or f"Cenário {len(current_user.cenarios) + 1}"
        renda = float(request.form["renda_mensal"])

        novo = Cenario(nome=nome, renda_mensal=renda, usuario_id=current_user.id)
        db_session.add(novo)
        db_session.commit()

        return redirect(url_for("ver_cenario", cenario_id=novo.id))

    sugestao_nome = f"Cenário {len(current_user.cenarios) + 1}"
    return render_template("novo_cenario.html", sugestao_nome=sugestao_nome)


@app.route("/cenarios/<int:cenario_id>")
@login_required
def ver_cenario(cenario_id):
    cenario = get_cenario_do_usuario_ou_404(cenario_id)
    return render_template("cenario.html", cenario=cenario, usuario=current_user)


@app.route("/cenarios/<int:cenario_id>/adicionar_transacao", methods=["POST"])
@login_required
def adicionar_transacao(cenario_id):
    cenario = get_cenario_do_usuario_ou_404(cenario_id)

    descricao = request.form["descricao"]
    valor = float(request.form["valor"])
    categoria = request.form.get("categoria") or "Outros"

    nova_transacao = Transacao(
        descricao=descricao,
        valor=valor,
        categoria=categoria,
        cenario_id=cenario.id
    )
    db_session.add(nova_transacao)
    db_session.commit()

    return redirect(url_for("ver_cenario", cenario_id=cenario.id))


@app.route("/recomendacoes")
@login_required
def recomendacoes():
    """Lista os cenários para o usuário escolher qual ver as dicas detalhadas."""
    return render_template("recomendacoes.html", cenarios=current_user.cenarios)


@app.route("/recomendacoes/<int:cenario_id>")
@login_required
def ver_recomendacoes(cenario_id):
    cenario = get_cenario_do_usuario_ou_404(cenario_id)
    return render_template("recomendacoes_detalhe.html", cenario=cenario)


@app.route("/conta", methods=["GET", "POST"])
@login_required
def conta():
    if request.method == "POST":
        acao = request.form.get("acao")

        if acao == "atualizar_nome":
            novo_nome = request.form["nome"].strip()
            if novo_nome:
                current_user.nome = novo_nome
                db_session.commit()
                flash("Nome atualizado com sucesso.")
            return redirect(url_for("conta"))

        if acao == "trocar_senha":
            senha_atual = request.form["senha_atual"]
            nova_senha = request.form["nova_senha"]

            if not current_user.checar_senha(senha_atual):
                flash("Senha atual incorreta.")
            else:
                current_user.set_senha(nova_senha)
                db_session.commit()
                flash("Senha alterada com sucesso.")
            return redirect(url_for("conta"))

    return render_template("conta.html")


if __name__ == "__main__":
    app.run(debug=True)