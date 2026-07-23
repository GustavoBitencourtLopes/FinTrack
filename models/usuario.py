from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

Base = declarative_base()


class Usuario(Base, UserMixin):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha_hash = Column(String, nullable=False)

    # Um usuário agora tem vários cenários (simulações), não uma renda fixa.
    cenarios = relationship("Cenario", back_populates="usuario", order_by="Cenario.id")

    def set_senha(self, senha_texto_puro):
        self.senha_hash = generate_password_hash(senha_texto_puro)

    def checar_senha(self, senha_texto_puro):
        return check_password_hash(self.senha_hash, senha_texto_puro)

    def __repr__(self):
        return f"Usuario(nome={self.nome!r})"


class Cenario(Base):
    """
    Um Cenário representa uma simulação financeira: uma renda mensal
    específica, junto com os gastos associados a ela. Um mesmo usuário
    pode ter vários cenários (ex: "Cenário 1" com renda de R$3000,
    "Cenário 2" com renda de R$5000), cada um com seus próprios gastos.
    """
    __tablename__ = "cenarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False, default="Cenário")
    renda_mensal = Column(Float, nullable=False, default=0)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="cenarios")

    transacoes = relationship("Transacao", back_populates="cenario")

    def total_gastos(self):
        return sum(t.valor for t in self.transacoes)

    def percentual_gasto(self):
        if not self.renda_mensal:
            return 0
        return (self.total_gastos() / self.renda_mensal) * 100

    def situacao_financeira(self):
        percentual = self.percentual_gasto()
        if percentual <= 70:
            return "OK"
        elif percentual <= 90:
            return "Atenção"
        else:
            return "Alerta"

    def sobra_mensal(self):
        return (self.renda_mensal or 0) - self.total_gastos()

    def recomendacao_investimento(self):
        """
        Regras simplificadas, só para fins didáticos (não é assessoria
        financeira real).
        """
        situacao = self.situacao_financeira()
        sobra = self.sobra_mensal()

        if situacao == "Alerta":
            return (
                "Seus gastos estão consumindo quase toda (ou mais que) sua renda. "
                "Antes de pensar em investir, o foco deveria ser reduzir despesas "
                "e evitar dívidas."
            )

        if situacao == "Atenção":
            return (
                f"Você tem uma sobra de R${sobra:.2f} este mês. O ideal é priorizar "
                "uma reserva de emergência, em algo simples e de fácil acesso, como "
                "Tesouro Selic ou CDB com liquidez diária."
            )

        if sobra <= 0:
            return "Sua renda está totalmente comprometida. Reveja seus gastos antes de investir."
        elif sobra < 500:
            return (
                f"Você tem R${sobra:.2f} de sobra. Um bom começo é formar uma reserva "
                "de emergência em Tesouro Selic ou CDB de liquidez diária."
            )
        else:
            return (
                f"Você tem R${sobra:.2f} de sobra mensal, uma boa margem! Considere "
                "manter uma reserva de emergência e destinar o restante a investimentos "
                "de médio/longo prazo, de acordo com seu perfil de risco."
            )

    def __repr__(self):
        return f"Cenario(nome={self.nome!r}, renda={self.renda_mensal})"


class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True)
    descricao = Column(String, nullable=False)
    valor = Column(Float, nullable=False)
    categoria = Column(String, default="Outros")

    # Agora a transação pertence a um Cenário, não direto ao Usuário.
    cenario_id = Column(Integer, ForeignKey("cenarios.id"), nullable=False)
    cenario = relationship("Cenario", back_populates="transacoes")

    def __repr__(self):
        return f"Transacao({self.descricao!r}, R${self.valor}, {self.categoria!r})"