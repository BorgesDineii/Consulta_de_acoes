import sys
import yfinance as yf
import matplotlib.dates as mdates
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objects as go
import os
import tempfile
from PyQt5.QtCore import QUrl

class AcaoWorker(QThread):
    dadosObtidos = pyqtSignal(object)

    def __init__(self, codigo_acao, periodo='6mo'):
        super().__init__()
        self.codigo_acao = codigo_acao
        self.periodo = periodo
        self.is_running = True

    def run(self):
        try:
            if not self.is_running:
                return
            # codigo_acao_ajustado = ajustar_codigo_para_mercado(self.codigo_acao)
            acao = yf.Ticker(self.codigo_acao)
            historico = acao.history(period=self.periodo)
            preco_atual = historico['Close'][-1]

            self.dadosObtidos.emit({'preco': preco_atual, 'historico':historico})
        except Exception as e:
            self.dadosObtidos.emit(None)
            print(f"Erro ao buscar os dados: {e}")

        #    if historico.empty:
        #        raise ValueError(f"Nenhum dado disponivel para a ação {self.codigo_acao}.")
        #    if self.is_running:
        #        self.sucesso.emit(self.codigo_acao, historico)
        #except Exception as e:
        #    self.erro.emit(str(e))


def stop(self):
    self.is_running = False
    if self.is_Running():
        self.quit()
        self.wait()

def get_historico_acao(codigo_acao, periodo='6mo'):
    """
    Retorna o historico de preços da ação para o periodo especificado.
    """
    print(f"[DEBUG] Buscando histórico para: {codigo_acao}, período: {periodo}")
    acao =  yf.Ticker(codigo_acao)
    historico = acao.history(period=periodo)
    if historico.empty:
        raise ValueError(f"Nenhum dado disponível para a ação '{codigo_acao}'.")
    return historico

class GraficoCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(5, 4))
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
    
    def plotar(self, historico):
        self.ax.clear()

        preco_inicial = historico['Close'].iloc[0]
        preco_final = historico['Close'].iloc[-1]

        cor_grafico = 'green' if preco_final > preco_inicial else 'red'

        #if historico.empty or 'Close' not in historico.columns:
        #    self.ax.clear()
        #    self.ax.set_title("Sem dados disponíveis")
        #    self.draw()
        #    return
        # historico = historico.resample('W').mean()
        """
        Plotar o gráfico de preços com base no histórico fornecido
        """
        
        self.ax.plot(historico.index, historico['Close'], label='Preço de Fechamento.', color='blue')
        self.ax.set_title("Histórico dos últimos 6 meses")
        self.ax.set_xlabel("Data")
        self.ax.set_ylabel("Preço (R$)")
        self.ax.legend()

        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())  # Exibe apenas rótulos mensais
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))  # Formato legível
        self.fig.autofmt_xdate(rotation=45)  # Rotaciona as datas automaticamente

        self.draw()

# def get_aca_info(codigo_acao):
    """
    Busca o preço, variação, volume e outros dados da ação ajustada usando o Yahoo Finance.
    """
#    print(f"[DEBUG] Buscando dados para: {codigo_acao}")
    
#    acao = yf.Ticker(codigo_acao)
#    historico = acao.history(period='1d')
#    # preco_atual = acao.history(period='1d')['Close'][0]

#    if historico.empty:
#        raise ValueError(f'Nenhum dados disponivel para a ação "{codigo_acao}". Verifique o código e tente #novamente.')
    
#    if 'Close' not in historico.columns or historico['Close'].empty:
#        raise ValueError(f'Dados de fechamento não encontrados para a ação "{codigo_acao}".')

#    preco_abertura = historico['Open'].iloc[0]
#    preco_fechamento = historico['Close'].iloc[0]
#    variacao = ((preco_fechamento - preco_abertura)/ preco_abertura)
#    volume = historico['Volume'].iloc[0]

#    dados = {
#        'preco_abertura': preco_abertura,
#        'preco_fechamento': preco_fechamento,
#        'variacao': variacao,
#        'volume': volume
#    }
#    return dados
worker = None

