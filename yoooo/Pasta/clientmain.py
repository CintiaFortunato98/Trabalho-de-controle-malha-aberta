from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pyModbusTCP.client import ModbusClient
from time import sleep


class ClienteMODBUS():
    """
    Classe Cliente MODBUS
    """

    def __init__(self, server_ip, porta, scan_time=1):
        """
        Construtor
        """
        self._cliente = ModbusClient(host=server_ip, port=porta)
        self._scan_time = scan_time

    def atendimento(self):
        """
        Método para atendimento do usuário
        """
        self._cliente.open()
        try:
            atendimento = True
            while atendimento:
                sel = input(
                    "Deseja realizar uma leitura, escrita ou configuração? (1- Leitura | 2- Escrita | 3- Configuração | 4- Registrar floats | 5- Ler floats | 6- Modificar 1 bit | 7- Ler HR em bits | 8- Sair): ")

                if sel == '1':
                    tipo = input(
                        """Qual tipo de dado deseja ler? (1- Holding Register) |2- Coil |3- Input Register |4- Discrete Input) :""")
                    addr = input(f"Digite o endereço da tabela MODBUS: ")
                    nvezes = input("Digite o número de vezes que deseja ler: ")
                    for i in range(0, int(nvezes)):
                        print(
                            f"Leitura {i+1}: {self.lerDado(int(tipo), int(addr))}")
                        sleep(self._scan_time)
                elif sel == '2':
                    tipo = input(
                        """Qual tipo de dado deseja escrever? (1- Holding Register) |2- Coil) :""")
                    addr = input(f"Digite o endereço da tabela MODBUS: ")
                    valor = input(f"Digite o valor que deseja escrever: ")
                    self.escreveDado(int(tipo), int(addr), int(valor))

                elif sel == '3':
                    scant = input("Digite o tempo de varredura desejado [s]: ")
                    self._scan_time = float(scant)

                elif sel == '4':
                    self.assignFloat_or_Double()

                elif sel == '5':
                    self.readFloat_or_Double()

                elif sel == '6':
                    self.modificar1bit()

                elif sel == '7':
                    self.lerRegPorBits()

                elif sel == '8':
                    self._cliente.close()
                    atendimento = False

                else:
                    print("Seleção inválida")
        except Exception as e:
            print('Erro no atendimento: ', e.args)

    def lerDado(self, tipo, addr):
        """
        Método para leitura de um dado da Tabela MODBUS
        """
        if tipo == 1:
            return self._cliente.read_holding_registers(addr, 1)[0]

        if tipo == 2:
            return self._cliente.read_coils(addr, 1)[0]

        if tipo == 3:
            return self._cliente.read_input_registers(addr, 1)[0]

        if tipo == 4:
            return self._cliente.read_discrete_inputs(addr, 1)[0]

    def escreveDado(self, tipo, addr, valor):
        """
        Método para a escrita de dados na Tabela MODBUS
        """
        if tipo == 1:
            return self._cliente.write_single_register(addr, valor)

        if tipo == 2:
            return self._cliente.write_single_coil(addr, valor)

    def assignFloat_or_Double(self):
        """
        Pegar um valor de 16/32bits e armazená-lo
        em 2/4 registradores de addres seguido
        """
        print("Você deseja armazenar um float (16bits) ou double (32bits)?")
        mod = int(input("1 - Float; 2 - Double "))
        addr = int(input("Digite o endereço da tabela MODBUS: "))
        val = float(input("Digite o valor que deseja escrever: "))
        builder = BinaryPayloadBuilder()
        if mod == 1:
            builder.add_16bit_float(val)
        elif mod == 2:
            builder.add_32bit_float(val)
        payload = builder.to_registers()
        # payload = int(builder.build())
        self._cliente.write_multiple_registers(
            regs_addr=addr, regs_value=payload)

    def readFloat_or_Double(self):
        """
        Ler um valor de 16/32bits
        em 2/4 registradores de addres seguido
        """
        print("Você deseja ler um float (16bits) ou double (32bits)?")
        mod = int(input(f"2 - Float; 4 - Double "))
        addr = int(input(f"Digite o endereço da tabela MODBUS: "))
        result = self._cliente.read_holding_registers(
            reg_addr=addr, reg_nb=mod)
        decoder = BinaryPayloadDecoder.fromRegisters(result)
        if mod == 2:
            a_float = decoder.decode_16bit_float()
            print(f"Seu float é: {a_float}")
        elif mod == 4:
            a_double = decoder.decode_32bit_float()
            print(f"Seu double é: {a_double}")

    def modificar1bit(self):
        """
        Pegar o valor armazenado em um registrador e modificar
        1 dos 16 bits armazenados nele
        """
        list_bits, addr = self.lerRegPorBits()
        pos = int(
            input("Qual a posição do bit que deve ser modificado? 1ª -> 16ª "))
        pos -= 1
        if list_bits[pos] == False:
            list_bits[pos] = True
        else:
            list_bits[pos] = False
        d_int = []
        for i in list_bits:
            if i == False:
                d_int.append(0)
            elif i == True:
                d_int.append(1)
        print(f"Novo valor do HR em bits: {d_int}")
        list_bits1 = []
        list_bits2 = []
        i = 0
        while i < 8:
            list_bits1.append(list_bits[i])
            i += 1
        while i < 16:
            list_bits2.append(list_bits[i])
            i += 1
        builder = BinaryPayloadBuilder()
        builder.add_bits(list_bits2)
        builder.add_bits(list_bits1)
        payload = builder.to_registers()
        # payload = builder.build()
        self._cliente.write_multiple_registers(
            regs_addr=addr, regs_value=payload)
        print(f"Novo valor do HR em int: {self.lerDado(1, addr)}")

    def lerRegPorBits(self):
        """
        Ler o valor armazenado em um registrador como 16bits
        """
        addr = int(input("Digite o endereço da tabela MODBUS: "))
        valor = self.lerDado(1, addr)
        print(f"Valor do HR como int: {valor}")
        result = self._cliente.read_holding_registers(
            reg_addr=addr, reg_nb=1)
        decoder = BinaryPayloadDecoder.fromRegisters(
            result)
        a_int = decoder.decode_bits()
        b_int = decoder.decode_bits()
        c_int = b_int + a_int
        d_int = []
        for i in c_int:
            if i == False:
                d_int.append(0)
            elif i == True:
                d_int.append(1)
        print(f"Valor do HR como bits: {d_int}")
        return c_int, addr


c = ClienteMODBUS('localhost', 502)
c.atendimento()
