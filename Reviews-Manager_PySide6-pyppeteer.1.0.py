import os
import sys
import asyncio
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QComboBox, QPushButton, QCalendarWidget,
                               QMessageBox, QFileDialog, QTextBrowser)
from PySide6.QtCore import QDate, QSize
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from PySide6.QtGui import QFont
from PySide6 import QtGui
from pyppeteer import launch
from qasync import QEventLoop


database_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banco_dados.db")
conn = QSqlDatabase.addDatabase("QSQLITE")
conn.setDatabaseName(database_path)

if not conn.open():
    print("Não foi possível abrir o banco de dados.")
    sys.exit(1)

query = QSqlQuery()
query.exec("CREATE TABLE IF NOT EXISTS atividades (disciplina TEXT, codigo TEXT, tipo TEXT, sequencia TEXT, data TEXT)")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loop = QEventLoop()
        asyncio.set_event_loop(self.loop)

        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        # Adicione a pasta "icones" ao caminho base
        icon_path = os.path.join(base_path, "icones")

        self.setWindowTitle("Cadastro de Atividades Avaliativas")
        icon_title_path = os.path.join(icon_path, "ReviewsManager.ico")
        self.setWindowIcon(QtGui.QIcon(icon_title_path))
        self.resize(900, 625)

        self.query = QSqlQuery()

        self.create_widgets()
        self.update_ementa()
        self.update_semestre()
        self.update_disciplinas()
        self.update_textbox()

    def create_widgets(self):
        self.label_curso = QLabel("Curso:", self)
        self.label_curso.setGeometry(10, 10, 270, 20)

        self.combo_curso = QComboBox(self)
        self.combo_curso.setGeometry(10, 30, 270, 20)
        self.combo_curso.addItems(["", "Engenharia Civil", "Engenharia de Computação", "Engenharia Elétrica"])
        self.combo_curso.currentIndexChanged.connect(self.update_ementa)

        self.label_ementa = QLabel("Ementa do Curso:", self)
        self.label_ementa.setGeometry(10, 55, 270, 20)

        self.entry_ementa = QComboBox(self)
        self.entry_ementa.setGeometry(10, 75, 270, 20)
        self.entry_ementa.currentIndexChanged.connect(self.update_semestre)

        self.label_semestre = QLabel("Selecione o Semestre:", self)
        self.label_semestre.setGeometry(10, 100, 270, 20)

        self.entry_semestre = QComboBox(self)
        self.entry_semestre.setGeometry(10, 120, 270, 20)
        self.entry_semestre.currentIndexChanged.connect(self.update_disciplinas)

        self.label_disciplina = QLabel("Nome da Disciplina:", self)
        self.label_disciplina.setGeometry(10, 145, 270, 20)

        self.entry_disciplina = QComboBox(self)
        self.entry_disciplina.setGeometry(10, 165, 270, 20)

        self.label_codigo = QLabel("Turma da Disciplina:", self)
        self.label_codigo.setGeometry(10, 190, 270, 20)

        self.entry_codigo = QComboBox(self)
        self.entry_codigo.setGeometry(10, 210, 270, 20)
        self.entry_codigo.addItems(["", "Turma A", "Turma B", "Turma C", "Turma D", "Turma E", "Turma F", "Turma G",
                                    "Turma H", "Turma I", "Turma J", "Turma K", "Turma L", "Turma M", "Turma N",
                                    "Turma O", "Turma P", "Turma Q", "Turma R", "Turma S", "Turma T", "Turma U",
                                    "Turma V", "Turma W", "Turma X", "Turma Y", "Turma Z"])

        self.label_tipo = QLabel("Tipo de Atividade Avaliativa:", self)
        self.label_tipo.setGeometry(10, 235, 270, 20)

        self.combo_tipo = QComboBox(self)
        self.combo_tipo.setGeometry(10, 255, 270, 20)
        self.combo_tipo.addItems(["", "PROVA", "TESTE", "2ª CHAMADA", "EXAME FINAL", "TRABALHO", "RELATÓRIO",
                                  "LISTA DE EXERCÍCIOS", "EXERCÍCIO", "APRESENTAÇÃO ORAL", "SEMINÁRIO", "KAHOOT",
                                  "ROCKBOWL", "APRENDIZADO BASEADO EM PROBLEMAS - PBL", "APRENDIZADO BASEADO EM PROJETOS - ABP",
                                  "APRENDIZADO BASEADO EM INQUÉRITO - IBL"])

        self.label_sequencia = QLabel("Sequência da Atividade:", self)
        self.label_sequencia.setGeometry(10, 280, 270, 20)

        self.combo_sequencia = QComboBox(self)
        self.combo_sequencia.setGeometry(10, 300, 270, 20)
        self.combo_sequencia.addItems([""] + [str(i) for i in range(1, 11)])

        self.label_data = QLabel("Defina a Data da Atividade:", self)
        self.label_data.setGeometry(10, 325, 270, 20)

        self.calendar = QCalendarWidget(self)
        self.calendar.setGeometry(10, 345, 270, 200)

        self.button_submit = QPushButton("Registrar Definições", self)
        self.button_submit.setGeometry(10, 550, 270, 30)
        self.button_submit.clicked.connect(self.submit)

        self.label_banco_dados = QLabel("Banco de Dados (Permitido Editar os Dados Abaixo):", self)
        self.label_banco_dados.setGeometry(290, 10, 300, 20)

        self.textbox = QTextBrowser(self)
        self.textbox.setGeometry(290, 30, 600, 590)
        self.textbox.setReadOnly(False)

        self.button_clear = QPushButton("Limpar Tudo", self)
        self.button_clear.setGeometry(10, 585, 110, 30)
        self.button_clear.clicked.connect(self.clear_entries)

        self.button_export = QPushButton("Exportar para PDF", self)
        self.button_export.setGeometry(170, 585, 110, 30)
        self.button_export.clicked.connect(self.export_to_pdf)

        self.update_textbox()

    def resizeEvent(self, event):
        new_size = QSize(event.size())
        self.textbox.setGeometry(290, 30, new_size.width() - 300, new_size.height() - 40)

    def update_ementa(self):
        selected_curso = self.combo_curso.currentText()
        ementas = {
            "Engenharia Civil": [
                "",
                "Ementa - 2011",
                "Ementa - 2023"
            ],
            "Engenharia de Computação": [
                "",
                "Ementa - 2015",
                "Ementa - 2021"
            ],
            "Engenharia Elétrica": [
                "",
                "Ementa - 2013",
                "Ementa - 2019"
            ]
        }.get(selected_curso, [])
        self.entry_ementa.clear()
        self.entry_ementa.addItems(ementas)

    def update_semestre(self):
        selected_ementa = self.entry_ementa.currentText()
        semestres = {
            "Ementa - 2011": [
                "",
                "1º Semestre",
                "2º Semestre",
                "3º Semestre",
                "4º Semestre",
                "5º Semestre",
                "6º Semestre",
                "7º Semestre",
                "8º Semestre",
                "9º Semestre",
                "10º Semestre",
                "Optativas (mínimo 6)"
            ],
            "Ementa - 2023": [
                "",
                "1º Semestre",
                "2º Semestre",
                "3º Semestre",
                "4º Semestre",
                "5º Semestre",
                "6º Semestre",
                "7º Semestre",
                "8º Semestre",
                "9º Semestre",
                "10º Semestre",
                "Optativas (mínimo 6)"
            ],
            "Ementa - 2015": [
                "",
                "1º Semestre",
                "2º Semestre",
                "3º Semestre",
                "4º Semestre",
                "5º Semestre",
                "6º Semestre",
                "7º Semestre",
                "8º Semestre",
                "9º Semestre",
                "10º Semestre",
                "Optativas (mínimo 6)"
            ],
            "Ementa - 2021": [
                "",
                "1º Semestre",
                "2º Semestre",
                "3º Semestre",
                "4º Semestre",
                "5º Semestre",
                "6º Semestre",
                "7º Semestre",
                "8º Semestre",
                "9º Semestre",
                "10º Semestre",
                "Optativas (mínimo 6)"
            ],
            "Ementa - 2013": [
                "",
                "1º Semestre",
                "2º Semestre",
                "3º Semestre",
                "4º Semestre",
                "5º Semestre",
                "6º Semestre",
                "7º Semestre",
                "8º Semestre",
                "9º Semestre",
                "10º Semestre",
                "Optativas (mínimo 6)"
            ],
            "Ementa - 2019": [
                "",
                "1º Semestre",
                "2º Semestre",
                "3º Semestre",
                "4º Semestre",
                "5º Semestre",
                "6º Semestre",
                "7º Semestre",
                "8º Semestre",
                "9º Semestre",
                "10º Semestre",
                "Optativas (mínimo 6)"
            ]
        }.get(selected_ementa, [])
        self.entry_semestre.clear()
        self.entry_semestre.addItems(semestres)

    def update_disciplinas(self):
        selected_curso = self.combo_curso.currentText()
        self.entry_disciplina.clear()

        if selected_curso == "Engenharia Civil":
            selected_ementa = self.entry_ementa.currentText()

            if selected_ementa == "Ementa - 2011":
                selected_semestre = self.entry_semestre.currentText()
                disciplinas = {
                    "1º Semestre": [
                        "",
                        "Cálculo Diferencial e Integral I – CM201",
                        "Eletricidade Aplicada – TE144",
                        "Expressão Gráfica I – CD027",
                        "Geometria Analítica – CM045",
                        "Introdução à Engenharia – TC022",
                        "Mecânica Geral I – TC021",
                        "Programação de Computadores – CI208"
                    ],
                    "2º Semestre": [
                        "",
                        "Álgebra Linear – CM005",
                        "Cálculo Diferencial e Integral II – CM202",
                        "Construção Civil I – TC024",
                        "Expressão Gráfica II – CD028",
                        "Mecânica Geral II – TC023",
                        "Métodos Numéricos – CI202"
                    ],
                    "3º Semestre": [
                        "",
                        "Cálculo III – CM043",
                        "Construção Civil II – TC025",
                        "Estatística II – CE003",
                        "Mecânica dos Fluidos I – TH019",
                        "Mecânica Geral III – TC027",
                        "Resistência dos Materiais I – TC026",
                        "Topografia I – GA069"
                    ],
                    "4º Semestre": [
                        "",
                        "Introdução à Engenharia Geotécnica – TC029",
                        "Ciências do Ambiente – TH022",
                        "Materiais de Construção Civil I – TC030",
                        "Mecânica dos Fluidos II – TH021",
                        "Resistência dos Materiais II – TC028",
                        "Sistemas de Transporte – TT046",
                        "Topografia II – GA070"
                    ],
                    "5º Semestre": [
                        "",
                        "Estruturação Sanitária das Cidades – TH025",
                        "Hidráulica – TH020",
                        "Infra-Estrutura Viária – TT048",
                        "Laboratório de Mecânica dos Solos – TC033",
                        "Materiais de Construção Civil II – TC031",
                        "Mecânica das Estruturas I – TC032"
                    ],
                    "6º Semestre": [
                        "",
                        "Atividades Formativas – AAC005",
                        "Equipamentos de Construção e Conservação – TT047",
                        "Hidráulica e Hidrologia Experimental – TH027",
                        "Hidrologia – TH024",
                        "Materiais de Construção Civil III – TC034",
                        "Mecânica das Estruturas II – TC036",
                        "Mecânica dos Solos – TC035"
                    ],
                    "7º Semestre": [
                        "",
                        "Construção Civil III – TC038",
                        "Engenharia de Recursos Hídricos – TH026",
                        "Engenharia Social – TH045",
                        "Estruturas de Concreto I – TC037",
                        "Laboratório de Materiais de Construção – TC039",
                        "Obras Geotécnicas – TC066",
                        "Planejamento de Transportes – TT049",
                        "Saneamento Ambiental I – TH028"
                    ],
                    "8º Semestre": [
                        "",
                        "Construção Civil IV – TC042",
                        "Economia de Engenharia I – TT007",
                        "Estágio Supervisionado – TC046",
                        "Estágio Supervisionado – TH043",
                        "Estágio Supervisionado – TT054",
                        "Estruturas de Concreto II – TC040",
                        "Geotecnia de Fundações – TC041",
                        "Pavimentação – TT051",
                        "Saneamento Ambiental II – TH029"
                    ],
                    "9º Semestre": [
                        "",
                        "Administração de Empresas de Engenharia I – TT008",
                        "Estrutura de Edifícios I – TC044",
                        "Estruturas Metálicas I – TC043",
                        "Gerenciamento de Projetos – TC045",
                        "Sistemas Prediais, Hidráulicos e Sanitários – TH030",
                        "Trabalho Final de Curso I – TC081",
                        "Trabalho Final de Curso I – TH061",
                        "Trabalho Final de Curso I – TT071"
                    ],
                    "10º Semestre": [
                        "",
                        "Trabalho Final de Curso II – TC082",
                        "Trabalho Final de Curso II – TH062",
                        "Trabalho Final de Curso II – TT072"
                    ],
                    "Optativas (mínimo 6)": [
                        "",
                        "Avaliação de Impactos Ambientais – TT059",
                        "Engenharia de Avaliações – TC064",
                        "Engenharia de Tráfego – TT056",
                        "Engenharia Econômica de Recursos Hídricos – TH035",
                        "Estruturas de Concreto III – TC054",
                        "Estruturas de Edifícios II – TC056",
                        "Estruturas de Madeira – TC057",
                        "Estruturas Metálicas II – TC055",
                        "Expressão Gráfica III – CD035",
                        "Ferrovias – TT066",
                        "Geologia de Engenharia – TC049",
                        "Geotecnia Ambiental – TC053",
                        "Geotecnia Aplicada as Vias de Transporte – TT065",
                        "Geotecnia de Taludes e Contenções – TC052",
                        "Gerenciamento de Empreendimentos – TC062",
                        "Gerenciamento de Recursos Hídricos – TH036",
                        "Gerenciamento de Rodovias e Vias Urbanas – TT063",
                        "Hidráulica Ambiental – TH033",
                        "Hidráulica Fluvial – TH032",
                        "Instalações Prediais Especiais – TC065",
                        "Introdução a Engenharia de Segurança do Trabalho – TT068",
                        "Legislação e Prática Profissional – TC061",
                        "Logística e Transporte – TT058",
                        "Mecânica das Rochas – TC051",
                        "Método dos Elementos Finitos Aplicados a Engenharia de Estruturas – TC059",
                        "Modelagem e Planejamento de Transportes Urbanos – TT060",
                        "Planejamento e Gestão dos Sistemas Urbanos – TH042",
                        "Pontes e Estruturas Especiais – TC058",
                        "Portos e Hidrovias – TT067",
                        "Projeto de Obras Viárias – TT064",
                        "Projetos de Arquitetura – TC060",
                        "Projetos de Drenagem Urbana – TH037",
                        "Projetos de Obras Hidráulicas – TH031",
                        "Projetos de Obras Viárias – TT064",
                        "Projetos de Sistemas de Resíduos Sólidos Urbanos – TH038",
                        "Projetos de Sistemas de Saneamento Ambiental – TH039",
                        "Projetos de Sistemas Prediais Hidráulicos Sanitários – TH040",
                        "Qualidade e Conservação Ambiental – TH041",
                        "Segurança Viária – TT061",
                        "Sistemas de Recursos Hídricos – TH034",
                        "Técnica de Investigação Geotécnica e Instrumentação – TC050",
                        "Tópicos Avançados de Pavimentação – TT062",
                        "Tópicos Avançados em Geotecnia – TC048",
                        "Transporte Público – TT057"
                    ]
                }.get(selected_semestre, [])
                self.entry_disciplina.clear()
                self.entry_disciplina.addItems(disciplinas)

            elif selected_ementa == "Ementa - 2023":
                selected_semestre = self.entry_semestre.currentText()
                disciplinas = {
                    "1º Semestre": [
                        "",
                        "Expressão Gráfica A – CEG019",
                        "Fundamentação de Programação de Computadores – CI182",
                        "Pré-Cálculo – CM310",
                        "Física I – TC501",
                        "Química Aplicada – TC502",
                        "Introdução à Engenharia e Inovação – TC591",
                        "Introdução à Engenharia e Inovação – TH591",
                        "Introdução à Engenharia e Inovação – TT591"
                    ],
                    "2º Semestre": [
                        "",
                        "Métodos Numéricos – CI202",
                        "Introdução à Geometria Analítica e Álgebra Linear – CM303",
                        "Cálculo 1 – CM311",
                        "Desenho Arquitetônico – TC503",
                        "Análise Estrutural I – TC504",
                        "Física II – TH512"
                    ],
                    "3º Semestre": [
                        "",
                        "Introdução à Estatística – CE009",
                        "Cálculo 2 – CM312",
                        "Topografia I – GA175",
                        "Construção Civil I – TC505",
                        "Análise Estrutural II – TC506",
                        "Sistemas Estruturais – TC507",
                        "Mecânica dos Fluídos I – TH501",
                        "Sistemas de Transporte – TT501"
                    ],
                    "4º Semestre": [
                        "",
                        "Cálculo 4 – CM314",
                        "Topografia II – GA176",
                        "Construção Civil II – TC508",
                        "Mecânica dos Sólidos I – TC509",
                        "Materiais de Construção Civil I – TC510",
                        "Laboratório de Materiais de Construção Civil – TC511",
                        "Mecânica dos Fluídos II – TH502",
                        "Mecânica dos Fluídos Experimental – TH503"
                    ],
                    "5º Semestre": [
                        "",
                        "Caracterização Geológica - Geotécnica – TC512",
                        "Mecânica dos Sólidos II – TC513",
                        "Materiais de Construção Civil II – TC514",
                        "Hidráulica – TH504",
                        "Ciências do Ambiente – TH508",
                        "Planejamento e Operação de Transportes – TT502",
                        "Engenharia Civil e Sustentabilidade – TC592",
                        "Engenharia Civil e Sustentabilidade – TH592",
                        "Engenharia Civil e Sustentabilidade – TT592",
                    ],
                    "6º Semestre": [
                        "",
                        "Hidráulica dos Solos – TC515",
                        "Análise Estrutural III – TC516",
                        "Construção Civil III – TC517",
                        "Hidrologia – TH505",
                        "Hidráulica e Hidrologia Experimental – TH506",
                        "Equipamentos de Terraplanagem e de Pavimentação – TT503",
                        "Estruturação das Cidades – TH593",
                        "Estruturação das Cidades – TT593"
                    ],
                    "7º Semestre": [
                        "",
                        "Mecânica dos Solos – TC518",
                        "Estruturas de Concreto I – TC519",
                        "Gestão de Projetos – TC520",
                        "Engenharia de Recursos Hídricos – TH507",
                        "Saneamento Ambiental I – TH509",
                        "Engenharia Econômica – TT504",
                        "Engenharia Urbana – TH594",
                        "Engenharia Urbana – TT594"
                    ],
                    "8º Semestre": [
                        "",
                        "Obras Geotécnicas – TC521",
                        "Estruturas de Concreto II – TC522",
                        "Saneamento Ambiental II – TH510",
                        "Estradas – TT505",
                        "Pavimentação – TT506",
                        "Laboratório de Transportes – TT507",
                        "Economia de Engenharia – TT508",
                        "Metodologia do Trabalho Científico e Tecnológico – TT509"
                    ],
                    "9º Semestre": [
                        "",
                        "Estruturas de Aço – TC523",
                        "Estruturas de Madeira – TC524",
                        "Engenharia de Fundações – TC525",
                        "Eletricidade Aplicada – TE144",
                        "Engenharia e Sociedade – TH511",
                        "Administração de Empresas – TT510",
                        "Trabalho Final de Curso I – TC581",
                        "Trabalho Final de Curso I – TH581",
                        "Trabalho Final de Curso I – TT581",
                        "Projeto de Infraestrutura e Obras Especiais – TC595",
                        "Projeto de Infraestrutura e Obras Especiais – TH595",
                        "Projeto de Infraestrutura e Obras Especiais – TT595"
                    ],
                    "10º Semestre": [
                        "",
                        "Trabalho Final de Curso II – TC582",
                        "Trabalho Final de Curso II – TH582",
                        "Trabalho Final de Curso II – TT582",
                        "Trabalho Final de Curso II – TC583",
                        "Trabalho Final de Curso II – TH583",
                        "Trabalho Final de Curso II – TT583",
                        "Estágio Supervisionado Obrigatório – TC585",
                        "Estágio Supervisionado Obrigatório – TH585",
                        "Estágio Supervisionado Obrigatório – TT585",
                        "Projetos de Edifícios – TC596",
                        "Projetos de Edifícios – TH596",
                    ],
                    "Optativas (mínimo 6)": [
                        "",
                        "Avaliação de Impactos Ambientais – TT059",
                        "Engenharia de Avaliações – TC064",
                        "Engenharia de Tráfego – TT056",
                        "Engenharia Econômica de Recursos Hídricos – TH035",
                        "Estruturas de Concreto III – TC054",
                        "Estruturas de Edifícios II – TC056",
                        "Estruturas de Madeira – TC057",
                        "Estruturas Metálicas II – TC055",
                        "Expressão Gráfica III – CD035",
                        "Ferrovias – TT066",
                        "Geologia de Engenharia – TC049",
                        "Geotecnia Ambiental – TC053",
                        "Geotecnia Aplicada as Vias de Transporte – TT065",
                        "Geotecnia de Taludes e Contenções – TC052",
                        "Gerenciamento de Empreendimentos – TC062",
                        "Gerenciamento de Recursos Hídricos – TH036",
                        "Gerenciamento de Rodovias e Vias Urbanas – TT063",
                        "Hidráulica Ambiental – TH033",
                        "Hidráulica Fluvial – TH032",
                        "Instalações Prediais Especiais – TC065",
                        "Introdução a Engenharia de Segurança do Trabalho – TT068",
                        "Legislação e Prática Profissional – TC061",
                        "Logística e Transporte – TT058",
                        "Mecânica das Rochas – TC051",
                        "Método dos Elementos Finitos Aplicados a Engenharia de Estruturas – TC059",
                        "Modelagem e Planejamento de Transportes Urbanos – TT060",
                        "Planejamento e Gestão dos Sistemas Urbanos – TH042",
                        "Pontes e Estruturas Especiais – TC058",
                        "Portos e Hidrovias – TT067",
                        "Projeto de Obras Viárias – TT064",
                        "Projetos de Arquitetura – TC060",
                        "Projetos de Drenagem Urbana – TH037",
                        "Projetos de Obras Hidráulicas – TH031",
                        "Projetos de Obras Viárias – TT064",
                        "Projetos de Sistemas de Resíduos Sólidos Urbanos – TH038",
                        "Projetos de Sistemas de Saneamento Ambiental – TH039",
                        "Projetos de Sistemas Prediais Hidráulicos Sanitários – TH040",
                        "Qualidade e Conservação Ambiental – TH041",
                        "Segurança Viária – TT061",
                        "Sistemas de Recursos Hídricos – TH034",
                        "Técnica de Investigação Geotécnica e Instrumentação – TC050",
                        "Tópicos Avançados de Pavimentação – TT062",
                        "Tópicos Avançados em Geotecnia – TC048",
                        "Transporte Público – TT057"
                    ]
                }.get(selected_semestre, [])
                self.entry_disciplina.clear()
                self.entry_disciplina.addItems(disciplinas)

        elif selected_curso == "Engenharia de Computação":
            selected_ementa = self.entry_ementa.currentText()

            if selected_ementa == "Ementa - 2015":
                selected_semestre = self.entry_semestre.currentText()
                disciplinas = {
                    "1º Semestre": [
                        "",
                        "Cálculo Diferencial e Integral I – CM201",
                        "Eletricidade Aplicada – TE144",
                        "Expressão Gráfica I – CD027",
                        "Geometria Analítica – CM045",
                        "Introdução à Engenharia – TC022",
                        "Mecânica Geral I – TC021",
                        "Programação de Computadores – CI208"
                    ],
                    "2º Semestre": [
                        "",
                        "Álgebra Linear – CM005",
                        "Cálculo Diferencial e Integral II – CM202",
                        "Construção Civil I – TC024",
                        "Expressão Gráfica II – CD028",
                        "Mecânica Geral II – TC023",
                        "Métodos Numéricos – CI202"
                    ],
                    "3º Semestre": [
                        "",
                        "Cálculo III – CM043",
                        "Construção Civil II – TC025",
                        "Estatística II – CE003",
                        "Mecânica dos Fluidos I – TH019",
                        "Mecânica Geral III – TC027",
                        "Resistência dos Materiais I – TC026",
                        "Topografia I – GA069"
                    ],
                    "4º Semestre": [
                        "",
                        "Introdução à Engenharia Geotécnica – TC029",
                        "Ciências do Ambiente – TH022",
                        "Materiais de Construção Civil I – TC030",
                        "Mecânica dos Fluidos II – TH021",
                        "Resistência dos Materiais II – TC028",
                        "Sistemas de Transporte – TT046",
                        "Topografia II – GA070"
                    ],
                    "5º Semestre": [
                        "",
                        "Estruturação Sanitária das Cidades – TH025",
                        "Hidráulica – TH020",
                        "Infra-Estrutura Viária – TT048",
                        "Laboratório de Mecânica dos Solos – TC033",
                        "Materiais de Construção Civil II – TC031",
                        "Mecânica das Estruturas I – TC032"
                    ],
                    "6º Semestre": [
                        "",
                        "Atividades Formativas – AAC005",
                        "Equipamentos de Construção e Conservação – TT047",
                        "Hidráulica e Hidrologia Experimental – TH027",
                        "Hidrologia – TH024",
                        "Materiais de Construção Civil III – TC034",
                        "Mecânica das Estruturas II – TC036",
                        "Mecânica dos Solos – TC035"
                    ],
                    "7º Semestre": [
                        "",
                        "Construção Civil III – TC038",
                        "Engenharia de Recursos Hídricos – TH026",
                        "Engenharia Social – TH045",
                        "Estruturas de Concreto I – TC037",
                        "Laboratório de Materiais de Construção – TC039",
                        "Obras Geotécnicas – TC066",
                        "Planejamento de Transportes – TT049",
                        "Saneamento Ambiental I – TH028"
                    ],
                    "8º Semestre": [
                        "",
                        "Construção Civil IV – TC042",
                        "Economia de Engenharia I – TT007",
                        "Estágio Supervisionado – TC046",
                        "Estágio Supervisionado – TH043",
                        "Estágio Supervisionado – TT054",
                        "Estruturas de Concreto II – TC040",
                        "Geotecnia de Fundações – TC041",
                        "Pavimentação – TT051",
                        "Saneamento Ambiental II – TH029"
                    ],
                    "9º Semestre": [
                        "",
                        "Administração de Empresas de Engenharia I – TT008",
                        "Estrutura de Edifícios I – TC044",
                        "Estruturas Metálicas I – TC043",
                        "Gerenciamento de Projetos – TC045",
                        "Sistemas Prediais, Hidráulicos e Sanitários – TH030",
                        "Trabalho Final de Curso I – TC081",
                        "Trabalho Final de Curso I – TH061",
                        "Trabalho Final de Curso I – TT071"
                    ],
                    "10º Semestre": [
                        "",
                        "Trabalho Final de Curso II – TC082",
                        "Trabalho Final de Curso II – TH062",
                        "Trabalho Final de Curso II – TT072"
                    ],
                    "Optativas (mínimo 6)": [
                        "",
                        "Avaliação de Impactos Ambientais – TT059",
                        "Engenharia de Avaliações – TC064",
                        "Engenharia de Tráfego – TT056",
                        "Engenharia Econômica de Recursos Hídricos – TH035",
                        "Estruturas de Concreto III – TC054",
                        "Estruturas de Edifícios II – TC056",
                        "Estruturas de Madeira – TC057",
                        "Estruturas Metálicas II – TC055",
                        "Expressão Gráfica III – CD035",
                        "Ferrovias – TT066",
                        "Geologia de Engenharia – TC049",
                        "Geotecnia Ambiental – TC053",
                        "Geotecnia Aplicada as Vias de Transporte – TT065",
                        "Geotecnia de Taludes e Contenções – TC052",
                        "Gerenciamento de Empreendimentos – TC062",
                        "Gerenciamento de Recursos Hídricos – TH036",
                        "Gerenciamento de Rodovias e Vias Urbanas – TT063",
                        "Hidráulica Ambiental – TH033",
                        "Hidráulica Fluvial – TH032",
                        "Instalações Prediais Especiais – TC065",
                        "Introdução a Engenharia de Segurança do Trabalho – TT068",
                        "Legislação e Prática Profissional – TC061",
                        "Logística e Transporte – TT058",
                        "Mecânica das Rochas – TC051",
                        "Método dos Elementos Finitos Aplicados a Engenharia de Estruturas – TC059",
                        "Modelagem e Planejamento de Transportes Urbanos – TT060",
                        "Planejamento e Gestão dos Sistemas Urbanos – TH042",
                        "Pontes e Estruturas Especiais – TC058",
                        "Portos e Hidrovias – TT067",
                        "Projeto de Obras Viárias – TT064",
                        "Projetos de Arquitetura – TC060",
                        "Projetos de Drenagem Urbana – TH037",
                        "Projetos de Obras Hidráulicas – TH031",
                        "Projetos de Obras Viárias – TT064",
                        "Projetos de Sistemas de Resíduos Sólidos Urbanos – TH038",
                        "Projetos de Sistemas de Saneamento Ambiental – TH039",
                        "Projetos de Sistemas Prediais Hidráulicos Sanitários – TH040",
                        "Qualidade e Conservação Ambiental – TH041",
                        "Segurança Viária – TT061",
                        "Sistemas de Recursos Hídricos – TH034",
                        "Técnica de Investigação Geotécnica e Instrumentação – TC050",
                        "Tópicos Avançados de Pavimentação – TT062",
                        "Tópicos Avançados em Geotecnia – TC048",
                        "Transporte Público – TT057"
                    ]
                }.get(selected_semestre, [])
                self.entry_disciplina.clear()
                self.entry_disciplina.addItems(disciplinas)

            elif selected_ementa == "Ementa - 2021":
                selected_semestre = self.entry_semestre.currentText()
                disciplinas = {
                    "1º Semestre": [
                        "",
                        "Expressão Gráfica A – CEG019",
                        "Fundamentação de Programação de Computadores – CI182",
                        "Pré-Cálculo – CM310",
                        "Física I – TC501",
                        "Química Aplicada – TC502",
                        "Introdução à Engenharia e Inovação – TC591",
                        "Introdução à Engenharia e Inovação – TH591",
                        "Introdução à Engenharia e Inovação – TT591"
                    ],
                    "2º Semestre": [
                        "",
                        "Métodos Numéricos – CI202",
                        "Introdução à Geometria Analítica e Álgebra Linear – CM303",
                        "Cálculo 1 – CM311",
                        "Desenho Arquitetônico – TC503",
                        "Análise Estrutural I – TC504",
                        "Física II – TH512"
                    ],
                    "3º Semestre": [
                        "",
                        "Introdução à Estatística – CE009",
                        "Cálculo 2 – CM312",
                        "Topografia I – GA175",
                        "Construção Civil I – TC505",
                        "Análise Estrutural II – TC506",
                        "Sistemas Estruturais – TC507",
                        "Mecânica dos Fluídos I – TH501",
                        "Sistemas de Transporte – TT501"
                    ],
                    "4º Semestre": [
                        "",
                        "Cálculo 4 – CM314",
                        "Topografia II – GA176",
                        "Construção Civil II – TC508",
                        "Mecânica dos Sólidos I – TC509",
                        "Materiais de Construção Civil I – TC510",
                        "Laboratório de Materiais de Construção Civil – TC511",
                        "Mecânica dos Fluídos II – TH502",
                        "Mecânica dos Fluídos Experimental – TH503"
                    ],
                    "5º Semestre": [
                        "",
                        "Caracterização Geológica - Geotécnica – TC512",
                        "Mecânica dos Sólidos II – TC513",
                        "Materiais de Construção Civil II – TC514",
                        "Hidráulica – TH504",
                        "Ciências do Ambiente – TH508",
                        "Planejamento e Operação de Transportes – TT502",
                        "Engenharia Civil e Sustentabilidade – TC592",
                        "Engenharia Civil e Sustentabilidade – TH592",
                        "Engenharia Civil e Sustentabilidade – TT592",
                    ],
                    "6º Semestre": [
                        "",
                        "Hidráulica dos Solos – TC515",
                        "Análise Estrutural III – TC516",
                        "Construção Civil III – TC517",
                        "Hidrologia – TH505",
                        "Hidráulica e Hidrologia Experimental – TH506",
                        "Equipamentos de Terraplanagem e de Pavimentação – TT503",
                        "Estruturação das Cidades – TH593",
                        "Estruturação das Cidades – TT593"
                    ],
                    "7º Semestre": [
                        "",
                        "Mecânica dos Solos – TC518",
                        "Estruturas de Concreto I – TC519",
                        "Gestão de Projetos – TC520",
                        "Engenharia de Recursos Hídricos – TH507",
                        "Saneamento Ambiental I – TH509",
                        "Engenharia Econômica – TT504",
                        "Engenharia Urbana – TH594",
                        "Engenharia Urbana – TT594"
                    ],
                    "8º Semestre": [
                        "",
                        "Obras Geotécnicas – TC521",
                        "Estruturas de Concreto II – TC522",
                        "Saneamento Ambiental II – TH510",
                        "Estradas – TT505",
                        "Pavimentação – TT506",
                        "Laboratório de Transportes – TT507",
                        "Economia de Engenharia – TT508",
                        "Metodologia do Trabalho Científico e Tecnológico – TT509"
                    ],
                    "9º Semestre": [
                        "",
                        "Estruturas de Aço – TC523",
                        "Estruturas de Madeira – TC524",
                        "Engenharia de Fundações – TC525",
                        "Eletricidade Aplicada – TE144",
                        "Engenharia e Sociedade – TH511",
                        "Administração de Empresas – TT510",
                        "Trabalho Final de Curso I – TC581",
                        "Trabalho Final de Curso I – TH581",
                        "Trabalho Final de Curso I – TT581",
                        "Projeto de Infraestrutura e Obras Especiais – TC595",
                        "Projeto de Infraestrutura e Obras Especiais – TH595",
                        "Projeto de Infraestrutura e Obras Especiais – TT595"
                    ],
                    "10º Semestre": [
                        "",
                        "Trabalho Final de Curso II – TC582",
                        "Trabalho Final de Curso II – TH582",
                        "Trabalho Final de Curso II – TT582",
                        "Trabalho Final de Curso II – TC583",
                        "Trabalho Final de Curso II – TH583",
                        "Trabalho Final de Curso II – TT583",
                        "Estágio Supervisionado Obrigatório – TC585",
                        "Estágio Supervisionado Obrigatório – TH585",
                        "Estágio Supervisionado Obrigatório – TT585",
                        "Projetos de Edifícios – TC596",
                        "Projetos de Edifícios – TH596",
                    ],
                    "Optativas (mínimo 6)": [
                        "",
                        "Avaliação de Impactos Ambientais – TT059",
                        "Engenharia de Avaliações – TC064",
                        "Engenharia de Tráfego – TT056",
                        "Engenharia Econômica de Recursos Hídricos – TH035",
                        "Estruturas de Concreto III – TC054",
                        "Estruturas de Edifícios II – TC056",
                        "Estruturas de Madeira – TC057",
                        "Estruturas Metálicas II – TC055",
                        "Expressão Gráfica III – CD035",
                        "Ferrovias – TT066",
                        "Geologia de Engenharia – TC049",
                        "Geotecnia Ambiental – TC053",
                        "Geotecnia Aplicada as Vias de Transporte – TT065",
                        "Geotecnia de Taludes e Contenções – TC052",
                        "Gerenciamento de Empreendimentos – TC062",
                        "Gerenciamento de Recursos Hídricos – TH036",
                        "Gerenciamento de Rodovias e Vias Urbanas – TT063",
                        "Hidráulica Ambiental – TH033",
                        "Hidráulica Fluvial – TH032",
                        "Instalações Prediais Especiais – TC065",
                        "Introdução a Engenharia de Segurança do Trabalho – TT068",
                        "Legislação e Prática Profissional – TC061",
                        "Logística e Transporte – TT058",
                        "Mecânica das Rochas – TC051",
                        "Método dos Elementos Finitos Aplicados a Engenharia de Estruturas – TC059",
                        "Modelagem e Planejamento de Transportes Urbanos – TT060",
                        "Planejamento e Gestão dos Sistemas Urbanos – TH042",
                        "Pontes e Estruturas Especiais – TC058",
                        "Portos e Hidrovias – TT067",
                        "Projeto de Obras Viárias – TT064",
                        "Projetos de Arquitetura – TC060",
                        "Projetos de Drenagem Urbana – TH037",
                        "Projetos de Obras Hidráulicas – TH031",
                        "Projetos de Obras Viárias – TT064",
                        "Projetos de Sistemas de Resíduos Sólidos Urbanos – TH038",
                        "Projetos de Sistemas de Saneamento Ambiental – TH039",
                        "Projetos de Sistemas Prediais Hidráulicos Sanitários – TH040",
                        "Qualidade e Conservação Ambiental – TH041",
                        "Segurança Viária – TT061",
                        "Sistemas de Recursos Hídricos – TH034",
                        "Técnica de Investigação Geotécnica e Instrumentação – TC050",
                        "Tópicos Avançados de Pavimentação – TT062",
                        "Tópicos Avançados em Geotecnia – TC048",
                        "Transporte Público – TT057"
                    ]
                }.get(selected_semestre, [])
                self.entry_disciplina.clear()
                self.entry_disciplina.addItems(disciplinas)

        elif selected_curso == "Engenharia Elétrica":
            selected_ementa = self.entry_ementa.currentText()

            if selected_ementa == "Ementa - 2013":
                selected_semestre = self.entry_semestre.currentText()
                disciplinas = {
                    "1º Semestre": [
                        "",
                        "Cálculo Diferencial e Integral I – CM201",
                        "Eletricidade Aplicada – TE144",
                        "Expressão Gráfica I – CD027",
                        "Geometria Analítica – CM045",
                        "Introdução à Engenharia – TC022",
                        "Mecânica Geral I – TC021",
                        "Programação de Computadores – CI208"
                    ],
                    "2º Semestre": [
                        "",
                        "Álgebra Linear – CM005",
                        "Cálculo Diferencial e Integral II – CM202",
                        "Construção Civil I – TC024",
                        "Expressão Gráfica II – CD028",
                        "Mecânica Geral II – TC023",
                        "Métodos Numéricos – CI202"
                    ],
                    "3º Semestre": [
                        "",
                        "Cálculo III – CM043",
                        "Construção Civil II – TC025",
                        "Estatística II – CE003",
                        "Mecânica dos Fluidos I – TH019",
                        "Mecânica Geral III – TC027",
                        "Resistência dos Materiais I – TC026",
                        "Topografia I – GA069"
                    ],
                    "4º Semestre": [
                        "",
                        "Introdução à Engenharia Geotécnica – TC029",
                        "Ciências do Ambiente – TH022",
                        "Materiais de Construção Civil I – TC030",
                        "Mecânica dos Fluidos II – TH021",
                        "Resistência dos Materiais II – TC028",
                        "Sistemas de Transporte – TT046",
                        "Topografia II – GA070"
                    ],
                    "5º Semestre": [
                        "",
                        "Estruturação Sanitária das Cidades – TH025",
                        "Hidráulica – TH020",
                        "Infra-Estrutura Viária – TT048",
                        "Laboratório de Mecânica dos Solos – TC033",
                        "Materiais de Construção Civil II – TC031",
                        "Mecânica das Estruturas I – TC032"
                    ],
                    "6º Semestre": [
                        "",
                        "Atividades Formativas – AAC005",
                        "Equipamentos de Construção e Conservação – TT047",
                        "Hidráulica e Hidrologia Experimental – TH027",
                        "Hidrologia – TH024",
                        "Materiais de Construção Civil III – TC034",
                        "Mecânica das Estruturas II – TC036",
                        "Mecânica dos Solos – TC035"
                    ],
                    "7º Semestre": [
                        "",
                        "Construção Civil III – TC038",
                        "Engenharia de Recursos Hídricos – TH026",
                        "Engenharia Social – TH045",
                        "Estruturas de Concreto I – TC037",
                        "Laboratório de Materiais de Construção – TC039",
                        "Obras Geotécnicas – TC066",
                        "Planejamento de Transportes – TT049",
                        "Saneamento Ambiental I – TH028"
                    ],
                    "8º Semestre": [
                        "",
                        "Construção Civil IV – TC042",
                        "Economia de Engenharia I – TT007",
                        "Estágio Supervisionado – TC046",
                        "Estágio Supervisionado – TH043",
                        "Estágio Supervisionado – TT054",
                        "Estruturas de Concreto II – TC040",
                        "Geotecnia de Fundações – TC041",
                        "Pavimentação – TT051",
                        "Saneamento Ambiental II – TH029"
                    ],
                    "9º Semestre": [
                        "",
                        "Administração de Empresas de Engenharia I – TT008",
                        "Estrutura de Edifícios I – TC044",
                        "Estruturas Metálicas I – TC043",
                        "Gerenciamento de Projetos – TC045",
                        "Sistemas Prediais, Hidráulicos e Sanitários – TH030",
                        "Trabalho Final de Curso I – TC081",
                        "Trabalho Final de Curso I – TH061",
                        "Trabalho Final de Curso I – TT071"
                    ],
                    "10º Semestre": [
                        "",
                        "Trabalho Final de Curso II – TC082",
                        "Trabalho Final de Curso II – TH062",
                        "Trabalho Final de Curso II – TT072"
                    ],
                    "Optativas (mínimo 6)": [
                        "",
                        "Avaliação de Impactos Ambientais – TT059",
                        "Engenharia de Avaliações – TC064",
                        "Engenharia de Tráfego – TT056",
                        "Engenharia Econômica de Recursos Hídricos – TH035",
                        "Estruturas de Concreto III – TC054",
                        "Estruturas de Edifícios II – TC056",
                        "Estruturas de Madeira – TC057",
                        "Estruturas Metálicas II – TC055",
                        "Expressão Gráfica III – CD035",
                        "Ferrovias – TT066",
                        "Geologia de Engenharia – TC049",
                        "Geotecnia Ambiental – TC053",
                        "Geotecnia Aplicada as Vias de Transporte – TT065",
                        "Geotecnia de Taludes e Contenções – TC052",
                        "Gerenciamento de Empreendimentos – TC062",
                        "Gerenciamento de Recursos Hídricos – TH036",
                        "Gerenciamento de Rodovias e Vias Urbanas – TT063",
                        "Hidráulica Ambiental – TH033",
                        "Hidráulica Fluvial – TH032",
                        "Instalações Prediais Especiais – TC065",
                        "Introdução a Engenharia de Segurança do Trabalho – TT068",
                        "Legislação e Prática Profissional – TC061",
                        "Logística e Transporte – TT058",
                        "Mecânica das Rochas – TC051",
                        "Método dos Elementos Finitos Aplicados a Engenharia de Estruturas – TC059",
                        "Modelagem e Planejamento de Transportes Urbanos – TT060",
                        "Planejamento e Gestão dos Sistemas Urbanos – TH042",
                        "Pontes e Estruturas Especiais – TC058",
                        "Portos e Hidrovias – TT067",
                        "Projeto de Obras Viárias – TT064",
                        "Projetos de Arquitetura – TC060",
                        "Projetos de Drenagem Urbana – TH037",
                        "Projetos de Obras Hidráulicas – TH031",
                        "Projetos de Obras Viárias – TT064",
                        "Projetos de Sistemas de Resíduos Sólidos Urbanos – TH038",
                        "Projetos de Sistemas de Saneamento Ambiental – TH039",
                        "Projetos de Sistemas Prediais Hidráulicos Sanitários – TH040",
                        "Qualidade e Conservação Ambiental – TH041",
                        "Segurança Viária – TT061",
                        "Sistemas de Recursos Hídricos – TH034",
                        "Técnica de Investigação Geotécnica e Instrumentação – TC050",
                        "Tópicos Avançados de Pavimentação – TT062",
                        "Tópicos Avançados em Geotecnia – TC048",
                        "Transporte Público – TT057"
                    ]
                }.get(selected_semestre, [])
                self.entry_disciplina.clear()
                self.entry_disciplina.addItems(disciplinas)

            elif selected_ementa == "Ementa - 2019":
                selected_semestre = self.entry_semestre.currentText()
                disciplinas = {
                    "1º Semestre": [
                        "",
                        "Expressão Gráfica A – CEG019",
                        "Fundamentação de Programação de Computadores – CI182",
                        "Pré-Cálculo – CM310",
                        "Física I – TC501",
                        "Química Aplicada – TC502",
                        "Introdução à Engenharia e Inovação – TC591",
                        "Introdução à Engenharia e Inovação – TH591",
                        "Introdução à Engenharia e Inovação – TT591"
                    ],
                    "2º Semestre": [
                        "",
                        "Métodos Numéricos – CI202",
                        "Introdução à Geometria Analítica e Álgebra Linear – CM303",
                        "Cálculo 1 – CM311",
                        "Desenho Arquitetônico – TC503",
                        "Análise Estrutural I – TC504",
                        "Física II – TH512"
                    ],
                    "3º Semestre": [
                        "",
                        "Introdução à Estatística – CE009",
                        "Cálculo 2 – CM312",
                        "Topografia I – GA175",
                        "Construção Civil I – TC505",
                        "Análise Estrutural II – TC506",
                        "Sistemas Estruturais – TC507",
                        "Mecânica dos Fluídos I – TH501",
                        "Sistemas de Transporte – TT501"
                    ],
                    "4º Semestre": [
                        "",
                        "Cálculo 4 – CM314",
                        "Topografia II – GA176",
                        "Construção Civil II – TC508",
                        "Mecânica dos Sólidos I – TC509",
                        "Materiais de Construção Civil I – TC510",
                        "Laboratório de Materiais de Construção Civil – TC511",
                        "Mecânica dos Fluídos II – TH502",
                        "Mecânica dos Fluídos Experimental – TH503"
                    ],
                    "5º Semestre": [
                        "",
                        "Caracterização Geológica - Geotécnica – TC512",
                        "Mecânica dos Sólidos II – TC513",
                        "Materiais de Construção Civil II – TC514",
                        "Hidráulica – TH504",
                        "Ciências do Ambiente – TH508",
                        "Planejamento e Operação de Transportes – TT502",
                        "Engenharia Civil e Sustentabilidade – TC592",
                        "Engenharia Civil e Sustentabilidade – TH592",
                        "Engenharia Civil e Sustentabilidade – TT592",
                    ],
                    "6º Semestre": [
                        "",
                        "Hidráulica dos Solos – TC515",
                        "Análise Estrutural III – TC516",
                        "Construção Civil III – TC517",
                        "Hidrologia – TH505",
                        "Hidráulica e Hidrologia Experimental – TH506",
                        "Equipamentos de Terraplanagem e de Pavimentação – TT503",
                        "Estruturação das Cidades – TH593",
                        "Estruturação das Cidades – TT593"
                    ],
                    "7º Semestre": [
                        "",
                        "Mecânica dos Solos – TC518",
                        "Estruturas de Concreto I – TC519",
                        "Gestão de Projetos – TC520",
                        "Engenharia de Recursos Hídricos – TH507",
                        "Saneamento Ambiental I – TH509",
                        "Engenharia Econômica – TT504",
                        "Engenharia Urbana – TH594",
                        "Engenharia Urbana – TT594"
                    ],
                    "8º Semestre": [
                        "",
                        "Obras Geotécnicas – TC521",
                        "Estruturas de Concreto II – TC522",
                        "Saneamento Ambiental II – TH510",
                        "Estradas – TT505",
                        "Pavimentação – TT506",
                        "Laboratório de Transportes – TT507",
                        "Economia de Engenharia – TT508",
                        "Metodologia do Trabalho Científico e Tecnológico – TT509"
                    ],
                    "9º Semestre": [
                        "",
                        "Estruturas de Aço – TC523",
                        "Estruturas de Madeira – TC524",
                        "Engenharia de Fundações – TC525",
                        "Eletricidade Aplicada – TE144",
                        "Engenharia e Sociedade – TH511",
                        "Administração de Empresas – TT510",
                        "Trabalho Final de Curso I – TC581",
                        "Trabalho Final de Curso I – TH581",
                        "Trabalho Final de Curso I – TT581",
                        "Projeto de Infraestrutura e Obras Especiais – TC595",
                        "Projeto de Infraestrutura e Obras Especiais – TH595",
                        "Projeto de Infraestrutura e Obras Especiais – TT595"
                    ],
                    "10º Semestre": [
                        "",
                        "Trabalho Final de Curso II – TC582",
                        "Trabalho Final de Curso II – TH582",
                        "Trabalho Final de Curso II – TT582",
                        "Trabalho Final de Curso II – TC583",
                        "Trabalho Final de Curso II – TH583",
                        "Trabalho Final de Curso II – TT583",
                        "Estágio Supervisionado Obrigatório – TC585",
                        "Estágio Supervisionado Obrigatório – TH585",
                        "Estágio Supervisionado Obrigatório – TT585",
                        "Projetos de Edifícios – TC596",
                        "Projetos de Edifícios – TH596",
                    ],
                    "Optativas (mínimo 6)": [
                        "",
                        "Avaliação de Impactos Ambientais – TT059",
                        "Engenharia de Avaliações – TC064",
                        "Engenharia de Tráfego – TT056",
                        "Engenharia Econômica de Recursos Hídricos – TH035",
                        "Estruturas de Concreto III – TC054",
                        "Estruturas de Edifícios II – TC056",
                        "Estruturas de Madeira – TC057",
                        "Estruturas Metálicas II – TC055",
                        "Expressão Gráfica III – CD035",
                        "Ferrovias – TT066",
                        "Geologia de Engenharia – TC049",
                        "Geotecnia Ambiental – TC053",
                        "Geotecnia Aplicada as Vias de Transporte – TT065",
                        "Geotecnia de Taludes e Contenções – TC052",
                        "Gerenciamento de Empreendimentos – TC062",
                        "Gerenciamento de Recursos Hídricos – TH036",
                        "Gerenciamento de Rodovias e Vias Urbanas – TT063",
                        "Hidráulica Ambiental – TH033",
                        "Hidráulica Fluvial – TH032",
                        "Instalações Prediais Especiais – TC065",
                        "Introdução a Engenharia de Segurança do Trabalho – TT068",
                        "Legislação e Prática Profissional – TC061",
                        "Logística e Transporte – TT058",
                        "Mecânica das Rochas – TC051",
                        "Método dos Elementos Finitos Aplicados a Engenharia de Estruturas – TC059",
                        "Modelagem e Planejamento de Transportes Urbanos – TT060",
                        "Planejamento e Gestão dos Sistemas Urbanos – TH042",
                        "Pontes e Estruturas Especiais – TC058",
                        "Portos e Hidrovias – TT067",
                        "Projeto de Obras Viárias – TT064",
                        "Projetos de Arquitetura – TC060",
                        "Projetos de Drenagem Urbana – TH037",
                        "Projetos de Obras Hidráulicas – TH031",
                        "Projetos de Obras Viárias – TT064",
                        "Projetos de Sistemas de Resíduos Sólidos Urbanos – TH038",
                        "Projetos de Sistemas de Saneamento Ambiental – TH039",
                        "Projetos de Sistemas Prediais Hidráulicos Sanitários – TH040",
                        "Qualidade e Conservação Ambiental – TH041",
                        "Segurança Viária – TT061",
                        "Sistemas de Recursos Hídricos – TH034",
                        "Técnica de Investigação Geotécnica e Instrumentação – TC050",
                        "Tópicos Avançados de Pavimentação – TT062",
                        "Tópicos Avançados em Geotecnia – TC048",
                        "Transporte Público – TT057"
                    ]
                }.get(selected_semestre, [])
                self.entry_disciplina.clear()
                self.entry_disciplina.addItems(disciplinas)

    def clear_database(self):
        query = QSqlQuery()
        query.exec("DELETE FROM atividades")

    def submit(self):
        disciplina = self.entry_disciplina.currentText()
        codigo = self.entry_codigo.currentText()
        tipo = self.combo_tipo.currentText()
        sequencia = self.combo_sequencia.currentText()
        data = self.calendar.selectedDate()
        data_string = data.toString("dd/MM/yyyy")

        if data_string == "":
            QMessageBox.critical(self, "Erro", "Selecione, pelo menos, uma data antes de prosseguir.")
            return

        print("Disciplina:", disciplina)
        print("Código:", codigo)
        print("Tipo:", tipo)
        print("Sequência:", sequencia)
        print("Data:", data_string)

        query.prepare("INSERT INTO atividades VALUES (:disciplina, :codigo, :tipo, :sequencia, :data)")
        query.bindValue(":disciplina", disciplina)
        query.bindValue(":codigo", codigo)
        query.bindValue(":tipo", tipo)
        query.bindValue(":sequencia", sequencia)
        query.bindValue(":data", data_string)
        if not query.exec():
            QMessageBox.critical(self, "Erro", "Não foi possível inserir os dados no banco de dados.")

        self.update_textbox()

    def closeEvent(self, event):
        self.clear_database()
        super().closeEvent(event)

    def clear_entries(self):
        self.combo_curso.setCurrentIndex(-1)
        self.entry_ementa.clear()
        self.entry_semestre.clear()
        self.entry_disciplina.clear()
        self.entry_codigo.setCurrentIndex(-1)
        self.combo_tipo.setCurrentIndex(-1)
        self.combo_sequencia.setCurrentIndex(-1)
        self.calendar.setSelectedDate(QDate())

        query.exec("DELETE FROM atividades")

        self.update_textbox()

    def generate_html(self):
        if not self.query.exec("SELECT * FROM atividades"):
            QMessageBox.critical(self, "Erro", "Não foi possível executar a consulta no banco de dados.")
            return

        dicionario_disciplinas = {
            "1ª Coloracao Disciplina": [
                "",
                "Cálculo Diferencial e Integral I – CM201",
                "Mecânica Geral II – TC023",
                "Materiais de Construção Civil I – TC030",
                "Atividades Formativas – AAC005",
                "Laboratório de Materiais de Construção – TC039",
                "Pavimentação – TT051",
                "Trabalho Final de Curso II – TH062",
                "Ferrovias – TT066",
                "Introdução a Engenharia de Segurança do Trabalho – TT068",
                "Projetos de Drenagem Urbana – TH037",
                "Tópicos Avançados em Geotecnia – TC048",
                "Introdução à Geometria Analítica e Álgebra Linear – CM303",
                "Mecânica dos Fluídos I – TH501",
                "Mecânica dos Sólidos II – TC513",
                "Hidrologia – TH505",
                "Engenharia Urbana – TH594",
                "Estruturas de Madeira – TC524",
                "Trabalho Final de Curso II – TC582"
            ],
            "2ª Coloracao Disciplina": [
                "",
                "Eletricidade Aplicada – TE144",
                "Métodos Numéricos – CI202",
                "Mecânica dos Fluidos II – TH021",
                "Equipamentos de Construção e Conservação – TT047",
                "Obras Geotécnicas – TC066",
                "Saneamento Ambiental II – TH029",
                "Trabalho Final de Curso II – TT072",
                "Geologia de Engenharia – TC049",
                "Legislação e Prática Profissional – TC061",
                "Projetos de Obras Hidráulicas – TH031",
                "Transporte Público – TT057",
                "Cálculo 1 – CM311",
                "Sistemas de Transporte – TT501",
                "Materiais de Construção Civil II – TC514",
                "Hidráulica e Hidrologia Experimental – TH506",
                "Engenharia Urbana – TT594",
                "Engenharia de Fundações – TC525",
                "Trabalho Final de Curso II – TH582"
            ],
            "3ª Coloracao Disciplina": [
                "",
                "Expressão Gráfica I – CD027",
                "Cálculo III – CM043",
                "Resistência dos Materiais II – TC028",
                "Hidráulica e Hidrologia Experimental – TH027",
                "Planejamento de Transportes – TT049",
                "Administração de Empresas de Engenharia I – TT008",
                "Avaliação de Impactos Ambientais – TT059",
                "Geotecnia Ambiental – TC053",
                "Logística e Transporte – TT058",
                "Projetos de Obras Viárias – TT064",
                "Expressão Gráfica A – CEG019",
                "Desenho Arquitetônico – TC503",
                "Cálculo 4 – CM314",
                "Hidráulica – TH504",
                "Equipamentos de Terraplanagem e de Pavimentação – TT503",
                "Obras Geotécnicas – TC521",
                "Eletricidade Aplicada – TE144",
                "Trabalho Final de Curso II – TT582"
            ],
            "4ª Coloracao Disciplina": [
                "",
                "Geometria Analítica – CM045",
                "Construção Civil II – TC025",
                "Sistemas de Transporte – TT046",
                "Hidrologia – TH024",
                "Saneamento Ambiental I – TH028",
                "Estrutura de Edifícios I – TC044",
                "Engenharia de Avaliações – TC064",
                "Geotecnia Aplicada as Vias de Transporte – TT065",
                "Mecânica das Rochas – TC051",
                "Projetos de Sistemas de Resíduos Sólidos Urbanos – TH038",
                "Fundamentação de Programação de Computadores – CI182",
                "Análise Estrutural I – TC504",
                "Topografia II – GA176",
                "Ciências do Ambiente – TH508",
                "Estruturação das Cidades – TH593",
                "Estruturas de Concreto II – TC522",
                "Engenharia e Sociedade – TH511",
                "Trabalho Final de Curso II – TC583"
            ],
            "5ª Coloracao Disciplina": [
                "",
                "Introdução à Engenharia – TC022",
                "Estatística II – CE003",
                "Topografia II – GA070",
                "Materiais de Construção Civil III – TC034",
                "Construção Civil IV – TC042",
                "Estruturas Metálicas I – TC043",
                "Engenharia de Tráfego – TT056",
                "Geotecnia de Taludes e Contenções – TC052",
                "Método dos Elementos Finitos Aplicados a Engenharia de Estruturas – TC059",
                "Projetos de Sistemas de Saneamento Ambiental – TH039",
                "Pré-Cálculo – CM310",
                "Física II – TH512",
                "Construção Civil II – TC508",
                "Planejamento e Operação de Transportes – TT502",
                "Estruturação das Cidades – TT593",
                "Saneamento Ambiental II – TH510",
                "Administração de Empresas – TT510",
                "Trabalho Final de Curso II – TH583"
            ],
            "6ª Coloracao Disciplina": [
                "",
                "Mecânica Geral I – TC021",
                "Mecânica dos Fluidos I – TH019",
                "Estruturação Sanitária das Cidades – TH025",
                "Mecânica das Estruturas II – TC036",
                "Economia de Engenharia I – TT007",
                "Gerenciamento de Projetos – TC045",
                "Engenharia Econômica de Recursos Hídricos – TH035",
                "Gerenciamento de Empreendimentos – TC062",
                "Modelagem e Planejamento de Transportes Urbanos – TT060",
                "Projetos de Sistemas Prediais Hidráulicos Sanitários – TH040",
                "Física I – TC501",
                "Introdução à Estatística – CE009",
                "Mecânica dos Sólidos I – TC509",
                "Engenharia Civil e Sustentabilidade – TC592",
                "Mecânica dos Solos – TC518",
                "Estradas – TT505",
                "Trabalho Final de Curso I – TC581",
                "Trabalho Final de Curso II – TT583"
            ],
            "7ª Coloracao Disciplina": [
                "",
                "Programação de Computadores – CI208",
                "Mecânica Geral III – TC027",
                "Hidráulica – TH020",
                "Mecânica dos Solos – TC035",
                "Estágio Supervisionado – TC046",
                "Sistemas Prediais, Hidráulicos e Sanitários – TH030",
                "Estruturas de Concreto III – TC054",
                "Gerenciamento de Recursos Hídricos – TH036",
                "Planejamento e Gestão dos Sistemas Urbanos – TH042",
                "Qualidade e Conservação Ambiental – TH041",
                "Química Aplicada – TC502",
                "Cálculo 2 – CM312",
                "Materiais de Construção Civil I – TC510",
                "Engenharia Civil e Sustentabilidade – TH592",
                "Estruturas de Concreto I – TC519",
                "Pavimentação – TT506",
                "Trabalho Final de Curso I – TH581",
                "Estágio Supervisionado Obrigatório – TC585"
            ],
            "8ª Coloracao Disciplina": [
                "",
                "Álgebra Linear – CM005",
                "Resistência dos Materiais I – TC026",
                "Infra-Estrutura Viária – TT048",
                "Construção Civil III – TC038",
                "Estágio Supervisionado – TH043",
                "Trabalho Final de Curso I – TC081",
                "Estruturas de Edifícios II – TC056",
                "Gerenciamento de Rodovias e Vias Urbanas – TT063",
                "Pontes e Estruturas Especiais – TC058",
                "Segurança Viária – TT061",
                "Introdução à Engenharia e Inovação – TC591",
                "Topografia I – GA175",
                "Laboratório de Materiais de Construção Civil – TC511",
                "Engenharia Civil e Sustentabilidade – TT592",
                "Gestão de Projetos – TC520",
                "Laboratório de Transportes – TT507",
                "Trabalho Final de Curso I – TT581",
                "Estágio Supervisionado Obrigatório – TH585"
            ],
            "9ª Coloracao Disciplina": [
                "",
                "Cálculo Diferencial e Integral II – CM202",
                "Topografia I – GA069",
                "Laboratório de Mecânica dos Solos – TC033",
                "Engenharia de Recursos Hídricos – TH026",
                "Estágio Supervisionado – TT054",
                "Trabalho Final de Curso I – TH061",
                "Estruturas de Madeira – TC057",
                "Hidráulica Ambiental – TH033",
                "Portos e Hidrovias – TT067",
                "Sistemas de Recursos Hídricos – TH034",
                "Introdução à Engenharia e Inovação – TH591",
                "Construção Civil I – TC505",
                "Mecânica dos Fluídos II – TH502",
                "Hidráulica dos Solos – TC515",
                "Engenharia de Recursos Hídricos – TH507",
                "Economia de Engenharia – TT508",
                "Projeto de Infraestrutura e Obras Especiais – TC595",
                "Estágio Supervisionado Obrigatório – TT585"
            ],
            "10ª Coloracao Disciplina": [
                "",
                "Construção Civil I – TC024",
                "Introdução à Engenharia Geotécnica – TC029",
                "Materiais de Construção Civil II – TC031",
                "Engenharia Social – TH045",
                "Estruturas de Concreto II – TC040",
                "Trabalho Final de Curso I – TT071",
                "Estruturas Metálicas II – TC055",
                "Hidráulica Fluvial – TH032",
                "Projeto de Obras Viárias – TT064",
                "Técnica de Investigação Geotécnica e Instrumentação – TC050",
                "Introdução à Engenharia e Inovação – TT591",
                "Análise Estrutural II – TC506",
                "Mecânica dos Fluídos Experimental – TH503",
                "Análise Estrutural III – TC516",
                "Saneamento Ambiental I – TH509",
                "Metodologia do Trabalho Científico e Tecnológico – TT509",
                "Projeto de Infraestrutura e Obras Especiais – TH595",
                "Projetos de Edifícios – TC596"
            ],
            "11ª Coloracao Disciplina": [
                "",
                "Expressão Gráfica II – CD028",
                "Ciências do Ambiente – TH022",
                "Mecânica das Estruturas I – TC032",
                "Estruturas de Concreto I – TC037",
                "Geotecnia de Fundações – TC041",
                "Trabalho Final de Curso II – TC082",
                "Expressão Gráfica III – CD035",
                "Instalações Prediais Especiais – TC065",
                "Projetos de Arquitetura – TC060",
                "Tópicos Avançados de Pavimentação – TT062",
                "Métodos Numéricos – CI202",
                "Sistemas Estruturais – TC507",
                "Caracterização Geológica - Geotécnica – TC512",
                "Construção Civil III – TC517",
                "Engenharia Econômica – TT504",
                "Estruturas de Aço – TC523",
                "Projeto de Infraestrutura e Obras Especiais – TT595",
                "Projetos de Edifícios – TH596"
            ]
        }

        dicionario_de_cores = {
            "1ª Coloracao Disciplina": "red",
            "2ª Coloracao Disciplina": "blue",
            "3ª Coloracao Disciplina": "green",
            "4ª Coloracao Disciplina": "olive",
            "5ª Coloracao Disciplina": "purple",
            "6ª Coloracao Disciplina": "orange",
            "7ª Coloracao Disciplina": "brown",
            "8ª Coloracao Disciplina": "deeppink",
            "9ª Coloracao Disciplina": "teal",
            "10ª Coloracao Disciplina": "magenta",
            "11ª Coloracao Disciplina": "darkslategray"
        }

        data_infos = []
        while self.query.next():
            sequencia = self.query.value(3)
            disciplina = self.query.value(0)

            cor = "black"
            for coloracao, disciplinas in dicionario_disciplinas.items():
                if disciplina in disciplinas:
                    cor = dicionario_de_cores.get(coloracao, "black")
                    break

            if sequencia != "":
                data_info = (
                    self.query.value(4),
                    f'<b>{self.query.value(4)}</b> ___ {self.query.value(2)} {self.query.value(3)} ___ '
                    f'<font color="{cor}"><b>{disciplina}</b></font> ___ {self.query.value(1)}<br><br>'
                )
                data_infos.append(data_info)

            elif sequencia == "":
                data_info = (
                    self.query.value(4),
                    f'<b>{self.query.value(4)}</b> ___ {self.query.value(2)}{self.query.value(3)} ___ '
                    f'<font color="{cor}"><b>{disciplina}</b></font> ___ {self.query.value(1)}<br><br>'
                )
                data_infos.append(data_info)

        sorted_data_infos = self.sort_dates(data_infos)

        html_string = ""
        for data_info in sorted_data_infos:
            html_string += data_info[1]

        return html_string

    def export_to_pdf(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Exportar para PDF", "", "PDF Files (*.pdf)")
        text = self.textbox.toHtml()

        if asyncio.ensure_future(self._export_to_pdf(filepath, text)):
            QMessageBox.information(self, "Exportar para PDF", "Exportação concluída com sucesso.")
        else:
            QMessageBox.critical(self, "Exportar para PDF", "Falha na exportação para PDF.")

    async def _export_to_pdf(self, filepath, text):
        if filepath:
            text = f"""
                    <html>
                    <head>
                    <style>
                    @page {{
                        margin-top: 1cm;
                        margin-right: 1cm;
                        margin-bottom: 1cm;
                        margin-left: 1cm;
                    }}
                    body {{
                        font-family: 'Arial';
                        font-size: 11px;
                        line-height: 1.5;
                    }}
                    </style>
                    </head>
                    <body>
                    {text}
                    </body>
                    </html>
                    """

            try:
                browser = await launch()
                page = await browser.newPage()
                await page.setContent(text)
                await page.pdf({"path": filepath, "format": "A4"})
                await browser.close()

                return True
            except Exception as e:
                print(f"Falha na exportação para PDF. Erro: {str(e)}")
                return False

    def sort_dates(self, data_infos):
        return sorted(data_infos, key=lambda x: days_from_year_start(x[0]))

    def update_textbox(self):
        self.textbox.clear()
        font = QFont("Arial", 10)
        self.textbox.setFont(font)
        self.textbox.document().setDefaultFont(font)
        self.textbox.insertHtml(self.generate_html())

    def update_database(self):
        query = QSqlQuery()
        if not query.exec("DELETE FROM atividades"):
            QMessageBox.critical(self, "Erro", "Não foi possível excluir os dados do banco de dados.")
            return

        data = self.textbox.toHtml().strip()
        rows = data.split("\n")

        for row in rows:
            info = row.split("___")
            if len(info) == 4:
                data_string, codigo_tipo, disciplina, sequencia = info
                codigo, tipo = codigo_tipo.strip().split()
                data_string = data_string.strip()
                data = QDate.fromString(data_string, "dd/MM/yyyy").toString("dd/MM/yyyy")

                query.prepare("INSERT INTO atividades VALUES (:disciplina, :codigo, :tipo, :sequencia, :data)")
                query.bindValue(":disciplina", disciplina.strip())
                query.bindValue(":codigo", codigo.strip())
                query.bindValue(":tipo", tipo.strip())
                query.bindValue(":sequencia", sequencia.strip())
                query.bindValue(":data", data.strip())
                query.exec()

        self.update_textbox()


def days_from_year_start(date_str):
    date = QDate.fromString(date_str, "dd/MM/yyyy")
    year_start = QDate(date.year(), 1, 1)
    return year_start.daysTo(date)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = MainWindow()
    window.show()
    with loop:
        sys.exit(loop.run_forever())

"""
Neste projeto, foram utilizadas as seguintes bibliotecas:

- `os`: Biblioteca padrão do Python para interação com o sistema operacional.
- `sys`: Biblioteca padrão do Python para acessar algumas variáveis usadas ou mantidas pelo interpretador Python.
- `asyncio`: Biblioteca padrão do Python para escrever código assíncrono usando a sintaxe async/await.
- `PySide6`: Biblioteca Python para a criação de interfaces gráficas de usuário (GUIs) usando o framework Qt.
- `QSqlDatabase`, `QSqlQuery`: Classes do módulo `PySide6.QtSql` para interação com bancos de dados SQL.
- `pyppeteer`: Biblioteca Python para automação de navegador headless usando a API do Puppeteer.
- `qasync`: Biblioteca Python para integração de asyncio com o Qt.

Gostaria de expressar meus sinceros agradecimentos aos desenvolvedores e contribuidores dessas bibliotecas. Seu trabalho tem sido fundamental para o desenvolvimento deste projeto.
"""
