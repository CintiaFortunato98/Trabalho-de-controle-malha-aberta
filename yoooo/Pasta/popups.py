from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from datetime import datetime
from time import sleep
from threading import Thread
import threading
from kivy.uix.boxlayout import BoxLayout
from timeseriesgraph import TimeSeriesGraph

class ModbusPopup(Popup):
    _info_lb = None
    def __init__(self, server_ip, server_port,**kwargs):
        """
        Construtor da classe ModbusPopup
        """
        super().__init__(**kwargs)
        self.ids.txt_ip.text = str(server_ip)
        self.ids.txt_port.text = str(server_port)

    def setInfo(self, message):
        self._info_lb = Label(text=message)
        self.ids.layout.add_widget(self._info_lb)

    def clearInfo(self):
        if self._info_lb is not None:
            self.ids.layout.remove_widget(self._info_lb)

class ScanPopup(Popup):
    def __init__(self, scantime, **kwargs):
        """
        Construtor da classe ScanPopup
        """
        super().__init__(**kwargs)
        self.ids.txt_st.text = str(scantime)

class EletricasPopup(Popup):
    def __init__(self, scan_time, lock, **kwargs):
        """
        Popup para mostrar medidas elétricas
        """
        self._meas = {}
        self.lock = lock
        self.tipo = 'fp'
        self.scan_time = scan_time
        super().__init__(**kwargs)

    def toggle_change(self, case):
        if case == 't':
            self.tipo = case
            self.ids.medida_titulo_a.text = 'Fase RS'
            self.ids.medida_titulo_b.text = 'Fase ST'
            self.ids.medida_titulo_c.text = 'Fase TR'
            self.ids.medida_titulo_d.text = 'Média'
            self.ids.medida_titulo_e.text = ''
            self.ids.medida_titulo_f.text = ''
            self.ids.medida_valor_e.text = ''
            self.ids.medida_valor_f.text = ''
        elif case == 'c':
            self.tipo = case
            self.ids.medida_titulo_a.text = 'Corrente R'
            self.ids.medida_titulo_b.text = 'Corrente S'
            self.ids.medida_titulo_c.text = 'Corrente T'
            self.ids.medida_titulo_d.text = 'Corrente N'
            self.ids.medida_titulo_e.text = 'Média'
            self.ids.medida_titulo_f.text = ''
            self.ids.medida_valor_f.text = ''
        elif case == 'd':
            self.tipo = case
            self.ids.medida_titulo_a.text = 'Anterior'
            self.ids.medida_titulo_b.text = 'Atual'
            self.ids.medida_titulo_c.text = 'Média'
            self.ids.medida_titulo_d.text = 'Prevista'
            self.ids.medida_titulo_e.text = ''
            self.ids.medida_titulo_f.text = ''
            self.ids.medida_valor_e.text = ''
            self.ids.medida_valor_f.text = ''
        elif case == 'fp':
            self.tipo = case
            self.ids.medida_titulo_a.text = 'Fase R'
            self.ids.medida_titulo_b.text = 'Fase S'
            self.ids.medida_titulo_c.text = 'Fase T'
            self.ids.medida_titulo_d.text = 'Total'
            self.ids.medida_titulo_e.text = ''
            self.ids.medida_titulo_f.text = ''
            self.ids.medida_valor_e.text = ''
            self.ids.medida_valor_f.text = ''
        elif case == 'thd':
            self.tipo = case
            self.ids.medida_titulo_a.text = 'RN'
            self.ids.medida_titulo_b.text = 'SN'
            self.ids.medida_titulo_c.text = 'TN'
            self.ids.medida_titulo_d.text = 'RS'
            self.ids.medida_titulo_e.text = 'ST'
            self.ids.medida_titulo_f.text = 'TR'
            
    def show_output(self, bt=0, bv=0, meas=0):
        self._meas = meas
        self.lock.acquire()
        if self.tipo == 't':
            self.ids['medida_valor_a'].text = str(self._meas['values']['tensao_rs']) + " V"
            self.ids['medida_valor_b'].text = str(self._meas['values']['tensao_st']) + " V"
            self.ids['medida_valor_c'].text = str(self._meas['values']['tensao_tr']) + " V"
            self.value4 = (self._meas['values']['tensao_rs'] + self._meas['values']['tensao_st'] + self._meas['values']['tensao_tr']) / 3
            self.ids['medida_valor_d'].text = str(round(self.value4/10, 1)) + " V"
        
        elif self.tipo == 'c':
            self.ids['medida_valor_a'].text = str(self._meas['values']['corrente_r']) + " A"
            self.ids['medida_valor_b'].text = str(self._meas['values']['corrente_s']) + " A"
            self.ids['medida_valor_c'].text = str(self._meas['values']['corrente_t']) + " A"
            self.ids['medida_valor_d'].text = str(self._meas['values']['corrente_n']) + " A"
            self.ids['medida_valor_e'].text = str(self._meas['values']['corrente_media']) + " A"

        elif self.tipo == 'd':
            self.ids['medida_valor_a'].text = str(self._meas['values']['demanda_anterior']) + " W"
            self.ids['medida_valor_b'].text = str(self._meas['values']['demanda_atual']) + " W"
            self.ids['medida_valor_c'].text = str(self._meas['values']['demanda_media']) + " W"
            self.ids['medida_valor_d'].text = str(self._meas['values']['demanda_prevista']) + " W"

        elif self.tipo == 'fp':
            self.ids['medida_valor_a'].text = str(self._meas['values']['fp_r'])
            self.ids['medida_valor_b'].text = str(self._meas['values']['fp_s'])
            self.ids['medida_valor_c'].text = str(self._meas['values']['fp_t'])
            self.ids['medida_valor_d'].text = str(self._meas['values']['fp_total'])

        elif self.tipo == 'thd':
            self.ids['medida_valor_a'].text = str(self._meas['values']['thd_tensao_rn']) + " %"
            self.ids['medida_valor_b'].text = str(self._meas['values']['thd_tensao_sn']) + " %"
            self.ids['medida_valor_c'].text = str(self._meas['values']['thd_tensao_tn']) + " %"
            self.ids['medida_valor_d'].text = str(self._meas['values']['thd_tensao_rs']) + " %"
            self.ids['medida_valor_e'].text = str(self._meas['values']['thd_tensao_st']) + " %"
            self.ids['medida_valor_f'].text = str(self._meas['values']['thd_tensao_tr']) + " %"
        self.lock.release()

