from flask import Flask, render_template
from database import SessionLocal
from models.usuario import Usuario

app = Flask(__name__)


@app.route("/")
def home():
    return "<h1>Bem-vindo ao FinTrack!</h1><p>Acesse /usuario para ver os dados.</p>"


@app.route("/usuario")
def ver_usuario():
    session = SessionLocal()
    usuario = session.query(Usuario).filter_by(email="joao@email.com").first()
    session.close()
    return render_template("usuario.html", usuario=usuario)


if __name__ == "__main__":
    app.run(debug=True)