def on_button_click():
    global worker
    codigo_acao = text_input.text().strip().upper()
    if not codigo_acao:
        result_label.setText("Por favor, digite um código de ação válida.")
        return
    
    result_label.setText("Buscando dados...")
    button.setEnabled(False)

    #if worker is not None and worker.isRunning():
    #    worker.stop()
    #codigo_acao = text_input.text().strip()
    #if not codigo_acao:
    #    result_label.setText("Por favor, digite um código de ação válido.")
    #    return
    #if worker is not None:
    #    worker.stop()
    #codigo_acao = text_input.text().strip()
    #if not codigo_acao:
    #    result_label.setText("Por favor, digite um codigo de ação valido.")
    #    return
    
    #codigo_acao_ajustado = ajustar_codigo_para_mercado(codigo_acao_usuario)
    
    worker = AcaoWorker(codigo_acao)
    worker.dadosObtidos.connect(atualizar_interface)
    #worker.erro.connect(exibir_erro)
    worker.finished.connect(lambda: button.setEnabled(True))
    worker.start()

    #def atualizar_periodicamente():
    #    worker = AcaoWorker(codigo_acao)
    #    worker.dadosObtidos.connect(atualizar_interface)
    #    worker.start()

        #timer = QTimer()
        #timer.timeout.connect(atualizar_periodicamente)
        #timer.start(60000)

def verificar_alerta(preco_atual, limite_superior, limite_inferior):
    if preco_atual >= limite_superior:
        print("Alerta: Ação atingiu o limite superior!")
    elif preco_atual <= limite_inferior:
        print("Alerta: A ação atingiu o limite inferior")

def atualizar_interface(resultado):
    try:
        if isinstance(resultado, dict):
            preco_atual = resultado['preco']
            historico = resultado['historico']

            result_label.setText(f"Preço atual de {text_input.text().strip().upper()}: R$ {preco_atual:.2f}")

            grafico.plotar(historico)
        else:
            result_label.setText("Erro: Não foi possivel obter os dados da ação.")
    except Exception as e:
        result_label.setText(f"Erro ao processar os dados: {str(e)}")
    finally:
        button.setEnabled(True)

def atualizar_grafico(codigo_acao, historico):
    grafico.plotar(historico)
    result_label.setText(f"Gráfico do histórico de preços da ação {codigo_acao}")

def exibir_erro(mensagem):
    result_label.setText(f"Erro: {mensagem}")

    #try:
        # dados_acao = get_aca_info(codigo_acao_ajustado)
    #    historico = get_historico_acao(codigo_acao_ajustado)
    #    grafico.plotar(historico)
    #    result_label.setText(f"Gráfico do histórico de preços de ação {codigo_acao_usuario}.")
    #except ValueError as ve:
    #        result_label.setText(str(ve))
    #except Exception as e:
    #        result_label.setText(f"Erro ao buscar a ação: {str(e)}")
        
        #if dados_acao['variacao'] >= 0:
        #     variacao_text = f"+{dados_acao['variacao']:.2f}%"
        #     variacao_color = "green"
        #else:
        #     variacao_text = f"{dados_acao['variacao']:.2f}%"
        #     variacao_color = "red"
             
        #result_label.setText(f"""
        #Preço da Abertura: R$ {dados_acao['preco_abertura']:.2f}
        #Preço de Fechamento: R$ {dados_acao['preco_abertura']:.2f}
        #Variação: {dados_acao['variacao']:.2f}%
        #Volume de Negócios: {dados_acao['volume']:,}
        #""")
        
    # elif not validar_codigo(codigo_acao):
    #    result_label.setText("Codigo de ação inválido. Use letras e números.")   
    #else:
    #    try:         
    #        preco = get_acao_preco(codigo_acao)
    #        result_label.setText(f'Preço da ação {codigo_acao}: no valor de R$ {preco:2f}')
    # except ValueError as ve:
    #        result_label.setText(str(ve))
    # except Exception as e:
    #        result_label.setText(f"Erro ao buscar a ação: {str(e)}")


def ajustar_codigo_para_mercado(codigo_acao):
    """
    Ajusta o código da ação para incluir o mercado brasileiro (.SA)
se necessario
    """
    if not codigo_acao.upper().endswith('.SA'):
         codigo_acao += '.SA'
    return codigo_acao.upper()
    
    #mercados = {
     #   'BR': '.SA', 
     #   'US': '',
    #}
    # if not codigo_acao.endswith('.SA') and codigo_acao.isalpha():
    #    codigo_acao += '.SA'
    # print(f"Código ajustado para: ")
    # return codigo_acao


app = QApplication([])

window = QWidget()
window.setWindowTitle('Consulta de Ações com gráfico')

label = QLabel('Digite o código da ação (ex: LEVE3.SA)')
text_input = QLineEdit()
button = QPushButton("Consultar Gráfico")
result_label = QLabel("O gráfico aparecerá abaixo.")
#button.clicked.connect(on_button_click)
#result_label = QLabel("Preço da ação aparecerá aqui.")
grafico = GraficoCanvas()

