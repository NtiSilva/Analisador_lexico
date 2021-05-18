# -*- coding: utf-8 -*-
import sys
import re
import xml.etree.ElementTree as ET

token = ""
numerico = ""
posicao = 0
separadores = ['(', ')', '{', '}', '=', '.', '|']
operadores = ['-', '+', '/', '*', '<', '>', '==', '!=', '&']
lista_erros = []
token_geral = []
tabela_token = {}
linha = 0
coluna = 0
id_tabela = 0
acumula = ""

def aux_agrupa(elem, i, lista, cont, elem_doub, next_elem):
    if elem in i:
        if(cont + 1) < len(lista):
            if next_elem in lista[cont + 1]:
                lista.pop(cont+1)
                lista.insert(cont,elem_doub)
                lista.pop(cont + 1)

def agrupa(lista):
    # agrupa elem na lista
    cont = 0
    # print(lista)
    for i in lista:
        aux_agrupa("-", i, lista, cont, "--", "-")
        aux_agrupa("+", i, lista, cont, "++", "+")
        aux_agrupa("=", i, lista, cont, "==", "=")
        aux_agrupa("&", i, lista, cont, "&&", "&")
        aux_agrupa("|", i, lista, cont, "||", "|")
        aux_agrupa("<", i, lista, cont, "<=", "=")
        aux_agrupa(">", i, lista, cont, ">=", "=")
        aux_agrupa("!", i, lista, cont, "!=", "=")
        cont = cont + 1

def imprime_tabela(tabela):
    arq_tabela = open("tabela_token", "w")
    arq_tabela.write("Tabela de Simbolos\n")
    for i in sorted(tabela):
        arq_tabela.write("Chave:" + str(i) + " " + str(tabela_token[i]) + "\n")
    arq_tabela.close()


def abrir_arquivo():
    try:
        nome = sys.argv[1]
        entrada = open(nome, "r")
    except Exception as e:
        entrada = open("teste.c", "r")
    return entrada


def verifica_numero(elem):
    return 0 if(re.match(r"[\d.]", elem)) else 1


def return_numero(num):
    return re.match(r"(^[0-9]*$|[0-9]+.[0-9]+)", num)


def verifica_identificador(elem):
    return 0 if(re.match(r"[\w]", elem)) else 1


def verifica_erro(elem, token_geral, lista_erros, linha, coluna):
    separadores = ['(', ')', '{', '}', ',', '=', '.', '-', '+', '/', '*', '!', '&', '|', '>', '<']
    if not re.match("[\w]", elem):
        if elem not in separadores:
            if not re.search(r"\s", elem):
                token_geral.append("[Token Invalido]")
                lista_erros.append(
                    [add_linha_coluna(token, linha, coluna), elem, "ERRO"])
            return 0
    return 1


def verifica_reservada(token):
    reservadas = ['int', 'float', 'char', 'if', 'else']
    cont = 0
    for i in reservadas:
        cont = cont + 1
        if (token == i):
            return cont


def add_linha_coluna(token, linha, coluna):
    """Adiciona linha e coluna"""
    p_inicio = coluna - len(token)
    return "L:" + str(linha) + " C:(" + str(p_inicio) + "," + str(coluna) + ")"


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
                posicao = 4
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
            # verifica se é um identificador literal
            if re.match(r"[\"]", elem) and posicao == 0 and posicao != 4:
                posicao = 3
            # se não for identificador valido é separador
            if verifica_numero(elem) and verifica_identificador(elem) and posicao == 0 and posicao != 4:
                if verifica_erro(elem, token_geral, lista_erros, linha, coluna):
                    token_geral.append([elem])

        if posicao is 1:
            # verifica identificador

            if re.match(r"([\w])", elem):
                token = token + elem
                # print("token", token)
                # print("elem", elem)
            if verifica_identificador(elem):
                posicao = 0
                if verifica_reservada(token):
                    # print("teste", token)
                    tabela_token[id_tabela] = [add_linha_coluna(token, linha, coluna),
                                               token, "Plv Res: " + str(verifica_reservada(token))]
                    token_geral.append([add_linha_coluna(token, linha, coluna),
                                        token, "Plv Res: " + str(verifica_reservada(token))])
                    if elem is not " ":
                        if verifica_erro(elem, token_geral, lista_erros, linha, coluna):
                            token_geral.append([elem])
                    token = ""
                else:
                    lista_erros.append(
                        [add_linha_coluna(token, linha, coluna), token, "ERRO"])

                    tabela_token[id_tabela] = [add_linha_coluna(
                        token, linha, coluna), token, "ID"]
                    token_geral.append(
                        [add_linha_coluna(token, linha, coluna), token, "id"])

                    # insere o elem como separador
                    if verifica_identificador(elem):
                        if elem is not re.match(r"\s", elem):
                            if verifica_erro(elem, token_geral, lista_erros, linha, coluna):
                                token_geral.append([elem])
                        posicao = 0
                    token = ""

        if posicao is 2:
            # verifica se é numero
            if re.match(r"[\w.]", elem):
                numerico = numerico + elem
            if verifica_numero(elem):
                valor = return_numero(numerico)
                if(valor):
                    if valor is not None:
                        tabela_token[id_tabela] = [add_linha_coluna(
                            token, linha, coluna), valor.group(), "num"]
                        token_geral.append(
                            [add_linha_coluna(token, linha, coluna), valor.group(), "num"])
                        if elem is not " ":
                            if verifica_erro(elem, token_geral, lista_erros, linha, coluna):
                                token_geral.append([elem])
                            posicao = 0
                            numerico = ""
                else:
                    # identifica token invalido
                    if elem in separadores or re.match(r"\s|\n", elem) or elem in operadores:
                        token_geral.append("[Token Invalido]")
                        lista_erros.append(
                            [numerico, add_linha_coluna(numerico, linha, coluna)])
                        numerico = ""
                        estado = 0
            else:
                if elem is not " ":
                    if verifica_erro(elem, token_geral, lista_erros, linha, coluna):
                        token_geral.append([elem])
                posicao = 0

        if posicao is 3:
            # indentifica o literal
            if re.match(r"[%a-zA-z0-9\"\s]", elem):
                token = token + elem
                if re.match(r"[\"]", elem):
                    lit = re.match(r"[\"]+[%\w\s]+[\"]*", token)
                    if lit is not None:
                        tabela_token[id_tabela] = [add_linha_coluna(
                            token, linha, coluna), lit.group, "ATT"]
                        token_geral.append(
                            [add_linha_coluna(token, linha, coluna), lit.group, "ATT"])
                        token = ""
                        estado = 0

        if posicao is 4:
            "passa comentario"
            acumula = acumula + elem
            if re.search(r"(\*\/)", acumula):
                token_geral.append("[*/]")
                estado = 0

# Sintatico


def lerXML():
    xml = ET.parse('LALRTable.xml')
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


if __name__ == '__main__':
    agrupa(token_geral)
    lista_erros = []
    simbolosMap, producoesMap, lalrMap = lerXML()
    # analisadorSintatico(listaTS, simbolosMap, producoesMap, lalrMap)
    imprime_tabela(tabela_token)
