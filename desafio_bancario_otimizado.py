import textwrap
from abc import ABC, abstractmethod, abstractproperty
from datetime import datetime, date
from typing import List, Optional
from functools import wraps

class Historico:
    """Armazena o histórico de transações da conta."""
    def __init__(self):
        self._transacoes: List[dict] = []

    @property
    def transacoes(self) -> List[dict]:
        return self._transacoes

    def adicionar_transacao(self, transacao):
        """Adiciona uma transação ao histórico."""
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

    def gerar_relatorio(self, tipo_transacao: Optional[str] = None):
        """Gera um relatório (lazy) das transações usando um gerador."""
        for transacao in self._transacoes:
            if (
                tipo_transacao is None
                or transacao["tipo"].lower() == tipo_transacao.lower()
            ):
                yield transacao

    def transacoes_do_dia(self) -> List[dict]:
        """Retorna todas as transações realizadas no dia de hoje."""
        data_atual = datetime.now().date()
        transacoes_do_dia = []
        for transacao in self._transacoes:
            try:
                data_transacao = datetime.strptime(
                    transacao["data"], "%d-%m-%Y %H:%M:%S"
                ).date()
                if data_atual == data_transacao:
                    transacoes_do_dia.append(transacao)
            except ValueError:
                continue
        return transacoes_do_dia


class Transacao(ABC):
    """Classe base abstrata para todas as transações."""
    
    @property
    @abstractproperty
    def valor(self):
        """Retorna o valor da transação."""
        raise NotImplementedError

    @abstractmethod
    def registrar(self, conta):
        """Registra a transação na conta."""
        raise NotImplementedError

class Saque(Transacao):
    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta) -> bool:
        """Tenta sacar o valor e registra no histórico se for bem-sucedido."""
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
        
        return sucesso_transacao

class Deposito(Transacao):
    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta) -> bool:
        """Tenta depositar o valor e registra no histórico se for bem-sucedido."""
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
        
        return sucesso_transacao

class Conta:
    """Classe base para contas bancárias."""
    AGENCIA = "0001"

    def __init__(self, numero: int, cliente):
        self._saldo: float = 0.0
        self._numero: int = numero
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero: int):
        """Método de fábrica (factory method) para criar uma nova conta."""
        return cls(numero, cliente)

    @property
    def saldo(self) -> float:
        return self._saldo

    @property
    def numero(self) -> int:
        return self._numero

    @property
    def agencia(self) -> str:
        return self.AGENCIA

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self) -> Historico:
        return self._historico

    def sacar(self, valor: float) -> bool:
        """Realiza um saque na conta."""
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        if valor > self._saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
            return False

        self._saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def depositar(self, valor: float) -> bool:
        """Realiza um depósito na conta."""
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True

class ContaCorrente(Conta):
    """Conta corrente com limites de saque e valor."""
    def __init__(self, numero: int, cliente, limite: float = 500.0, limite_saques: int = 3):
        super().__init__(numero, cliente)
        self._limite: float = limite
        self._limite_saques: int = limite_saques

    @classmethod
    def nova_conta(cls, cliente, numero: int, limite: float, limite_saques: int):
        """Cria uma nova ContaCorrente com limites específicos."""
        return cls(numero, cliente, limite, limite_saques)

    def sacar(self, valor: float) -> bool:
        """Sobrescreve o sacar para aplicar limites da Conta Corrente."""
        
        saques_do_dia = [
            t for t in self.historico.transacoes_do_dia() if t["tipo"] == Saque.__name__
        ]
        numero_saques = len(saques_do_dia)

        if valor > self._limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
            return False

        if numero_saques >= self._limite_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
            return False

        return super().sacar(valor)

    def __str__(self):
        """Representação de string da Conta Corrente."""
        return textwrap.dedent(f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
            Limite:\t\tR$ {self._limite:.2f}
        """)

class Cliente:
    """Classe base para clientes do banco."""
    def __init__(self, endereco: str):
        self.endereco: str = endereco
        self.contas: List[Conta] = []

    def realizar_transacao(self, conta, transacao: Transacao) -> bool:
        """Realiza uma transação, verificando limites diários."""
        if len(conta.historico.transacoes_do_dia()) >= 2:
            print("\n@@@ Você excedeu o número de transações permitidas para hoje! @@@")
            return False

        return transacao.registrar(conta)

    def adicionar_conta(self, conta):
        """Adiciona uma conta ao cliente."""
        self.contas.append(conta)

class PessoaFisica(Cliente):
    """Representa um cliente pessoa física."""
    def __init__(self, nome: str, data_nascimento: str, cpf: str, endereco: str):
        super().__init__(endereco)
        self.nome: str = nome
        self.data_nascimento: str = data_nascimento
        self._cpf: str = cpf

    @property
    def cpf(self) -> str:
        return self._cpf
    
    def __repr__(self) -> str:
        """Representação canônica do objeto."""
        return f"PessoaFisica(nome='{self.nome}', cpf='{self.cpf}', endereco='{self.endereco}')"

class ContasIterador:
    """Implementação do protocolo Iterator para as contas."""
    def __init__(self, contas: List[Conta]):
        self.contas: List[Conta] = contas
        self._index: int = 0

    def __iter__(self):
        return self

    def __next__(self):
        """Retorna o próximo item formatado ou levanta StopIteration."""
        if self._index >= len(self.contas):
            raise StopIteration

        conta = self.contas[self._index]
        self._index += 1
        
        return str(conta)

def log_transacao(func):
    """Decorador para logar a execução de funções de transação."""
    @wraps(func)
    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] LOG: {func.__name__.upper()} EXECUTADA.")
        return resultado
    return envelope

def menu() -> str:
    """Exibe o menu e captura a opção do usuário."""
    menu_str = """\
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu_str)).strip().lower()

