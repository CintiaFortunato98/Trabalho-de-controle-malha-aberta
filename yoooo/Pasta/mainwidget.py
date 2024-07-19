from kivy.uix.boxlayout import BoxLayout
from popups import EletricasPopup, ModbusPopup, ScanPopup, softPopup, inversorPopup, diretaPopup, Metodos, CompressorPopup, HistGraphPopup, TemperaturaPopup
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian
from pyModbusTCP.client import ModbusClient
from kivy.core.window import Window
from datetime import datetime
from time import sleep
from threading import Thread
import threading
import random
from kivy.clock import Clock
from kivy_garden.graph import Graph, LinePlot
from bdhandler_teste import BDHandler
from functools import partial

class MainWidget(BoxLayout):

    _updateThread = None
    _updateWidgets = True
    _tags = {}

    def __init__(self, scantime, server_ip, server_port, modbus_addr, tagsMotor, tagsFlap, tagsSensores, db_path, **kwargs):
        valid_kwargs = {k: v for k, v in kwargs.items() if k in ['valid_property_1', 'valid_property_2']}
        super().__init__(**kwargs)
        # Cria um lock
        self._ev = 0
        self.source = 0
        self.st = 0
        self.lock = threading.Lock()
        self._scan_time = scantime
        self._scanPopup = ScanPopup(scantime=self._scan_time)
        self._serverIP = server_ip
        self._serverPort = server_port
        self._modbusClient = ModbusClient(
            host=self._serverIP, port=self._serverPort)
        self._meas = {}
        self._meas['timestamp'] = None
        self._meas['values'] = {}
        for key, value in modbus_addr.items():
            if key == 'st_aquecedor_1':
                plot_color = (1, 0, 0, 1)
            else:
                plot_color = (random.random(), random.random(),
                              random.random(), 1)
            self._tags[key] = {'addr': value[0], 'color': plot_color,
                               'type': value[1], 'multiplier': value[2]}
        self._tagsMotor = tagsMotor
        self._acoes = Metodos(
            clienteModbus=self._modbusClient, tagsMotor=self._tagsMotor, lock=self.lock)
        self._softPopup = softPopup(acoes=self._acoes)
        self._inversorPopup = inversorPopup(acoes=self._acoes)
        self._diretaPopup = diretaPopup(acoes=self._acoes)
        self._modbusPopup = ModbusPopup(
            server_ip=server_ip, server_port=server_port)
        self._scanComp = CompressorPopup(self._scan_time, self._modbusClient, lock=self.lock) # ja cria o cliente modbus
        self._hgraph = HistGraphPopup(tags=self._tags)
        self._db = BDHandler(dbpath=db_path, tablename='database',tags=self._tags)
        self._medidaseletricas = EletricasPopup(scan_time=self._scan_time, lock=self.lock)
        self._medidastemperatura = TemperaturaPopup(scan_time=self._scan_time, lock=self.lock)


    def startDataRead(self, ip, port):
        """
        Inicializa uma thread para leitura dos dados e atualização da interface
        """
        self._serverIP = ip
        self._serverPort = port
        self._modbusClient.host = self._serverIP
        self._modbusClient.port = self._serverPort
        try:
            Window.set_system_cursor("wait")
            if not self._modbusClient:
                raise ValueError("Modbus client não inicializado corretamente")
            self._modbusClient.open()
            Window.set_system_cursor("arrow")
            if self._modbusClient.is_open:
                print('Iniciando Thread')
                self.ids.img_con.source = '../imagens/connected.png'
                print('Updater metodo: ', self.updater)
                self._updateThread = Thread(target=self.updater)
                print('Update: ', self._updateThread)
                self._updateThread.start()
                self.ids.servidor_status.text = 'Status: Conectado'
                self.ids.servidor_status.color = (0, 1, 0, 1)
                self._modbusPopup.dismiss()
            else:
                self._modbusPopup.setInfo("Falha na conexão com o servidor")
        except Exception as e:
            print("Erro: ", e.args)

    def updater(self):
        """
        Leitura dos dados e atualização da interface
        Inserção dos dados do BD
        """
        
        try:
            while self._updateWidgets:
                # ler os dados modbus
                self.readData()
                # atualizar a interface
                print('Print meas updater: ',self._meas)
                self._db.insert_data(self._meas)
                self.updateGUI()
                # inserir os dados no banco de dados
                sleep(self._scan_time/1000)
        except Exception as e:
            self._modbusClient.close()
            print("Erro: ", e.args)

    def readData(self):
        """
        Método para a leitura dos dados do servidor Modbus
        """
        self._meas['timestamp'] = datetime.now()
        for key, value in self._tags.items():
            print('value readData: ', value)
            self.lock.acquire()
            
            if value['type'] == "fp":
                try:
                    dado = self._modbusClient.read_holding_registers(value['addr'], 2)
                    if dado:
                        decoder = BinaryPayloadDecoder.fromRegisters(dado, byteorder=Endian.BIG, wordorder=Endian.LITTLE)
                        valor_float = decoder.decode_32bit_float()
                        self._meas['values'][key] = round(valor_float / value['multiplier'], 2)
                    else:
                        print(f"Erro ao ler dado do Modbus para {key}")
                finally:
                    self.lock.release()
            elif value['type'] == "4x":
                dado = self._modbusClient.read_holding_registers(
                    value['addr'], 1)[0]
                self._meas['values'][key] = dado / value['multiplier']
                self.lock.release()

    def writeData(self, valor, addr):
        self.lock.acquire()
        try:
            self._modbusClient.write_single_register(reg_addr=addr, reg_value=valor)
        finally:
            self.lock.release()

    def updateGUI(self):
        """
        Método para atualizar a interface gráfica com a leitura dos sensores e 
        status do compressor e aquecedor
        """
        for key, value in self._tags.items():
            if key == 'tit_1' or key == 'tit_2' or key == 'temp_saida':
                self.ids[key].text = str(self._meas['values'][key]) + ' °C'
            elif key == 'pit_1' or key == 'pit_2':
                self.ids[key].text = str(self._meas['values'][key]) + ' PSI'
            elif key == 'vel_saida':
                self.ids[key].text = str(self._meas['values'][key]) + ' m/s'
            elif key == 'vazao_saida':
                self.ids[key].text = str(self._meas['values'][key]) + ' m³/h'
            elif key == 'vel_scroll':
                self.ids[key].text = str(self._meas['values'][key]) + ' Hz'
            elif key == 'encoder':
                self.ids[key].text = str(self._meas['values'][key]) + ' RPM'
            elif key == 'tipo_motor':
                if self._meas['values'][key] == 1:
                    self.ids[key].text = "VERDE"
                elif self._meas['values'][key] == 2:
                    self.ids[key].text = "AZUL"

        # faz a leitura e o update da GUI do status do compressor e do aquecedor
        self.leitura_aquecedor()
        self.leitura_compressor()
        self.leitura_ventilador()
        self._medidaseletricas.show_output(bt=0, bv=0, meas=self._meas)
        self._medidastemperatura.show_output(bt=0, bv=0, meas=self._meas)
        # Expandir nisso

    def leitura_aquecedor(self):
        # leitura do status dos aquecedores e atualização da interface
        lista_bit = self.lerDadoRegistradorBits(addr=1231)
        status_aq_1 = lista_bit[2]
        status_aq_2 = lista_bit[3]

        if status_aq_1 == 1:
            self.ids.st_aquecedor_1.text = 'Ligado'
            self.ids.st_aquecedor_1.color = (1, 1, 1, 1)
            self.source = 'img_aquecedor_1'
            self.st = 'ligado'
            self._ev = Clock.schedule_once(self.changeImage)
        else:
            self.ids.st_aquecedor_1.text = 'Desligado'
            self.ids.st_aquecedor_1.color = (0, 0, 0, 1)
            self.source = 'img_aquecedor_1'
            self.st = 'desligado'
            self._ev = Clock.schedule_once(self.changeImage)

        if status_aq_2 == 1:
            self.ids.st_aquecedor_2.text = 'Ligado'
            self.ids.st_aquecedor_2.color = (1, 1, 1, 1)
            self.source = 'img_aquecedor_2'
            self.st = 'ligado'
            self._ev = Clock.schedule_once(self.changeImage)
        else:
            self.ids.st_aquecedor_2.text = 'Desligado'
            self.ids.st_aquecedor_2.color = (0, 0, 0, 1)
            self.source = 'img_aquecedor_2'
            self.st = 'desligado'
            self._ev = Clock.schedule_once(self.changeImage)

    def leitura_compressor(self):
        """
        Lê o status do compressor selecionado
        """
        lista_bit = self.lerDadoRegistradorBits(addr=1231)
        # lista_bit = list(reversed(lista_bit))
        # status do compressor selecionado (ligado/desligado)
        status_compressor = lista_bit[5]

        # pegando informações do registrador 1328
        lista_bit_1328 = self.lerDadoRegistradorBits(addr=1328)
        # se o compressor scroll esta selecionado
        if lista_bit_1328[1] == 0:
            self.ids.selecionado_compressor_scroll.text = 'SELECIONADO'
            self.ids.selecionado_compressor_hermetico.text = ''
            if status_compressor == 1:
                self.ids.st_compressor_scroll.text = 'LIGADO'
                self.ids.st_compressor_scroll.color = (1, 1, 1, 1)
            else:
                self.ids.st_compressor_scroll.text = 'DESLIGADO'
                self.ids.st_compressor_scroll.color = (0, 0, 0, 1)
        # se o compressor hermetico esta selecionado
        else:
            self.ids.selecionado_compressor_hermetico.text = 'SELECIONADO'
            self.ids.selecionado_compressor_scroll.text = ''
            if status_compressor == 1:
                self.ids.st_compressor_hermetico.text = 'LIGADO'
                self.ids.st_compressor_hermetico.color = (1, 1, 1, 1)
            else:
                self.ids.st_compressor_hermetico.text = 'DESLIGADO'
                self.ids.st_compressor_hermetico.color = (0, 0, 0, 1)

    # CONFERIR SE ANALISE DE MOTOR LIGADO/DESLIGADO TA CERTO
    def leitura_ventilador(self):
        # leitura do status do ventilador
        lista_bit_1328 = self.lerDadoRegistradorBits(addr=1328)
        lista_bit_1230 = self.lerDadoRegistradorBits(addr=1230)
        # se tipo de ventilador é o radial
        if lista_bit_1328[2] == 0:
            self.ids.tipo_vent.text = 'RADIAL'
            # se ventilador ligado
            if lista_bit_1230[6] == 0:
                self.ids.st_vent.text = 'LIGADO'
                self.ids.st_vent.color = (1, 1, 1, 1)
            else:
                self.ids.st_vent.text = 'DESLIGADO'
                self.ids.st_vent.color = (0, 0, 0, 1)
            # se motor ligado
            if self._meas['values']['atv31'] == 1 or self._meas['values']['ats48'] == 1 or self._meas['values']['tesys'] == 1:
                self.source = 'img_ventilador_radial'
                self.st = 'ligado'
                self._ev = Clock.schedule_once(self.changeImage)
                self.ids.st_motor.text = 'LIGADO'
                self.ids.st_motor.color = (1, 1, 1, 1)
                #imagem muda de acordo com motor ligado/desligado, radial/axial, azul/verde
            else:
                self.source = 'img_ventilador_radial'
                self.st = 'desligado'
                self._ev = Clock.schedule_once(self.changeImage)
                self.ids.st_motor.text = 'DESLIGADO'
                self.ids.st_motor.color = (0, 0, 0, 1)
            self.ids['torque'].text = str(self._meas['values']['torque_radial1']) + ' N*m'
        # se tipo de ventilador é o axial
        else:
            self.ids.tipo_vent.text = 'AXIAL'
            # se ventilador ligado
            if lista_bit_1230[6] == 0:
                self.ids.st_vent.text = 'LIGADO'
                self.ids.st_vent.color = (1, 1, 1, 1)
            else:
                self.ids.st_vent.text = 'DESLIGADO'
                self.ids.st_vent.color = (0, 0, 0, 1)
            # se motor ligado
            if self._meas['values']['atv31'] == 1 or self._meas['values']['ats48'] == 1 or self._meas['values']['tesys'] == 1:
                self.source = 'img_ventilador_axial'
                self.st = 'ligado'
                self._ev = Clock.schedule_once(self.changeImage)
                self.ids.st_motor.text = 'LIGADO'
                self.ids.st_motor.color = (1, 1, 1, 1)
                #imagem muda de acordo com motor ligado/desligado, radial/axial, azul/verde
            else:
                self.source = 'img_ventilador_axial'
                self.st = 'desligado'
                self._ev = Clock.schedule_once(self.changeImage)
                self.ids.st_motor.text = 'DESLIGADO'
                self.ids.st_motor.color = (0, 0, 0, 1)
            self.ids['torque'].text = str(self._meas['values']['torque_axial1']) + ' N*m'

    def lerDadoRegistradorBits(self, addr):
        """
        Lê o registrador e retorna a lista de bits
        """
        self.lock.acquire()
        valor = self._modbusClient.read_holding_registers(reg_addr=addr, reg_nb=1)[0]
        self.lock.release()
        binary_string = format(valor, '016b')
        lista_bits = ([int(bit) for bit in binary_string])
        return list(reversed(list(lista_bits)))

    def seleciona_compressor(self, tipo):
        """"
        Seleciona o tipo de compressor e modifica o valor presente no endereço
        """
        lista_bit = self.lerDadoRegistradorBits(addr=1328)
        print(tipo)

        if tipo == 'hermetico':
            lista_bit[1] = 0 # bit 1: seleciona o tipo de compressor utilizado (0-scroll, 1-hermetico)
        else:
            lista_bit[1] = 1 # bit 1: seleciona o tipo de compressor utilizado (0-scroll, 1-hermetico)

        # coloca o novo valor no endereço 1328
        print('Lista modificada 1328: ', lista_bit)
        dado_novo = int(''.join(map(str, lista_bit)), 2)
        print(dado_novo)
        self.writeData(valor=dado_novo, addr=1328)

    def stopRefresh(self):
        self._updateWidgets = False

    def getDataDB(self):
        """
        Método que coleta as informações da interface fornecidas pelo usuário
        """
        try:
            init_t = self.parseDTString(self._hgraph.ids.txt_init_time.text)
            final_t = self.parseDTString(self._hgraph.ids.txt_final_time.text)
            cols = []

            for sensor in self._hgraph.ids.sensores.children:
                if sensor.ids.checkbox.active:
                    cols.append(sensor.id)  # Assume que `sensor.id` seja o nome da coluna correspondente

            if init_t is None or final_t is None or len(cols) == 0:
                return

            # Seleciona os dados do banco de dados com base nas condições fornecidas
            dados = self._db.select_data(start_time=init_t, end_time=final_t, columns=cols)

            print('dados filtrados: ', dados)

            # Verifica se os dados foram retornados
            if not dados or len(dados) == 0:
                raise ValueError("Nenhum dado encontrado para as condições fornecidas.")
            
            # Organiza os dados em um dicionário com listas
            dados_dict = {col: [] for col in cols}
            dados_dict['timestamp'] = []
            for row in dados:
                dados_dict['timestamp'].append(row['timestamp'])
                for col in cols:
                    dados_dict[col].append(row[col])

            # Limpa os gráficos antigos
            self._hgraph.ids.graph.clearPlots()

            print('Dados dict: ', dados_dict)
            # Adiciona os novos dados ao gráfico
            for key, value in dados_dict.items():
                if key == 'timestamp':
                    continue
                p = LinePlot(line_width=1.5, color=self._tags[key]['color'])
                p.points = [(x, value[x]) for x in range(len(value))]
                self._hgraph.ids.graph.add_plot(p)
            
            # Atualiza os labels do eixo X do gráfico
            self._hgraph.ids.graph.xmax = len(dados_dict['timestamp'])
            self._hgraph.ids.graph.update_x_labels([datetime.strptime(x, "%Y-%m-%d %H:%M:%S") for x in dados_dict['timestamp']])

        except Exception as e:
            print("Erro: ", e.args)

    def parseDTString(self, datetime_str):
        try:
            datetime_str = datetime_str.strip()
            d = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
            return d.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print("Erro parseDTString: ", e.args)

    def mudaPartida(self, partida):
        if partida == "soft":
            self._modbusClient.write_single_register(self._tagsMotor["sel_driver"]["addr"], 1) # define o tipo de partida como softstarter
            print("soft")
        if partida == "inversor":
            self._modbusClient.write_single_register(self._tagsMotor["sel_driver"]["addr"], 2) # define o tipo de partida como softstarter
            print("inversor")
        if partida == "direta":
            self._modbusClient.write_single_register(self._tagsMotor["sel_driver"]["addr"], 3) # define o tipo de partida como softstarter
            print("direta")

    def changeImage(self, dt):
        if self.source == 'img_aquecedor_1':
            if self.st == 'ligado':
                self.ids.img_aquecedor_1.source = '../imagens/aquecedor.png'
            else:
                self.ids.img_aquecedor_1.source = '../imagens/vazio.png'
        elif self.source == 'img_aquecedor_2':
            if self.st == 'ligado':
                self.ids.img_aquecedor_2.source = '../imagens/aquecedor.png'
            else:
                self.ids.img_aquecedor_2.source = '../imagens/vazio.png'
        elif self.source == 'img_ventilador_axial':
            if self.st == 'ligado':
                self.ids.img_ventilador.source = '../imagens/axial_ligado.png'
            else:
                self.ids.img_ventilador.source = '../imagens/axial_desligado.png'
        elif self.source == 'img_ventilador_radial':
            if self.st == 'ligado':
                self.ids.img_ventilador.source = '../imagens/radial_ligado.png'
            else:
                self.ids.img_ventilador.source = '../imagens/radial_desligado.png'