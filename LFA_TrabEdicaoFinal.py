# -*- coding: utf-8 -*-
"""LFATP - LFA trabalho pratico I.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LN5ycVh9GrOElA06-idKpbCQXQZ1xF4e
"""

import pickle as pk
import os
from enum import Enum
import xml.etree.ElementTree as ET
import xml.dom.minidom


class EstadosComparacao(Enum):
    EQUIVALENTE = 1
    NAOEQUIVALENTE = 2
    PENDENTE = 3


class AutomatoFD:
    def __init__(self, Alfabeto):
        Alfabeto = str(Alfabeto)
        self.estados = set()
        self.alfabeto = Alfabeto
        self.transicoes = dict()
        self.inicial = None
        self.finais = set()

    def limpaAfd(self):

        self.__deuErro = False
        self.__estadoAtual = self.inicial

    def criaEstado(self, id, inicial=False, final=False):

        id = int(id)
        if id in self.estados:
            return False
        self.estados = self.estados.union({id})
        if inicial:
            self.inicial = id
        if final:
            self.finais = self.finais.union({id})
        return True

    def criaTransicao(self, origem, destino, simbolo):

        origem = int(origem)
        destino = int(destino)
        simbolo = str(simbolo)
        if not origem in self.estados:
            return False
        if not destino in self.estados:
            return False
        if len(simbolo) != 1 or not simbolo in self.alfabeto:
            return False
        self.transicoes[(origem, simbolo)] = destino
        return True

    def mudaEstadoInicial(self, id):
        if not id in self.estados:
            return
        self.inicial = id

    def mudaEstadoFinal(self, id, final):

        if not id in self.estados:
            return
        if final:
            self.finais = self.finais.union({id})
        else:
            self.finais = self.finais.difference({id})

    def move(self, cadeia):

        for simbolo in cadeia:
            if not simbolo in self.alfabeto:
                self.__deuErro = True
                break
            if (self.__estadoAtual, simbolo) in self.transicoes.keys():
                novoEstado = self.transicoes[(self.__estadoAtual, simbolo)]
                self.__estadoAtual = novoEstado
            else:
                self.__deuErro = True
                break
        return self.__estadoAtual

    def deuErro(self):
        return self.__deuErro

    def estadoAtual(self):
        return self.__estadoAtual

    def estadoFinal(self, id):
        return id in self.finais

    def __str__(self):

        s = 'AFD(E, A, T, i, F): \n'
        s += '  E = { '
        for e in self.estados:
            s += '{}, '.format(str(e))
        s += '} \n'
        s += '  A = { '
        for a in self.alfabeto:
            s += '{}, '.format(a)
        s += '} \n'
        s += '  T = { '
        for (e, a) in self.transicoes.keys():
            d = self.transicoes[(e, a)]
            s += "({}, '{}')-->{},".format(e, a, d)
        s += '} \n'
        s += '  i = {} \n'.format(self.inicial)
        s += '  F = { '
        for e in self.finais:
            s += '{}, '.format(str(e))
        s += '}'
        return s

    def criaJFF(self, nome_arquivo):
        doc = xml.dom.minidom.Document()

        # Crie a estrutura XML para o arquivo JFF
        struct = doc.createElement("structure")
        doc.appendChild(struct)
        type = doc.createElement("type")
        type.appendChild(doc.createTextNode('fa'))
        struct.appendChild(type)
        automato = doc.createElement("automaton")
        struct.appendChild(automato)

        alfabeto = doc.createElement("alphabet")
        automato.appendChild(alfabeto)
        for simbolo in self.alfabeto:
            symbol = doc.createElement("symbol")
            symbol.appendChild(doc.createTextNode(simbolo))
            alfabeto.appendChild(symbol)

        for estado in self.estados:
            estado_element = doc.createElement("state")
            estado_element.setAttribute("id", str(estado))
            automato.appendChild(estado_element)
            
            coord = estado * 50

            x_element = doc.createElement("x")
            x_element.appendChild(doc.createTextNode(str(coord)))
            estado_element.appendChild(x_element)

            y_element = doc.createElement("y")
            y_element.appendChild(doc.createTextNode(str(coord)))
            estado_element.appendChild(y_element)

            if estado == self.inicial:
                inicial = doc.createElement("initial")
                estado_element.appendChild(inicial)
            if estado in self.finais:
                final = doc.createElement("final")
                estado_element.appendChild(final)

        for (origem, simbolo), destino in self.transicoes.items():
            transicao = doc.createElement("transition")
            automato.appendChild(transicao)

            from_element = doc.createElement("from")
            from_element.appendChild(doc.createTextNode(str(origem)))
            transicao.appendChild(from_element)

            to_element = doc.createElement("to")
            to_element.appendChild(doc.createTextNode(str(destino)))
            transicao.appendChild(to_element)

            read_element = doc.createElement("read")
            read_element.appendChild(doc.createTextNode(simbolo))
            transicao.appendChild(read_element)
            transicao.appendChild(doc.createElement("write"))
            transicao.appendChild(doc.createElement("move"))

        with open(nome_arquivo, "w") as arquivo:
            arquivo.write(doc.toprettyxml())

        print(f"Arquivo JFF '{nome_arquivo}' gerado com sucesso!")

    def clonaAutomato(self):
        novoAutomato = AutomatoFD(self.alfabeto)
        novoAutomato.estados = self.estados
        novoAutomato.transicoes = self.transicoes
        novoAutomato.inicial = self.inicial
        novoAutomato.finais = self.finais
        return novoAutomato

    def removerTransicoes(self, estado):
        transicoes_a_remover = []
        for transicao, destino in self.transicoes.items():
            origem, simbolo = transicao
            if origem == estado or destino == estado:
                transicoes_a_remover.append(transicao)
        for transicao in transicoes_a_remover:
            del self.transicoes[transicao]

    def minimizaAfd(self):
        mat_equivalentes = self.testa_equivalencia()
        for par in mat_equivalentes:
            estado1 = par[0]
            estado2 = par[1]
            estadoexcluir = max(estado1, estado2)
            estadosalvar = min(estado1, estado2)
            for simbolo in self.alfabeto:
                for estados in self.estados:
                    if estadoexcluir == obter_destino(self, estados, simbolo):
                        self.criaTransicao(estados, estadosalvar, simbolo)

            for final in self.finais:
                if estadoexcluir == final:
                    self.mudaEstadoFinal(estadoexcluir, False)

            self.estados.discard(estadoexcluir)
            self.removerTransicoes(estadoexcluir)
        
        return self
    
    def __nao_marcado(self, afd_dict):
        for estado1 in self.estados:
            for estado2 in self.estados:
                if estado1 > estado2:
                    if afd_dict[estado1, estado2] == EstadosComparacao.PENDENTE:
                        afd_dict[estado1, estado2] = EstadosComparacao.EQUIVALENTE

    def __equivalenciaEstados(self):
        afd_dict = dict()
        ec = EstadosComparacao
        for estado1 in self.estados:
            for estado2 in self.estados:
                if estado1 > estado2:
                    if estado1 in self.finais and estado2 not in self.finais:
                        afd_dict[estado1, estado2] = ec.NAOEQUIVALENTE
                    elif estado2 in self.finais and estado1 not in self.finais:
                        afd_dict[estado1, estado2] = ec.NAOEQUIVALENTE
                    else:
                        afd_dict[estado1, estado2] = ec.PENDENTE

        return afd_dict

    def testa_equivalencia(self):
        afd_dict = self.__equivalenciaEstados()
        ec = EstadosComparacao
        pendente = True
        mudou = False
        while pendente and not mudou:
            mudou = True
            pendente = True
            for estado1 in self.estados:
                equivalente = True
                for estado2 in self.estados:
                    if estado1 > estado2:
                        if afd_dict[estado1, estado2] is None or afd_dict[estado1, estado2] == ec.PENDENTE:
                            pendente = False
                            for simbolo in self.alfabeto:
                                if (estado1, simbolo) not in self.transicoes or (
                                        estado2, simbolo) not in self.transicoes:
                                    equivalente = False
                                    afd_dict[estado1, estado2] = ec.NAOEQUIVALENTE
                                    break

                                estado1_proximo = self.transicoes[estado1, simbolo]
                                estado2_proximo = self.transicoes[estado2, simbolo]
                                if estado2_proximo > estado1_proximo:
                                    estado2_proximo, estado1_proximo = estado1_proximo, estado2_proximo

                                if estado1_proximo != estado2_proximo and afd_dict[
                                    estado1_proximo, estado2_proximo] is ec.NAOEQUIVALENTE:
                                    equivalente = False
                                    mudou = False
                                    afd_dict[estado1, estado2] = ec.NAOEQUIVALENTE
                                    break
                                elif estado2_proximo != estado1_proximo and (
                                        afd_dict[estado1_proximo, estado2_proximo] is None or afd_dict[
                                    estado1_proximo, estado2_proximo] == ec.PENDENTE):
                                    equivalente = False
                                    mudou = False
                                    afd_dict[estado1, estado2] = ec.PENDENTE

                            if equivalente:
                                mudou = False
                                afd_dict[estado1, estado2] = ec.EQUIVALENTE

        self.__nao_marcado(afd_dict)
        matriz_equivalencia = []
        for chave, valor in afd_dict.items():
            if valor == EstadosComparacao.EQUIVALENTE:
                matriz_equivalencia.append(chave)
        return matriz_equivalencia

    def afdComplemento(self):
        afd = AutomatoFD(self.alfabeto)
        afd.estados = self.estados
        afd.inicial = self.inicial
        afd.transicoes = self.transicoes
        for estado in self.estados:
            if estado not in self.finais:
                afd.mudaEstadoFinal(estado, True)
        return afd


