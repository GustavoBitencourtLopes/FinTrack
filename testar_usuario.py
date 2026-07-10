from models.usuario import Usuario, Transacao

joao = Usuario(nome="João", email="joao@email.com", renda_mensal=3000)

joao.adicionar_transacao(Transacao("Aluguel", 1200, categoria="Moradia"))
joao.adicionar_transacao(Transacao("Mercado", 600, categoria="Alimentação"))
joao.adicionar_transacao(Transacao("Lazer", 500, categoria="Lazer"))

print(joao)
print("Transações:", joao.transacoes)
print("Total gasto:", joao.total_gastos())
print(f"Percentual gasto: {joao.percentual_gasto():.1f}%")
print("Situação:", joao.situacao_financeira())