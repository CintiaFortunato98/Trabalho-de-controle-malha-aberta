import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
from kivy.app import App
from mainwidget import MainWidget
from kivy.lang.builder import Builder
from kivy.core.window import Window

class MainApp(App):

    def build(self):
        modbus_addrs = {
            "temp_r": [700, "fp", 10],
            "temp_s": [702, "fp", 10],
            "temp_t": [704, "fp", 10],
            "temp_carc": [706, "fp", 10],
            "tipo_motor": [708, "4x", 1],
            "temp_saida": [710, "fp", 1],
            "vel_saida": [712, "fp", 1],
            "vazao_saida": [714, "fp", 1],
            "thd_tensao_rn": [800, "4x", 10],
            "thd_tensao_sn": [801, "4x", 10],
            "thd_tensao_tn": [802, "4x", 10],
            "thd_tensao_rs": [804, "4x", 10],
            "thd_tensao_st": [805, "4x", 10],
            "thd_tensao_tr": [806, "4x", 10],
            "corrente_r": [840, "4x", 10],
            "corrente_s": [841, "4x", 10],
            "corrente_t": [842, "4x", 10],
            "corrente_n": [843, "4x", 10],
            "corrente_media": [845, "4x", 10],
            "tensao_rs": [847, "4x", 10],
            "tensao_st": [848, "4x", 10],
            "tensao_tr": [849, "4x", 10],
            "fp_r": [868, "4x", 1000],
            "fp_s": [869, "4x", 1000],
            "fp_t": [870, "4x", 1000],
            "fp_total": [871, "4x", 1000],
            "encoder": [884, "fp", 1],
            "demanda_anterior": [1204, "4x", 10],
            "demanda_atual": [1205, "4x", 10],
            "demanda_media": [1206, "4x", 10],
            "demanda_prevista": [1207, "4x", 10],
            "tit_2": [1218, "fp", 10],
            "tit_1": [1220, "fp", 10],
            "pit_2": [1222, "fp", 10],
            "pit_1": [1224, "fp", 10],
            "st_compressor": [1230, "4x", 1],
            "vel_scroll": [1236, "4x", 1],
            "atv31": [1312, "4x", 1],
            "ats48": [1316, "4x", 1],
            "tesys": [1319, "4x", 1],
            "liga_compressor": [1328, "4x", 1],
            "st_aquecedor": [1329, "4x", 1],
            "torque_radial1": [1422, "fp", 1],
            "torque_axial1": [1424, "fp", 1]
        }
        tagsMotor = {
            # velocidade do motor e tipo do motor
            # mostra velocidade do motor em RPM
            "status_velocidade_motor": {"addr": 884, "tamanho": 32, "tipo": 'leitura', "valor": None, "timestamp": None},
            # mostra tipo do motor (1 - Verde e 2 - Azul)
            "status_tipo_motor": {"addr": 708, "tamanho": 16, "tipo": 'leitura', "valor": None, "timestamp": None},

            # tipo de partida
            # seleção tipo de partida (1 - Soft, 2 - Inversor, 3 - Direta)
            "sel_driver": {"addr": 1324,  "tamanho": 16, "tipo": 'escrita', "valor": None, "timestamp": None},
            # mostra tipo do driver
            "ve.indica_driver": {"addr": 1216,  "tamanho": 16, "tipo": 'leitura', "valor": None, "timestamp": None},

            # inversor de frequencia
            # on/off motor (0 - Desliga, 1 - Liga, 2 - Reset)
            "sel_partida_inversor":       {"addr": 1312, "tamanho": 16, "valor": None, "timestamp": None},
            # seleciona velocidade (x10) (0Hz a 60Hz)
            "sel_velocidade_inversor":    {"addr": 1313, "tamanho": 16, "valor": None, "timestamp": None},
            # seleciona aceleração (x10) (10s a 60s)
            "sel_aceleracao_inversor":    {"addr": 1314, "tamanho": 16, "valor": None, "timestamp": None},
            # seleciona desaceleração (x10) (10s a 60s)
            "sel_desaceleracao_inversor": {"addr": 1315, "tamanho": 16, "valor": None, "timestamp": None},

            # soft starter
            # on/off motor (0 - Desliga, 1 - Liga, 2 - Reset)
            "sel_partida_soft":       {"addr": 1316, "tamanho": 16, "valor": None, "timestamp": None},
            # seleciona aceleração (x10) (10s a 60s)
            "sel_aceleracao_soft":    {"addr": 1317, "tamanho": 16, "valor": None, "timestamp": None},
            # seleciona desaceleração (x10) (10s a 60s)
            "sel_desaceleracao_soft": {"addr": 1318, "tamanho": 16, "valor": None, "timestamp": None},

            # direta
            # on/off motor (0 - Desliga, 1 - Liga, 2 - Reset)
            "sel_partida_direta": {"addr": 1319, "tamanho": 16, "valor": None, "timestamp": None},
        }

        tagsFlap = {
            # seleciona tipo de PID (Automático = 0 e Manual = 1)
            "sel_pid": {"addr": 1332,  "tamanho": 16, "tipo": 'escrita', "valor": None, "timestamp": None},
            # mostra tipo de PID
            "status_pid": {"addr": 722,  "tamanho": 16, "tipo": 'leitura', "valor": None, "timestamp": None},
            # 0 a 100
            "pos_flap": {"addr": 1310, "tamanho": 32, "tipo": 'escrita', "valor": None, "timestamp": None}
        }

        tagsSensores = {
            # /10
            "status_tit03":       {"addr": 1226, "tamanho": 32, "tipo": 'leitura', "valor": None, "timestamp": None},
            "status_vazao":       {"addr": 714,  "tamanho": 32, "tipo": 'leitura', "valor": None, "timestamp": None},
            "status_velocidade":  {"addr": 712,  "tamanho": 32, "tipo": 'leitura', "valor": None, "timestamp": None},
            "status_temperatura": {"addr": 710,  "tamanho": 32, "tipo": 'leitura', "valor": None, "timestamp": None},
        }
        db_path = 'database.db'
        # self._widget = MainWidget(scantime=1000, server_ip='192.168.0.12', server_port=502, modbus_addr=modbus_addrs)
        self._widget = MainWidget(scantime=1000, server_ip='192.168.0.12', server_port=502,
                                  modbus_addr=modbus_addrs, tagsMotor=tagsMotor, tagsFlap=tagsFlap, tagsSensores=tagsSensores, db_path=db_path)

        return self._widget

    def on_stop(self):
        """"
        Método executado quando a aplicação é finalizada
        """

        self._widget.stopRefresh()


if __name__ == "__main__":
    Window.size=(1120,630)
    Window.fullscreen = False
    Builder.load_string(open('mainwidget.kv', encoding='utf-8').read(), rulesonly=True)
    Builder.load_string(open('popups.kv', encoding='utf-8').read(), rulesonly=True)
    MainApp().run()