def obter_destino(self, origem, simbolo):
    if (origem, simbolo) in self.transicoes:
        return self.transicoes[(origem, simbolo)]
    else:
        return None


def uneAlfabeto(alfabeto1, alfabeto2):
    alfabeto = alfabeto1
    for simbolo in alfabeto2:
        if simbolo not in alfabeto:
            alfabeto += simbolo
    return alfabeto


def UniaoAutomatos(automato1, automato2):
    qtd_estados1 = len(automato1.estados)
    qtd_estados2 = len(automato2.estados)
    total_estados = qtd_estados2 + qtd_estados1
    automato_concatenado = AutomatoFD((uneAlfabeto(automato1.alfabeto, automato2.alfabeto)))

    for i in range(1, total_estados + 1):
        automato_concatenado.criaEstado(i)
    automato_concatenado.mudaEstadoInicial(1)

    automato_concatenado.finais = automato1.finais.union(automato2.finais)

    for estado in range(1, qtd_estados1 + 1):
        for simbolo in automato1.alfabeto:
            destino = obter_destino(automato1, estado, simbolo)
            automato_concatenado.criaTransicao(estado, destino, simbolo)
    for estado2 in range(1, qtd_estados2 + 1):
        for simbolo in automato2.alfabeto:
            destino = obter_destino(automato2, estado2, simbolo)
            automato_concatenado.criaTransicao(estado2 + qtd_estados1, destino, simbolo)

    return automato_concatenado


