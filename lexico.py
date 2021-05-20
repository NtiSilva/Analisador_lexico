# -*- coding: utf-8 -*-
import sys
import re
import xml.etree.ElementTree as ET

token = ""
numerico = ""
posicao = 0
separadores = ['(', ')', '{', '}', '=', '.', '|']
operadores = ['-', '+', '/', '*', '<', '>', '&']
lista_erros = []
token_geral = []
tabela_token = {}
tabela_sin = {}
linha = 0
coluna = 0
id_tabela = 0
acumula = ""

def imprime_tabela(tabela):
    arq_tabela = open("Tabela Lexica", "w")
    arq_tabela.write("Tabela de Simbolos\n")
    for i in sorted(tabela):
        arq_tabela.write("Chave:" + str(i) + " " + str(tabela_token[i]) + "\n")
    arq_tabela.close()

def imprime_tabela_s(tabela):
    arq_tabela = open("Tabela Sintatica", "w")
    arq_tabela.write("Tabela de Simbolos\n")
    for i in sorted(tabela):
        arq_tabela.write("Chave:" + str(i) + " " + str(tabela_sin[i]) + "\n")
    arq_tabela.close()

def imprime_erros(lista):
    arq_erro = open("Lista de erros lexicos", "w")
    arq_erro.write("Tabela de Erros")
    linhas = len(lista)
    colunas = len(lista[0])
    for i in range(linhas):
        for j in range(colunas):
            if j == colunas -1:
                arq_erro.write(str(lista[i]))
            else:
                arq_erro.write("\n")
    arq_erro.close()

def abrir_arquivo():
    try:
        nome = sys.argv[1]
        entrada = open(nome, "r")
    except Exception as e:
        entrada = open("teste.c", "r")
    return entrada

def verifica_numero(elem):
    return 1 if(re.match(r"\d", elem)) else 0

def verifica_identificador(elem):
    return 0 if(re.match(r"[\w]", elem)) else 1

def verifica_separador(elem):
    separadores = ['(', ')', '{', '}', ',', '=', '+',
                   '/', '*', '!', '&', '|', '>', '<', '^']
    return 0 if elem not in separadores else 1

def verifica_erro(elem, token_geral, lista_erros, linha, coluna):
    separadores = ['(', ')', '{', '}', ',', '=', '+',
                   '/', '*', '!', '&', '|', '>', '<', '^']
    if not re.match("[\w]", elem):
        if elem not in separadores:
            if not re.search(r"\s", elem):
                lista_erros.append(["Error", elem, linha])
                token_geral.append(["Error", elem, linha])
            return 0
        else:
            return elem
    return 1

def verifica_reservada(token):
    reservadas = ['int', 'float', 'char', 'if', 'else', 'while']
    cont = 0
    for i, valor in enumerate(reservadas):
        if (token == valor):
            cont = cont + 1
            return cont

def verifica_iden(token):
    identificador = ['a', 'b', 'c', 'd', 'x', 'y', 'z']
    cont = 0
    for i, valor in enumerate(identificador):
        if (token == valor):
            cont = cont + 1
            return cont

entrada = abrir_arquivo()
for arq in entrada:
    linha = linha + 1
    coluna = 0
    for elem in arq:
        id_tabela = (id_tabela + 1)
        coluna = coluna + 1

        if posicao is 0:
            # verifica se é um comentario
            if elem is "/" and arq[coluna] is "*" and posicao == 0 and posicao != 4:
                posicao = 3
                token_geral.append(["*/"])
            # ignora se é linha comentada
            if re.search(r"^(#)|[/]{2}", arq) and posicao == 0 and posicao != 4:
                break
            # verifica se é um identificador valido
            if re.match(r"([A-Za-z_])", elem) and posicao == 0 and posicao != 4:
                posicao = 1
            # verifica se é uma numero
            if re.match(r"[0-9]", elem) and posicao == 0 and posicao != 4:
                posicao = 2
            #verifica se é um separador
            if verifica_separador(elem):
               posicao = 4
            # se não for identificador valido é separador
            if verifica_numero(elem) == 0 and verifica_identificador(elem) == 1 and posicao == 0 and posicao != 4:
                if verifica_erro(elem, token_geral, lista_erros, linha, coluna):
                    token_geral.append(["Error", elem, linha])

        if posicao is 1:
            # verifica identificador
            if re.match(r"([\w])", elem):
                token = token + elem
            if verifica_identificador(elem):
                posicao = 0
                if verifica_reservada(token):
                    tabela_token[id_tabela] = ["Plv Res: " + str(verifica_reservada(token)), token, linha]
                    token_geral.append([token, token, linha])
                    if elem is not " ":
                        if verifica_erro(elem, token_geral, lista_erros, linha, coluna):
                            token_geral.append([linha, elem, 'Error'])
                            lista_erros.append(["Error", token, linha])
                    token = ""
                else:
                    if(verifica_iden(token)):
                        tabela_token[id_tabela] = ["id", token, linha]
                        token_geral.append(["id", token, linha])
                    else:
                        token_geral.append(["Error ", token, id_tabela])
                        lista_erros.append(["Error", token, linha])

                    # insere o elem como separador
                    if verifica_identificador(elem):
                        if elem is not re.match(r"\s", elem):
                            if verifica_erro(elem, token_geral, lista_erros, linha, coluna):
                                token_geral.append([elem, elem, linha])
                        posicao = 0
                    token = ""

        if posicao is 2:
            # verifica se é numero
            if re.match(r"[\w.]", elem):
                numerico = numerico + elem
            if verifica_numero(elem):
                valor = re.match(r"(^[0-9]*$|[0-9]+.[0-9]+)", numerico)
                if(valor):
                    if valor is not None:
                        tabela_token[id_tabela] = ["num", valor.group(), linha]
                        token_geral.append(["num", valor.group(), linha])
                        posicao = 0
                        numerico = ""
                else:
                    # identifica token invalido
                    if elem in separadores or re.match(r"\s|\n", elem) or elem in operadores:
                        token_geral.append(["Error", linha, elem])
                        lista_erros.append(["Error", linha, elem])
                        numerico = ""
                        estado = 0
            else:
                if elem is not " ":
                    if verifica_erro(elem, token_geral, lista_erros, linha, coluna):
                        token_geral.append(['', linha, elem])
                posicao = 0

        if posicao is 3:
            # não adiciona comentario aos tokens
            acumula = acumula + elem
            if re.search(r"(\*\/)", acumula):
                token_geral.append("[*/]")
                estado = 0

        if posicao is 4:
            if verifica_separador(elem):
                tabela_token[id_tabela] = [elem, elem, linha, "separador"]
                token_geral.append([elem, elem, linha, "separador"])
                posicao = 0
            else:
                if verifica_erro(elem, token_geral, lista_erros, linha, coluna):
                    token_geral.append(["Error", linha,  elem])
                posicao = 0