class Metodos():
    def __init__(self, clienteModbus, tagsMotor, lock):
        self._tagsMotor = tagsMotor
        self._cliente =  clienteModbus
        self._lock = lock

    def acionaMotor(self, key, estado):
        if estado == 'on':
                self.escreveDado(self._tagsMotor, key, 1)
                print(0)
        if estado == 'off':
                self.escreveDado(self._tagsMotor, key, 0)
                print(1)
        if estado == 'reset':
                self.escreveDado(self._tagsMotor, key, 2)
                print(2)
                
    def mudaVelocidade(self, key, valor):
        self.escreveDado(self._tagsMotor, key, valor)
        print(key)
        print(self._tagsMotor[key]["valor"])
    
    def mudaAceleracao(self, key, valor):
        self.escreveDado(self._tagsMotor, key, valor)
        print(key)
        print(self._tagsMotor[key]["valor"])
    
    def mudaDesaceleracao(self, key, valor):
        self.escreveDado(self._tagsMotor, key, valor)
        print(key)
        print(self._tagsMotor[key]["valor"])

    def escreveDado(self, tagsMotor, key, valor):
            """
            Método para a escrita de dados na Tabela MODBUS
            """
            self._lock.acquire()
            self._tagsMotor = tagsMotor
            self._tagsMotor[key]["valor"] = valor
            self._tagsMotor[key]["timestamp"] = datetime.now()
            if self._tagsMotor[key]["tamanho"] == 16:
                self._cliente.write_single_register(self._tagsMotor[key]["addr"],valor)
            
            elif self._tagsMotor[key]["tamanho"] == 32:
                buider = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
                buider.add_32bit_float(valor)
                payload = buider.to_registers() 
                self._cliente.write_multiple_registers(self._tagsMotor[key]["addr"],payload)
            self._lock.release()
   
class softPopup(Popup):  
    def __init__(self, acoes):
        """
        Popup para controlar a partida por Soft Starter
        """       
        super().__init__()
        self._acoes = acoes
         
class inversorPopup(Popup):   
    def __init__(self, acoes):
        """
        Popup para controlar a partida por Invsor de frequência
        """
        super().__init__()
        self._acoes = acoes
             
class diretaPopup(Popup):   
    def __init__(self, acoes):
        """
        Popup para controlar a partida por Invsor de frequência
        """
        super().__init__()
        self._acoes = acoes