def automatosEquivalentes(automato1, automato2, cadeia):
    automato_concatenado = UniaoAutomatos(automato1, automato2)
    print(automato_concatenado)
    mat = []
    matriz = automato_concatenado.testa_equivalencia()
    palavra = cadeia
    automato1.limpaAfd()
    automato2.limpaAfd()
    parada1 = automato1.move(palavra)
    parada2 = automato2.move(palavra)
    if automato1.deuErro() != automato2.deuErro():
        return False
    else:
        inicial1 = automato1.inicial
        inicial2 = automato2.inicial + len(automato1.estados)
        mat = (inicial1, inicial2)
        for chave in matriz:
            if mat == chave:
                return True
        mat2 = (inicial2, inicial1)
        for chave1 in matriz:
            if mat2 == chave1:
                return True
        return False


# def intercessaoAutomato(automato1, automato2):

def encontraParNaMatriz(matriz, valor1, valor2):
    for indice, par in enumerate(matriz):
        if par == [valor1, valor2]:
            return indice
    return None  # Retorna None se o par ordenado não for encontrado na matriz


def multiplicaAutomato(automato1, automato2, operacao):
    print(len(automato1.estados))
    print(len(automato2.estados))
    num_estados = len(automato1.estados) * len(automato2.estados)
    print(num_estados)
    estado_erro = num_estados + 1
    conjunto_uniao_estados = [[x, y] for x in automato1.estados for y in automato2.estados]

    afd = AutomatoFD(uneAlfabeto(automato1.alfabeto, automato2.alfabeto))

    # cria estado de erro
    afd.criaEstado(estado_erro)
    for simbolo in afd.alfabeto:
        afd.criaTransicao(estado_erro, estado_erro, simbolo)

    for estado in range(num_estados):  # para um estado de conj_uniao, 0 = automato1, 1 = automato2
        # print('estado: ',estado)
        afd.criaEstado(estado + 1)

    estado = 0
    for estado in range(num_estados):  # para um estado de conj_uniao, 0 = automato1, 1 = automato2
        # print('estado: ',estado)

        estadoDoAfd1 = conjunto_uniao_estados[estado][0]
        estadoDoAfd2 = conjunto_uniao_estados[estado][1]

        if (estadoDoAfd1 == automato1.inicial and estadoDoAfd2 == automato2.inicial):
            afd.inicial = (encontraParNaMatriz(conjunto_uniao_estados, estadoDoAfd1, estadoDoAfd2) + 1)

        if (operacao == 1):  # uniao

            if (estadoDoAfd1 in automato1.finais or estadoDoAfd2 in automato2.finais):
                afd.mudaEstadoFinal(encontraParNaMatriz(conjunto_uniao_estados, estadoDoAfd1, estadoDoAfd2) + 1, True)

        elif (operacao == 2):  # intercessao

            if (estadoDoAfd1 in automato1.finais and estadoDoAfd2 in automato2.finais):
                afd.mudaEstadoFinal(encontraParNaMatriz(conjunto_uniao_estados, estadoDoAfd1, estadoDoAfd2) + 1, True)
        elif (operacao == 3):  # diferenca

            if (estadoDoAfd1 in automato1.finais and estadoDoAfd2 not in automato2.finais):
                afd.mudaEstadoFinal(encontraParNaMatriz(conjunto_uniao_estados, estadoDoAfd1, estadoDoAfd2) + 1, True)

        for simbolo in automato1.alfabeto:

            destinoTransicao1 = obter_destino(automato1, estadoDoAfd1, simbolo)
            destinoTransicao2 = obter_destino(automato2, estadoDoAfd2, simbolo)
            destino = encontraParNaMatriz(conjunto_uniao_estados, destinoTransicao1, destinoTransicao2)
            if (destino != None):
                afd.criaTransicao(estado + 1, destino + 1, simbolo)
            else:
                afd.criaTransicao(estado + 1, estado_erro, simbolo)
    return afd