token_geral.append(["EOF", '$', linha])

# Sintatico

def lerXML():
    xml = ET.parse('MinhaTabela.xml')
    raiz = xml.getroot()

    simbolos = raiz.iter('m_Symbol')
    producoes = raiz.iter('m_Production')
    tabelaLALR = raiz.iter('LALRTable')

    # Mapeando resultados
    simbolosMap = {}
    for s in simbolos:
        for i in s:
            simbolosMap[i.attrib["Name"]] = i.attrib["Index"]

    producoesMap = []
    for p in producoes:
        for i in p:
            a = (i.attrib["NonTerminalIndex"], i.attrib["SymbolCount"])
            producoesMap.append(a)

    lalrMap = []
    for t in tabelaLALR:
        for i in t:
            lEstados = []
            for j in i:
                a = (j.attrib["SymbolIndex"],
                     j.attrib["Action"], j.attrib["Value"])
                lEstados.append(a)
            lalrMap.append(lEstados)

    return simbolosMap, producoesMap, lalrMap


def analisadorSintatico(token_geral, simbolosMap, producoesMap, lalrMap):
    estadoAtualFita = 0

    pilha = []
    pilha.append('0')

    fita = []
    fitaLinha = []

    #retorna só o tipo do atributo e salva na fita
    for l in range(len(token_geral)):
        for e in range(len(token_geral[l])):
            fita.append(token_geral[l][0])
            fitaLinha.append(token_geral[l][2])
            break

    print(fita)
    
    # converte os valores salvos na fita para os volores dos simbolos
    for i, j in enumerate(fita):
        fita[i] = simbolosMap[j]

    print(fita)
    status = ''
    while(status != 'AC'):
        print(fita[estadoAtualFita])
        estadoTabela = lalrMap[int(pilha[-1])]
        encontrado = False
        for simb in estadoTabela:
            if simb[0] == fita[estadoAtualFita]:
                print("pilha", pilha)
                acao, valor = simb[1], simb[2]
                simbE = simb[0]
                encontrado = True
                break

        if encontrado:
            if acao == '1':
                pilha.append(simbE)
                pilha.append(valor)
                estadoAtualFita += 1
            elif acao == '2':
                # retirar dobro
                # NomeDaRegra, Tamanho
                tupla = producoesMap[int(valor)]
                desempilha = len(pilha) - 2 * int(tupla[1])
                del pilha[desempilha:]
                # empilha nome regra
                pilha.append(tupla[0])
                # verifica salto
                proxEstado = lalrMap[int(pilha[-2])]
                encontrado2 = False
                for i in proxEstado:
                    if i[0] == pilha[-1]:
                        acao, valor = i[1], i[2]
                        if acao == '3':
                            pilha.append(valor)
                        encontrado2 = True
                        break
                if not encontrado2:
                    print('Erro sintático na linha {}'.format(
                        fitaLinha[estadoAtualFita]))
                    break
            elif acao == '3':
                pilha.append(valor)
            elif acao == '4':
                print('Aceita')
                status = 'AC'
        else:
            print('Erro sintático na linha {}'.format(
                fitaLinha[estadoAtualFita]),
                estadoAtualFita)
            break


if __name__ == '__main__':
    # agrupa(token_geral)
    if (lista_erros):
        print("Erros lexicos foram encontrados, verifique o arquivo de erros!!")
        imprime_erros(lista_erros, "Lexico")
    else:
        lista_erros = []
        simbolosMap, producoesMap, lalrMap = lerXML()
        # print("simbolos", simbolosMap)
        # print("producoes", producoesMap)
        # print("lalr", lalrMap)
        # print("tabela", tabela_token)
        # print("token",  token_geral)
        imprime_tabela(tabela_token)
        analisadorSintatico(token_geral, simbolosMap, producoesMap, lalrMap)
        imprime_tabela_s(tabela_sin)