# layout = QVBoxLayout()
# layout.addWidget(label)
# layout.addWidget(text_input)
# layout.addWidget(button)
# layout.addWidget(result_label)
# layout.addWidget(grafico)

# window.setLayout(layout)

button.clicked.connect(on_button_click)

class PlotlyGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        # # Layout do Widget
        # self.layout = QVBoxLayout()
        # self.setLayout(self.layout)
        
        # # WebEngineView para exibir o gráfico
        # self.webview.reload()  # Atualiza o gráfico no navegador embutido
        # self.layout.addWidget(self.webview)
        
    def initUI(self):
        self.setWindowTitle("Consulta de ações")
        self.setGeometr(100, 100, 800, 600)

        self.layout = QVBoxLayout()
        self.label = QLabel("Digite o código da ação (ex: APPL, TSLA, PETRA.SA):")
        self.text_input = QLineEdit()
        self.button = QPushButton("Buscar")
        self.result_label = QLabel("O gráfico aparecerá abaixo.")

        self.webview = QWebEngineView()

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.text_input)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.result_label)
        self.layout.addWidget(self.webview)

        self.setLayout(self.layout)
        self.button.clicked.connect(self.buscar_acao)


def buscar_acao(self):
    codigo_acao = self.text_input.text().strip().upper()
    if not codigo_acao:
        self.result_label.setText("Por favor, digite um código de ação válido.")
        return

    self.result_label.setText("Buscando dados...")
    historico = yf.Ticker(codigo_acao).history(period='5y')

    if historico.empty:
        self.result_label.setText("Nenhum dado encontrado para esta ação.")
        return

    self.gerar_grafico(codigo_acao, historico)

def gerar_grafico(self, codigo_acao, historico):
    



    def exibir_grafico(self, fig):
        # Gerar o HTML do gráfico
        html_content = fig.to_html(include_plotlyjs='cdn')

        # Criar um arquivo temporário para armazenar o HTML
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        with open(temp_file.name, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Garantir que o caminho está formatado corretamente para QWebEngineView
        fig.write_html("index.html", auto_open=False)  # Sobrescreve o HTML
        caminho_absoluto = os.path.abspath("index.html")
        file_url = QUrl.fromLocalFile(caminho_absoluto)
        self.webview.reload()  # Atualiza o gráfico no navegador embutido

        # Carregar o arquivo no WebView
        self.webview.setUrl(file_url)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Criar a Janela
    window = PlotlyGraph()
    window.setWindowTitle("Gráfico Interativo")

    # Criar os dados do gráfico
    x_data = ["2023-01-01", "2023-02-01", "2023-03-01"]
    y_data = [100, 150, 120]
    fig = go.Figure(data=go.Scatter(x=x_data, y=y_data, mode='lines', name='Preço'))
    fig.update_layout(title='Histórico de Preços', xaxis_title='Data', yaxis_title='Preço (R$)')

    # Exibir o gráfico
    window.exibir_grafico(fig)

    # Mostrar a janela
    window.show()
    sys.exit(app.exec_())


# class GraficoInterativo(QWidget):
    # def __init__(self, parent=None):
    #     super().__init__(parent)
    #     self.layout = QVBoxLayout(self)
    #     self.webview = QWebEngineView(self)
    #     self.layout.addWidget(self.webview)
    #     self.setLayout(self.layout)
    
    # def plotar(self, historico):
    #     fig = go.Figure()
    #     fig.add_trace(go.Scatter(
    #         x=historico.index,
    #         y=historico['Close'],
    #         mode='lines',
    #         name='Preço de Fechamento',
    #         line=dict(color='blue')
    #     ))
    #     fig.update_layout(
    #         title="Histórico de Preço de Ação",
    #         xaxis_title="Data",
    #         yaxis_title="Preço (R$)",
    #         xaxis=dict(rangeslider=dict(visible=True), type='date'),
    #         template="plotly_dark"
    #     )

    #     self.webview.setHtml(fig.to_html(include_plotlyjs='cdn'))
    #     html_content = fig.to_html(include_plotlyjs='cdn')
    #     self.webview.setHtml(html_content)
    #     print(html_content)

# grafico = GraficoInterativo()
# layout.addWidget(grafico)

# def close_event():
#     global worker
#     if worker is not None:
#         worker.stop()
#     app.quit()
# # window.resize(300, 200)
# window.closeEvent = close_event
# window.show()
# sys.exit(app.exec_())
# # app.exec_()