def carregaJFF(nome_arquivo):
        try:
            automato = AutomatoFD("")
            tree = ET.parse(nome_arquivo)
            root = tree.getroot()
            
            # Processar o alfabeto
            alfabeto = set()
            for symbol in root.find(".//alphabet").findall("symbol"):
                alfabeto.add(symbol.text)
            automato.alfabeto = alfabeto

            # Processar os estados
            for state in root.find(".//automaton").findall("state"):
                estado_id = int(state.get("id"))
                automato.estados.add(estado_id)
                if state.find("initial") is not None:
                    automato.inicial = estado_id
                if state.find("final") is not None:
                    automato.finais.add(estado_id)

            # Processar as transições
            for transition in root.find(".//automaton").findall("transition"):
                origem = int(transition.find("from").text)
                destino = int(transition.find("to").text)
                simbolo = transition.find("read").text
                automato.criaTransicao(origem, destino, simbolo)

            return automato
        except FileNotFoundError:
            print(f"Erro: Arquivo {nome_arquivo} não encontrado !")
            return None

def menu(vetAfd):
    id = 0
    for automato in vetAfd:
        print(f"Automato {id}:\n", id, automato)
        id = id + 1
        print('-----------------------------------------------\\-----------------------------------------------')
    print('=====================================================\\menu\\=====================================================')
    print("Dados os automatos acima, qual operação deseja fazer com eles?")
    print("0-Sair")
    print("1-salvar, carregar ou criar copia")
    print("2-Algoritmos de Minimização")
    print("3-Operação com conjuntos")
    operacao = int(input("Qual compartimento deseja entrar?:"))
    op = 1
    if operacao == 0:
        return 0
    elif operacao == 1:
        print('=========================================SALVAR,CARREGAR OU CRIAR COPIA=========================================')
        print("0-voltar")
        print("1-Salvar")
        print("2-Carregar")
        print("3-Cria copia de um AFD em outro ")
        op = int(input("Qual operação deseja fazer?:"))
        if op == 0:
           menu(vetAfd)
        elif (op == 1):
            indice = int(input("Digite o indice do AFD a ser usado: "))
            nome_arquivo = str(input("Digite o nome do arquivo: "))
            vetAfd[indice].criaJFF(nome_arquivo)
            menu(vetAfd)
        elif (op == 2):
            indice = int(input("Digite o indice do AFD a ser usado: "))
            nome_arquivo = str(input("Digite o nome do arquivo: "))
            vetAfd[indice].carregaJFF(nome_arquivo)
            menu(vetAfd)
        elif (op == 3):
            indice = int(input("Digite o indice do AFD que será clonado: "))
            vetAfd.append(vetAfd[indice].clonaAutomato())
            print("Clonagem finalizada")
            menu(vetAfd)
        else:
            print("Essa opção não existe!")
            menu(vetAfd)
            
    elif operacao == 2:
        print('===========================================ALGORITMOS DE MINIMIZAÇÃO============================================')
        print("0-voltar")
        print("1-Testar os estados de equivalencia do AFD")
        print("2-Testar equivalencia entre 2 AFD fornecidos")
        print("3-Calcular o automato minimizado")
        opminimzacao = int(input("Qual operação deseja fazer?:"))
        if opminimzacao == 0:
            menu(vetAfd)
        elif opminimzacao == 1:
            print("0- Voltar ao menu")
            indice = int(input("Qual dos autômatos você deseja testar a equivalencia de estados?"))
            if indice == 0:
                menu(vetAfd)
            elif indice > len(vetAfd) or indice < 0:
                print(" Autômato Inesistente !")
                menu(vetAfd)
            else:
                mat1 = []
                mat1 = vetAfd[indice].testa_equivalencia()
                print("Os estados equivalentes do automato são:", mat1)
                menu(vetAfd)
        elif opminimzacao == 2:
            print("Para ver se os autômatos são equivalentes, primeiro passe uma palavra para verificar se eles são equivalentes")
            palavra = input("Palavra:")
            indice1 = int(input("Escolha o primeiro autômato?"))
            indice2 = int(input("Escolha o segundo autômato?"))
            retorno = automatosEquivalentes(vetAfd[indice1],vetAfd[indice2] , palavra)
            if retorno == True:
                print("Os autômatos são equivalentes!")
            else:
                print("Os autômatos não são Equivalentes!")
        elif opminimzacao == 3:
            print("0- Voltar ao menu")
            mini = int(input("Qual dos automatos você deseja fazer a minimização de estados?"))
            if mini == 0:
                menu(vetAfd)
            elif mini > len(vetAfd) or mini < 0:
                print(" Autômato Inesistente !")
                menu(vetAfd)
            else:
                vetAfd.append(vetAfd[mini].minimizaAfd())
                print('-----------------------------------------------\\-----------------------------------------------')
        else:
            print("essa operação não existe!")
            menu(vetAfd)

    elif operacao == 3:
        print('=============================================OPERAÇÃO COM CONJUNTOS=============================================')
        print("0-voltar")
        print("1-Uniao ")
        print("2-Intercecao ")
        print("3-Diferenca")
        print("4-Complemtento de automato")
        op = int(input("Qual operação deseja fazer?:"))
        if op == 0:
            menu(vetAfd)
        elif op == 1:
            indice1 = int(input("digite indice o primeiro autômato?:"))
            indice2 = int(input("digite indice o segundo autômato?:"))
            vetAfd.append(multiplicaAutomato(vetAfd[indice1],vetAfd[indice2], op))
            menu(vetAfd)
        elif op == 2:
            indice1 = int(input("digite indice o primeiro autômato?:"))
            indice2 = int(input("digite indice o segundo autômato?:"))
            vetAfd.append(multiplicaAutomato(vetAfd[indice1],vetAfd[indice2], op))
            menu(vetAfd)
        elif op == 3:
            indice1 = int(input("digite indice o primeiro autômato?:"))
            indice2 = int(input("digite indice o segundo autômato?:"))
            vetAfd.append(multiplicaAutomato(vetAfd[indice1],vetAfd[indice2], op))
            menu(vetAfd)
        elif op == 4:            
            indice = int(input("digite indice o primeiro autômato?:"))
            vetAfd.append(vetAfd[indice].afdComplemento())
            menu(vetAfd)
        else:
            print("Essa opção não existe!")
            menu(vetAfd)
    else:
        print("essa opção é invalida!")
        menu(vetAfd)
    
    return menu(vetAfd)


