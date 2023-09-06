from Horario import Horario
from Disciplina import Disciplina
from Sala import Sala
from extrai_salas import ExtraiSalas
from extrai_horarios_aula import ExtraiHorariosAula
import pandas as pd
import gurobipy as gp
import numpy as np
from gurobipy import GRB

def cria_csv(disciplinas,salas,horaraios,x):

    alocacoes=[]
    #print("Disciplina  | Horário | Sala | Capacidade restante")
    for d in disciplinas:
        for s in salas:
            for h in disciplinas[d].horarios:
                #print(x[d,s,h].X)
                if(round(x[d,s,h].X))==1:
                    #print(d,h,s,(salas[s].capacidade-disciplinas[d].alunos))
                    alocacoes.append([disciplinas[d].curso,d, h, s, (salas[s].capacidade-disciplinas[d].alunos)])

    # Criar um DataFrame com as informações
    df = pd.DataFrame(alocacoes, columns=["Curso", "Disciplina", "Horario", "Sala", "Capacidade Restante"])

    # Salvar o DataFrame em um arquivo CSV
    nome_arquivo = "alocacoes.csv"
    df.to_csv(nome_arquivo, index=False)
    print("Alocações realizadas com sucesso!")

def exporta_alocacoes(disciplinas,salas,horarios,x):
    alocacoes=[]
    linhas=[]
    linha_salas=[]
    for s in salas:
        linha_salas.append(s)
    

    coluna_horarios=[]
    for h in horarios:
        coluna_horarios.append(h)

    matriz = [['-' for coluna in range(len(coluna_horarios))] for linha in range(len(linha_salas))]

    for d in disciplinas:
        for s in salas:
            for h in disciplinas[d].horarios:
                if(round(x[d,s,h].X))==1:
                    linha = linha_salas.index(s)
                    coluna = coluna_horarios.index(h)
                    matriz[linha][coluna] = d

    # print(coluna_horarios)
    # for i in range(len(linha_salas)):
    #     for j in range(len(coluna_horarios)):
    #         print (matriz[i][j],end=" ")
    #     print("")
        
    df = pd.DataFrame(matriz)

    # Criar um DataFrame com rótulos personalizados
    df = pd.DataFrame(matriz, columns=coluna_horarios, index=linha_salas)

    # Exibir o DataFrame personalizado
    nome_arquivo = "alocacoes_v2.csv"
    df.to_csv(nome_arquivo, index=True)
    print("Alocações realizadas com sucesso!")
    
            

def main():
    salas = ExtraiSalas("./dados/salas.csv").extrai_salas()
    disciplinas, horarios = ExtraiHorariosAula("./dados/horarios_teste.xlsx").extrai_horarios_aula()

    # Criando o modelo
    m = gp.Model()

    # Variaveis
    x = {}
    for d in disciplinas:
        for h in disciplinas[d].horarios:
            for s in salas:
                x[d, s, h] = m.addVar(vtype=gp.GRB.BINARY, name=f"x[{d}, {s}, {h}]")
    y = m.addVars(disciplinas,salas,vtype=gp.GRB.INTEGER, name="y")

    # Cria vetor de variaveis das salas preferenciais
    vet_salas_preferenciais=[]

    for d in disciplinas:
        for h in disciplinas[d].horarios:
            for s in salas:
                if s not in disciplinas[d].salasPreferenciais:
                    vet_salas_preferenciais.append(x[d,s,h])

    # Funcao obj
    m.setObjective(gp.quicksum(y[d,s] for d in disciplinas for s in salas) +
                gp.quicksum(vet_salas_preferenciais),
    sense=gp.GRB.MINIMIZE
    )


    # Restricoes

    # No máximo uma disciplina (turma) pode ser alocada a uma sala em um determinado horário:
    c1 = m.addConstrs(
        gp.quicksum(x[d, s, h] for d in disciplinas if h in disciplinas[d].horarios) <= 1
        for s in salas for h in horarios
    )

    # No máximo uma sala pode ser alocada a uma disciplina em um determinado horário
    c2 = m.addConstrs( 
        gp.quicksum(x[d,s,h] for s in salas ) <= 1 for d in disciplinas for h in disciplinas[d].horarios
    )

    # No mínimo uma sala deve ser alocada a uma disciplina em um determinado horário
    c3 = m.addConstrs( 
        gp.quicksum(x[d,s,h] for s in salas ) >= 1 for d in disciplinas for h in disciplinas[d].horarios
    )

    # Uma sala não pode ser alocada a uma disciplina cujo número de alunos ultrapasse a sua capacidade:
    c4 = m.addConstrs(
        x[d,s,h] * disciplinas[d].alunos <= salas[s].capacidade for d in disciplinas for s in salas for h in disciplinas[d].horarios)


    # Uma sala é alocada a uma disciplina se a sala é alocada à disciplina em algum horário:
    c5 = m.addConstrs(
        y[d,s] >= x[d,s,h] for d in disciplinas for s in salas for h in disciplinas[d].horarios)

    m.optimize()

    if m.status == gp.GRB.OPTIMAL:
        print("Solução ótima encontrada.")
        #cria_csv(disciplinas,salas,horarios,x)
        exporta_alocacoes(disciplinas,salas,horarios,x)
    else:
        print("O modelo é inviável.")

main()