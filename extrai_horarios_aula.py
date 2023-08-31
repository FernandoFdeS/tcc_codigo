import pandas as pd
import re
from Disciplina import Disciplina
from Horario import Horario

# Salas preferenciais por curso
salas_preferenciais = dict()
salas_preferenciais["MEDICINA"]=["302-A","303-A","304-A"]
salas_preferenciais["CIÊNCIA DA COMPUTAÇÃO"]=["308-B","309-B","310-B"]

# Cria horarios
horarios_fixos = dict()
for i in range(6):
    for j in range(16):
        horarios_fixos["Horario_"+(str(i+2))+"_"+(str(j+1))]=(Horario(i+2,j+1))

# Pega os horarios das aulas
dados = pd.read_excel("./dados/horarios.xlsx", header=None)
nomes_cursos = dados.iloc[:, 0]
horarios_disciplina = dados.iloc[:, 1]
horarios = ""
cod_aula= ""
n_turma = ""
padrao = r"(\d+)([A-Za-z]+)(\d+)"
padrao_n_turma = r"Turma:(\d+)"
periodo_map = dict()
periodo_map["M"]=0
periodo_map["T"]=6
periodo_map["N"]=12

disciplinas = dict()

for nome_curso, horario_disciplina in zip(nomes_cursos,horarios_disciplina):
    print(nome_curso.split)
    cod_aula = horario_disciplina.split("-")
    cod_aula = cod_aula[0]
    cod_aula = cod_aula[:-1]
    turma = re.search(padrao_n_turma,horario_disciplina)
    n_turma = turma.group(1)
    horarios = horario_disciplina.split("/")
    horarios = horarios[0].split("-")
    horarios = horarios[-1].split(":")
    horarios = horarios[1]
    horarios = horarios[:-3]
    horarios = horarios.split()
    print(cod_aula+"_"+n_turma)
    horario_aula=dict()
    for horario in horarios:
        dias=""
        periodo=""
        faixas=""
        resultado = re.match(padrao,horario)
        dias=resultado.group(1)
        periodos=resultado.group(2)
        faixas=resultado.group(3)

        for dia in dias:
            for periodo in periodos:
                for faixa in faixas:
                    dia_horario= int(dia)
                    faixa_horario = (int(periodo_map[periodo]))+int(faixa)
                    horario_aula["Horario_{}_{}".format(dia_horario,faixa_horario)]=Horario(dia_horario,faixa_horario)
        
    sp = []
    if nome_curso in salas_preferenciais:
        sp = salas_preferenciais[nome_curso]

    disciplina = Disciplina(nome_curso,25,horario_aula,sp) # não tem o tamanho da turma nos horários
    disciplinas[cod_aula+"_"+n_turma]=disciplina

# for d in disciplinas:
#     print(disciplinas[d].curso,d,disciplinas[d].salasPreferenciais)
#     for h in disciplinas[d].horarios:
#         print(h)