if __name__ == '__main__':
    afd = AutomatoFD('ab')
    for i in range(1, 4):
        afd.criaEstado(i)
    afd.mudaEstadoInicial(1)

    # # Defina o estado final
    afd.mudaEstadoFinal(2, True)

    # Crie as transições
    afd.criaTransicao(1, 3, 'a')
    afd.criaTransicao(1, 2, 'b')
    afd.criaTransicao(2, 1, 'a')
    afd.criaTransicao(2, 2, 'b')
    afd.criaTransicao(3, 3, 'a')
    afd.criaTransicao(3, 2, 'b')

    afdSecundario = AutomatoFD('ab')
    for i in range(1, 7):
        afdSecundario.criaEstado(i)
    afdSecundario.mudaEstadoInicial(1)

    afdSecundario.mudaEstadoFinal(1, True)
    afdSecundario.mudaEstadoFinal(5, True)
    afdSecundario.mudaEstadoFinal(6, True)

    afdSecundario.criaTransicao(1, 3, 'a')
    afdSecundario.criaTransicao(1, 2, 'b')
    afdSecundario.criaTransicao(2, 2, 'a')
    afdSecundario.criaTransicao(2, 1, 'b')
    afdSecundario.criaTransicao(3, 5, 'a')
    afdSecundario.criaTransicao(3, 6, 'b')
    afdSecundario.criaTransicao(4, 6, 'a')
    afdSecundario.criaTransicao(4, 5, 'b')
    afdSecundario.criaTransicao(5, 4, 'a')
    afdSecundario.criaTransicao(5, 3, 'b')
    afdSecundario.criaTransicao(6, 3, 'a')
    afdSecundario.criaTransicao(6, 4, 'b')

    vetAfd = []
    vetAfd.append(afd)
    vetAfd.append(afdSecundario)
    vetAfd.append(AutomatoFD(""))
    menu(vetAfd)