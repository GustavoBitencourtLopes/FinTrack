from database import SessionLocal
from models.usuario import Usuario, Transacao

session = SessionLocal()

joao = session.query(Usuario).filter_by(email="joao@email.com").first()

if joao is None:
    joao = Usuario(nome="João", email="joao@email.com", renda_mensal=3000)
    session.add(joao)
    session.commit()

    t1 = Transacao(descricao="Aluguel", valor=1200, categoria="Moradia", usuario_id=joao.id)
    t2 = Transacao(descricao="Mercado", valor=600, categoria="Alimentação", usuario_id=joao.id)
    session.add_all([t1, t2])
    session.commit()
    print("Usuário e transações criados no banco pela primeira vez.")
else:
    print("Usuário já existia no banco, só fui buscar os dados.")

usuario_do_banco = session.query(Usuario).filter_by(email="joao@email.com").first()

print(usuario_do_banco)
print("Transações:", usuario_do_banco.transacoes)
print("Total gasto:", usuario_do_banco.total_gastos())
print("Situação:", usuario_do_banco.situacao_financeira())

session.close()