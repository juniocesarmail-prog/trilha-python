def depositar(saldo, extrato, valor):
    """
    Realiza a operação de depósito.
    Recebe saldo e extrato e retorna os novos valores.
    """
    if valor > 0:
        saldo += valor
        extrato += f"Depósito: R$ {valor:.2f}\n"
        print("Depósito realizado com sucesso!")
    else:
        print("Operação falhou! O valor informado é inválido.")
    
    # Retorna o saldo e extrato atualizados
    return saldo, extrato

def sacar(saldo, extrato, numero_saques, valor, limite, limite_saques):
    """
    Realiza a operação de saque, verificando limites.
    Recebe todos os dados e retorna os novos valores.
    """
    excedeu_saldo = valor > saldo
    excedeu_limite = valor > limite
    excedeu_saques = numero_saques >= limite_saques
    
    if excedeu_saldo:
        print("Operação falhou! Você não tem saldo suficiente.")
    elif excedeu_limite:
        print(f"Operação falhou! O valor do saque excede o limite de R$ {limite:.2f}.")
    elif excedeu_saques:
        print(f"Operação falhou! Número máximo de {limite_saques} saques excedido.")
    elif valor > 0:
        saldo -= valor
        extrato += f"Saque: R$ {valor:.2f}\n"
        numero_saques += 1
        print("Saque realizado com sucesso!")
    else:
        print("Operação falhou! O valor informado é inválido.")
        
    # Retorna o saldo, extrato e número de saques atualizados
    return saldo, extrato, numero_saques

def exibir_extrato(saldo, extrato):
    """
    Exibe o extrato e o saldo atual.
    """
    print("\n================ EXTRATO ================")
    print("Não foram realizadas movimentações." if not extrato else extrato)
    print(f"\nSaldo Atual: R$ {saldo:.2f}")
    print("==========================================")
    
# --- Configurações Iniciais ---
menu = """

[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair

=> """

saldo = 0
limite = 500
extrato = ""
numero_saques = 0
LIMITE_SAQUES = 3

# --- Loop Principal ---
while True:
    opcao = input(menu).lower() # Usar .lower() para ser mais robusto

    if opcao == "d":
        valor = float(input("Informe o valor do depósito: "))
        # Atualiza as variáveis globais com o retorno da função
        saldo, extrato = depositar(saldo, extrato, valor)
        
    elif opcao == "s":
        valor = float(input("Informe o valor do saque: "))
        # Atualiza as variáveis globais com o retorno da função
        saldo, extrato, numero_saques = sacar(
            saldo=saldo,
            extrato=extrato,
            numero_saques=numero_saques,
            valor=valor,
            limite=limite,
            limite_saques=LIMITE_SAQUES
        )
        
    elif opcao == "e":
        exibir_extrato(saldo, extrato)
        
    elif opcao == "q":
        print("Obrigado por usar nosso sistema bancário. Até logo!")
        break
        
    else:
        print("Operação inválida, por favor selecione novamente a operação desejada.")