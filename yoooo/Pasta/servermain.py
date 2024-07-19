from pyModbusTCP.server import DataBank, ModbusServer
import random
from time import sleep
from bitstring import BitArray


class ServidorMODBUS():
    """
    Classe Servidor Modbus
    """

    def __init__(self, host_ip, port):
        """
        Construtor
        """
        self._db = DataBank()
        self._server = ModbusServer(
            host=host_ip, port=port, no_block=True, data_bank=self._db)
        
        

    def run(self):
        """
        Execução do servidor Modbus
        """
        try:
            self._server.start()
            print("Servidor MODBUS em execução")
            bitlist=[0,0,1,1,0,1,0,0]
            comp = BitArray(bitlist)
            bitlistt=[0,1,1,0,0,0,0,0]
            estados = BitArray(bitlistt)
            bitlisttt=[0,1,1,0,0,0,1,0]
            estadosss = BitArray(bitlisttt)
            bitlistttt=[0,0,0,0,0,0,0,0]
            yeye = BitArray(bitlistttt)
            modbus_addr = {
                "temp_r": [700, "fp", 11, 0],
                "temp_s": [702, "fp", 11, 0],
                "temp_t": [704, "fp", 11, 0],
                "temp_carc": [706, "fp", 11, 0],
                "tipo_motor": [708, "4x", 1, 1],
                "temp_saida": [710, "fp", 1, 1],
                "vel_saida": [712, "fp", 1, 1],
                "vazao_saida": [714, "fp", 1, 1],
                "thd_tensao_rn": [800, "4x", 11, 0],
                "thd_tensao_sn": [801, "4x", 11, 0],
                "thd_tensao_tn": [802, "4x", 11, 0],
                "thd_tensao_rs": [804, "4x", 11, 0],
                "thd_tensao_st": [805, "4x", 11, 0],
                "thd_tensao_tr": [806, "4x", 11, 0],
                "corrente_r": [840, "4x", 11, 0],
                "corrente_s": [841, "4x", 11, 0],
                "corrente_t": [842, "4x", 11, 0],
                "corrente_n": [843, "4x", 11, 0],
                "corrente_media": [845, "4x", 11, 0],
                "tensao_rs": [847, "4x", 11, 0],
                "tensao_st": [848, "4x", 11, 0],
                "tensao_tr": [849, "4x", 11, 0],
                "fp_r": [868, "4x", 1001, 0],
                "fp_s": [869, "4x", 1001, 0],
                "fp_t": [870, "4x", 1001, 0],
                "fp_total": [871, "4x", 1001, 0],
                "encoder": [884, "fp", 1, 1],
                "demanda_anterior": [1204, "4x", 11, 0],
                "demanda_atual": [1205, "4x", 11, 0],
                "demanda_media": [1206, "4x", 11, 0],
                "demanda_prevista": [1207, "4x", 11, 0],
                "tit_2": [1218, "fp", 11, 0],
                "tit_1": [1220, "fp", 11, 0],
                "pit_2": [1222, "fp", 11, 0],
                "pit_1": [1224, "fp", 11, 0],
                "st_compressor": [1230, "4x", 1, 1],
                "vel_scroll": [1236, "4x", 1, 1],
                "atv31": [1312, "4x", 1, 1],
                "ats48": [1316, "4x", 1, 1],
                "tesys": [1319, "4x", 1, 1],
                "liga_compressor": [1328, "4x", 1, 1],
                "st_aquecedor": [1329, "4x", 1, 1],
                "torque_radial1": [1422, "fp", 1, 1],
                "torque_axial1": [1424, "fp", 1, 1]
            }
            self._tags = {}
            for key, value in modbus_addr.items():
                self._tags[key] = {'addr': value[0], 'type': value[1], 'multiplier': value[2], 'valor': value[3]}
                print(12)
                self._db.set_holding_registers(self._tags[key]['addr'], [self._tags[key]['valor']*self._tags[key]['multiplier']])
                print(13)
            while True:
                print('======================')
                print("Tabela MODBUS")
                for key, value in modbus_addr.items():
                    print('Holding Register R', self._tags[key]['addr'], self._tags[key]['type'], key, ': ', self._db.get_holding_registers(self._tags[key]['addr'])[0])
                sleep(1)
        except Exception as e:
            print("Erro: ", e.args)


s = ServidorMODBUS('localhost', 502)
s.run()