class CompressorPopup(Popup):
    _updateThread = None
    _updateWidgets = True
    _tags = {}
    def __init__(self, scantime, modbusClient, lock, **kwargs):

        super().__init__(**kwargs)
        # Cria um lock
        self.lock = lock
        self._scan_time = scantime
        # self._modbusPopup = ModbusPopup(server_ip=server_ip, server_port=server_port)
        # self._scanPopup = ScanPopup(scantime=self._scan_time)
        
        self._modbusClient = modbusClient

        # estrutura para a leitura de dados
        self._meas = {}
        self._meas['timestamp'] = None
        self._meas['values'] = {}

    def writeData(self, valor, addr):
        self.lock.acquire()
        self._modbusClient.write_single_register(reg_addr=addr, reg_value=valor)
        self.lock.release()

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

    def lerDadoRegistradorBits(self, addr):

        """
        Lê o registrador e retorna a lista de bits
        """
        # pegando informações do registrador 1328
        self.lock.acquire()
        valor = self._modbusClient.read_holding_registers(reg_addr=addr, reg_nb=1)[0] # faz outra leitura aqui
        self.lock.release()
        binary_string = format(valor, '016b')
        lista_bits = ([int(bit) for bit in binary_string])
        return list(reversed(list(lista_bits)))

    def checkbox_activated(self, checkbox_name, value):

        """
        Verifica se o checkbox dos aquecedores e do compressor estão ativos e modifica os endereços

        """

        lista_bit_1328 = self.lerDadoRegistradorBits(addr=1328)
        lista_bit_1329 = self.lerDadoRegistradorBits(addr=1329)

        if checkbox_name == 'aquecedor_1':

            if value: # liga o aquecedor 1 se o checkbox está selecionado
                lista_bit_1329[4] = 1
                lista_bit_1329[5] = 0 
                
            else: # desliga o aquecedor 1 se o checkbox não estiver selecionado
                lista_bit_1329[5] = 1 
                lista_bit_1329[4] = 0

        if checkbox_name == 'aquecedor_2':

            if value: # liga o aquecedor 2 se o checkbox está selecionado
                lista_bit_1329[6] = 1 
                lista_bit_1329[7] = 0


            else: # desliga o aquecedor 2 se o checkbox não estiver selecionado
                lista_bit_1329[6] = 0
                lista_bit_1329[7] = 1 # desliga aquecedor 2 

        
        elif checkbox_name == 'compressor':

            # se o checkbox estiver selecionado, liga o compressor
            if value:
                lista_bit_1328[4] = 1 # bit 4: ligar compressor selecionado
                lista_bit_1329[0] = 1
                # print('Lista 1231 ON: ', lista_bit_1231)
            else:
                lista_bit_1329[0] = 0 # bit 0: desligar compressor selecionado
                lista_bit_1328[4] = 0
                # print('Lista 1231 OFF: ', lista_bit_1231)

        # coloca o novo valor no endereço 1328
        # print('Lista modificada 1328: ', lista_bit_1328)
        dado_novo_1328 = int(''.join(map(str, reversed(lista_bit_1328))), 2)
        print(dado_novo_1328)
        self.writeData(valor=dado_novo_1328, addr=1328)
            
        # coloca o novo valor no endereço 1329 
        # print('Lista modificada 1329: ', lista_bit_1329)
        dado_novo_1329 = int(''.join(map(str, reversed(lista_bit_1329))), 2)
        print(dado_novo_1329)
        self.writeData(valor=dado_novo_1329, addr=1329)

class HistGraphPopup(Popup):

    def __init__(self, tags, **kwargs):

        """
        Construtor do gráfico histórico das tags
        """
        super().__init__(**kwargs)
        for key, value in tags.items():
            cb = LabeledCheckBoxHistGraph()
            cb.ids.label.text = key
            cb.ids.label.color = value['color']
            cb.id = key
            self.ids.sensores.add_widget(cb)

class LabeledCheckBoxHistGraph(BoxLayout):
    pass

class TemperaturaPopup(Popup):
    def __init__(self, scan_time, lock, **kwargs):
        """
        Popup para mostrar medidas elétricas
        """
        self._meas = {}
        self.lock = lock
        self.tipo = 'fp'
        self.scan_time = scan_time
        super().__init__(**kwargs)

    def show_output(self, bt=0, bv=0, meas=0):
        self._meas = meas
        self.lock.acquire()
        self.ids['medida_valor_a'].text = str(self._meas['values']['temp_r']) + " °C"
        self.ids['medida_valor_b'].text = str(self._meas['values']['temp_s']) + " °C"
        self.ids['medida_valor_c'].text = str(self._meas['values']['temp_t']) + " °C"
        self.ids['medida_valor_d'].text = str(self._meas['values']['temp_carc']) + " °C"
        self.lock.release()
