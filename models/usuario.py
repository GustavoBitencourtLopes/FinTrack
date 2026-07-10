from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    renda_mensal = Column(Float, default=0)

    transacoes = relationship("Transacao", back_populates="usuario")

    def total_gastos(self):
        return sum(t.valor for t in self.transacoes)

    def percentual_gasto(self):
        if self.renda_mensal == 0:
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

    def __repr__(self):
        return f"Usuario(nome={self.nome!r}, renda={self.renda_mensal})"


class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True)
    descricao = Column(String, nullable=False)
    valor = Column(Float, nullable=False)
    categoria = Column(String, default="Outros")
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario", back_populates="transacoes")

    def __repr__(self):
        return f"Transacao({self.descricao!r}, R${self.valor}, {self.categoria!r})"