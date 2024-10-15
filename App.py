import sqlite3
import pandas as pd
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

# Configuração de cores e layout moderno
Window.clearcolor = (1, 1, 1, 1)  # Fundo branco

# Conectando ao banco de dados SQLite
conn = sqlite3.connect('financial_data.db')
cursor = conn.cursor()

# Criação da tabela de transações, se não existir
cursor.execute('''CREATE TABLE IF NOT EXISTS transacoes
                  (id INTEGER PRIMARY KEY, descricao TEXT, valor REAL, data TEXT)''')
conn.commit()

class FinancialApp(App):
    def build(self):
        self.title = 'Controle de Gastos'

        # Layout principal da aplicação
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Label que exibirá o saldo total (somente valor)
        self.label_saldo = Label(text='€0.00', font_size=60, size_hint=(1, 0.3), color=(0, 0, 0, 1))
        layout.add_widget(self.label_saldo)

        # Botão para acessar o menu
        self.menu_button = Button(text='Menu', size_hint=(1, 0.1), background_color=(0.2, 0.6, 0.8, 1), color=(1, 1, 1, 1),font_size=40)
        self.menu_button.bind(on_release=self.open_menu)
        layout.add_widget(self.menu_button)

        # Botão para adicionar gasto
        btn_gasto = Button(text='Adicionar Gasto', size_hint=(1, 0.15), background_color=(0.2, 0.7, 0.4, 1), color=(1, 1, 1, 1),font_size=40)
        btn_gasto.bind(on_press=self.abrir_modal_gasto)  # Chamada para o método correto
        layout.add_widget(btn_gasto)

        # Botão para acessar o histórico de transações
        btn_historico = Button(text='Ver Registros', size_hint=(1, 0.15), background_color=(0.5, 0.5, 0.8, 1), color=(1, 1, 1, 1),font_size=40)
        btn_historico.bind(on_press=self.ver_registros_gastos)
        layout.add_widget(btn_historico)

        # Atualizar o saldo na inicialização
        self.atualizar_saldo()

        return layout

    def abrir_modal_gasto(self, instance):
        # Função para abrir o popup de adicionar gasto
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        input_descricao = TextInput(hint_text='Descrição', multiline=False, background_color=(0.95, 0.95, 0.95, 1))
        input_valor = TextInput(hint_text='Valor (€)', input_filter='float', multiline=False, background_color=(0.95, 0.95, 0.95, 1))
        btn_adicionar = Button(text='Adicionar', size_hint=(1, 1), background_color=(0.2, 0.7, 0.4, 1), color=(1, 1, 1, 1))

        def salvar_gasto(instance):
            descricao = input_descricao.text
            valor = input_valor.text
            if descricao and valor:  # Verifica se os campos não estão vazios
                # Salva o gasto no banco de dados com a data atual
                cursor.execute("INSERT INTO transacoes (descricao, valor, data) VALUES (?, ?, ?)", (descricao, -float(valor), datetime.now().strftime('%Y-%m-%d')))
                conn.commit()
                self.atualizar_saldo()
                popup.dismiss()

        btn_adicionar.bind(on_release=salvar_gasto)
        content.add_widget(input_descricao)
        content.add_widget(input_valor)
        content.add_widget(btn_adicionar)

        popup = Popup(title='Adicionar Gasto', content=content, size_hint=(0.6, 0.25))
        popup.open()

    def open_menu(self, instance):
        # Popup para o menu
        content = BoxLayout(orientation='vertical', padding=0, spacing=10)

        # Botão "Adicionar Valor Recebido"
        btn_add_recebido = Button(text='Adicionar Valor', size_hint_y=None, height=44, background_color=(0.2, 0.6, 0.8, 1), color=(1, 1, 1, 1))
        btn_add_recebido.bind(on_release=self.adicionar_valor_recebido)
        content.add_widget(btn_add_recebido)

        # Botão "Resetar Saldo"
        btn_reset_saldo = Button(text='Resetar Saldo', size_hint_y=None, height=44, background_color=(0.2, 0.6, 0.8, 1), color=(1, 1, 1, 1))
        btn_reset_saldo.bind(on_release=self.confirmar_reset_saldo)
        content.add_widget(btn_reset_saldo)

        # Botão "Resetar Registros"
        btn_reset_registros = Button(text='Resetar Registros', size_hint_y=None, height=44, background_color=(0.2, 0.6, 0.8, 1), color=(1, 1, 1, 1))
        btn_reset_registros.bind(on_release=self.confirmar_reset_registros)
        content.add_widget(btn_reset_registros)

        # Botão "Exportar Registros"
        btn_exportar = Button(text='Exportar Registros', size_hint_y=None, height=44, background_color=(0.2, 0.6, 0.8, 1), color=(1, 1, 1, 1))
        btn_exportar.bind(on_release=self.selecionar_formato_exportacao)
        content.add_widget(btn_exportar)

        # Popup do menu
        popup = Popup(title='Menu', content=content, size_hint=(0.5, 0.3))
        popup.open()

    def selecionar_formato_exportacao(self, instance):
        # Modal para selecionar o formato de exportação (PDF ou CSV)
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        btn_pdf = Button(text='Exportar como PDF', size_hint_y=None, height=44)
        btn_csv = Button(text='Exportar como CSV', size_hint_y=None, height=44)

        btn_pdf.bind(on_release=lambda x: self.exportar_registros('pdf'))
        btn_csv.bind(on_release=lambda x: self.exportar_registros('csv'))

        content.add_widget(btn_pdf)
        content.add_widget(btn_csv)

        popup = Popup(title='Selecionar Formato de Exportação', content=content, size_hint=(0.6, 0.2))
        popup.open()

    def exportar_registros(self, formato):
        # Buscando registros no banco de dados
        registros = pd.read_sql_query("SELECT descricao, valor, data FROM transacoes", conn)
        saldo_atual = self.obter_saldo()

        if formato == 'csv':
            # Salvar como CSV
            registros.to_csv('registros_gastos.csv', index=False)
            
            # Popup de sucesso
            popup = Popup(title='Exportação Completa', content=Label(text='Registros exportados como CSV com sucesso!'), size_hint=(0.6, 0.4))
            popup.open()
        
        elif formato == 'pdf':
            # Salvar como PDF (com saldo e em formato de tabela)
            c = canvas.Canvas("registros_gastos.pdf", pagesize=letter)

            # Título do PDF
            c.drawString(100, 750, "Registros de Gastos")

            # Preparar dados para tabela
            data = [["Descrição", "Valor (€)", "Data"]] + registros.values.tolist()

            # Adiciona o saldo ao final da tabela
            data.append(["", "Saldo", f"€{saldo_atual:.2f}"])

            # Criar tabela
            tabela = Table(data)
            tabela.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                                        ('GRID', (0, 0), (-1, -1), 0.5, colors.black)]))

            # Definir o tamanho da tabela no PDF
            tabela.wrapOn(c, 400, 600)
            tabela.drawOn(c, 30, 500)

            c.save()

            # Popup de sucesso
            popup = Popup(title='Exportação Completa', content=Label(text='Registros exportados como PDF com sucesso!'), size_hint=(0.6, 0.4))
            popup.open()

    def adicionar_valor_recebido(self, instance):
        # Função para abrir o popup de adicionar valor recebido
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        input_valor_recebido = TextInput(hint_text='Valor Recebido (€)', input_filter='float', multiline=False, background_color=(0.95, 0.95, 0.95, 1))
        btn_adicionar = Button(text='Adicionar', size_hint=(1, 0.2), background_color=(0.2, 0.7, 0.4, 1), color=(1, 1, 1, 1))

        def salvar_valor(instance):
            valor = input_valor_recebido.text
            if valor:  # Verifica se o campo não está vazio
                # Salva o valor recebido no banco de dados com a data atual
                cursor.execute("INSERT INTO transacoes (descricao, valor, data) VALUES (?, ?, ?)", ('Recebimento', float(valor), datetime.now().strftime('%Y-%m-%d')))
                conn.commit()
                self.atualizar_saldo()
                popup.dismiss()

        btn_adicionar.bind(on_release=salvar_valor)
        content.add_widget(input_valor_recebido)
        content.add_widget(btn_adicionar)

        popup = Popup(title='Adicionar Valor Recebido', content=content, size_hint=(0.6, 0.4))
        popup.open()

    def ver_registros_gastos(self, instance):
        # Exibir registros de gastos (sem os recebimentos)
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        scrollview = ScrollView(size_hint=(1, None), size=(Window.width, Window.height * 0.7))

        grid = GridLayout(cols=3, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        cursor.execute("SELECT descricao, valor, data FROM transacoes WHERE descricao != 'Recebimento'")
        registros = cursor.fetchall()

        for descricao, valor, data in registros:
            grid.add_widget(Label(text=descricao, size_hint_y=None, height=40))
            grid.add_widget(Label(text=f'€{valor:.2f}', size_hint_y=None, height=40))
            grid.add_widget(Label(text=data, size_hint_y=None, height=40))

        scrollview.add_widget(grid)
        content.add_widget(scrollview)

        # Exibindo saldo total na parte inferior da tela
        saldo_layout = BoxLayout(orientation='horizontal', padding=10, size_hint_y=None, height=40)
        saldo_layout.add_widget(Label(text='Saldo Atual:'))
        saldo_layout.add_widget(Label(text=f'€{self.obter_saldo():.2f}'))
        content.add_widget(saldo_layout)

        btn_fechar = Button(text='Fechar', size_hint_y=None, height=44)
        btn_fechar.bind(on_release=lambda x: popup.dismiss())
        content.add_widget(btn_fechar)

        popup = Popup(title='Registros de Gastos', content=content, size_hint=(0.9, 0.9))
        popup.open()

    def confirmar_reset_saldo(self, instance):
        # Confirmação de resetar o saldo
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label_confirmar = Label(text='Deseja Resetar o Saldo?')
        content.add_widget(label_confirmar)

        botoes = BoxLayout(orientation='horizontal', spacing=10)
        btn_sim = Button(text='Sim', background_color=(0.2, 0.7, 0.4, 1), color=(1, 1, 1, 1))
        btn_nao = Button(text='Não', background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1))

        def reset_saldo(instance):
            cursor.execute("DELETE FROM transacoes WHERE descricao='Recebimento'")
            conn.commit()
            self.atualizar_saldo()
            popup.dismiss()

        btn_sim.bind(on_press=reset_saldo)
        btn_nao.bind(on_press=lambda x: popup.dismiss())
        botoes.add_widget(btn_sim)
        botoes.add_widget(btn_nao)
        content.add_widget(botoes)

        popup = Popup(title='Confirmar Reset', content=content, size_hint=(0.6, 0.4))
        popup.open()

    def confirmar_reset_registros(self, instance):
        # Confirmação de resetar os registros (exceto recebimentos)
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label_confirmar = Label(text='Deseja Resetar os Registros?')
        content.add_widget(label_confirmar)

        botoes = BoxLayout(orientation='horizontal', spacing=10)
        btn_sim = Button(text='Sim', background_color=(0.2, 0.7, 0.4, 1), color=(1, 1, 1, 1))
        btn_nao = Button(text='Não', background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1))

        def reset_registros(instance):
            cursor.execute("DELETE FROM transacoes WHERE descricao != 'Recebimento'")
            conn.commit()
            self.atualizar_saldo()
            popup.dismiss()

        btn_sim.bind(on_press=reset_registros)
        btn_nao.bind(on_press=lambda x: popup.dismiss())
        botoes.add_widget(btn_sim)
        botoes.add_widget(btn_nao)
        content.add_widget(botoes)

        popup = Popup(title='Confirmar Reset', content=content, size_hint=(0.6, 0.4))
        popup.open()

    def atualizar_saldo(self):
        # Calcular o saldo total
        cursor.execute("SELECT SUM(valor) FROM transacoes")
        saldo = cursor.fetchone()[0]

        if saldo is None:
            saldo = 0.00

        self.label_saldo.text = f'€{saldo:.2f}'

    def obter_saldo(self):
        cursor.execute("SELECT SUM(valor) FROM transacoes")
        saldo = cursor.fetchone()[0]
        if saldo is None:
            saldo = 0.00
        return saldo

if __name__ == '__main__':
    FinancialApp().run()