def filtrar_cliente(cpf: str, clientes: List[PessoaFisica]) -> Optional[PessoaFisica]:
    """Busca um cliente pelo CPF. Otimizado com generator expression."""
    return next((cliente for cliente in clientes if cliente.cpf == cpf), None)

def recuperar_conta_cliente(cliente: Cliente):
    """Recupera a primeira conta do cliente (FIXME: precisa de melhoria para escolher)."""
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return None

    return cliente.contas[0]

@log_transacao
def depositar(clientes: List[PessoaFisica]):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    try:
        valor = float(input("Informe o valor do depósito: "))
        if valor <= 0:
            print("@@@ O valor deve ser positivo! @@@")
            return
    except ValueError:
        print("@@@ Valor inválido! @@@")
        return
        
    transacao = Deposito(valor)
    conta = recuperar_conta_cliente(cliente)
    
    if conta:
        cliente.realizar_transacao(conta, transacao)

@log_transacao
def sacar(clientes: List[PessoaFisica]):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    try:
        valor = float(input("Informe o valor do saque: "))
        if valor <= 0:
            print("@@@ O valor deve ser positivo! @@@")
            return
    except ValueError:
        print("@@@ Valor inválido! @@@")
        return

    transacao = Saque(valor)
    conta = recuperar_conta_cliente(cliente)
    
    if conta:
        cliente.realizar_transacao(conta, transacao)

@log_transacao
def exibir_extrato(clientes: List[PessoaFisica]):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    
    transacoes_str = [
        f"{t['data']}\n{t['tipo']}:\n\tR$ {t['valor']:.2f}"
        for t in conta.historico.gerar_relatorio()
    ]

    if not transacoes_str:
        print("Não foram realizadas movimentações.")
    else:
        print("\n".join(transacoes_str))

    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")

@log_transacao
def criar_cliente(clientes: List[PessoaFisica]):
    cpf = input("Informe o CPF (somente número): ").strip().replace(".", "").replace("-", "")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input(
        "Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): "
    )

    cliente = PessoaFisica(
        nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco
    )

    clientes.append(cliente)
    print("\n=== Cliente criado com sucesso! ===")

@log_transacao
def criar_conta(numero_conta: int, clientes: List[PessoaFisica], contas: List[ContaCorrente]):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    conta = ContaCorrente.nova_conta(
        cliente=cliente, numero=numero_conta, limite=500.0, limite_saques=3
    )
    
    contas.append(conta)
    cliente.adicionar_conta(conta) # Uso do método do cliente.

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas: List[Conta]):
    """Lista todas as contas formatadas usando o iterador."""

    for conta_info in ContasIterador(contas):
        print("=" * 100)
        print(conta_info)
    
    if not contas:
        print("Não há contas cadastradas.")


def main():
    """Função principal do sistema."""
    clientes: List[PessoaFisica] = []
    contas: List[ContaCorrente] = []
    
    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            print("\nObrigado por usar o nosso sistema bancário. Até mais!")
            break

        else:
            print(
                "\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@"
            )


if __name__ == "__main__":
    main()