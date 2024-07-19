from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String, Float, create_engine
from threading import Lock
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy import select, and_

Base = declarative_base()

class BDHandler:
    def __init__(self, tags, tablename, dbpath='sqlite:///:memory:'):
        self._dbpath = dbpath
        self._tablename = tablename
        self._tags = tags
        self._engine = create_engine(f'sqlite:///{self._dbpath}?check_same_thread=False')
        self._lock = Lock()
        self._DataTable = self.createTable()  # Initialize DataTable here
    
    def createTable(self):
        with self._lock:
            # Define columns
            columns = {
                '__tablename__': self._tablename,
                'id': Column(Integer, primary_key=True, autoincrement=True),
                'timestamp': Column(DateTime)
            }
            for tag, params in self._tags.items():
                if params['type'] == '4x':
                    columns[tag] = Column(Integer)
                elif params['type'] == 'fp':
                    columns[tag] = Column(Float)
                elif params['type'] == 'str':
                    columns[tag] = Column(String)
                else:
                    raise ValueError(f"Unsupported datatype for tag {tag}: {params['type']}")
                
            DataTable = type(self._tablename, (Base,), columns)
            Base.metadata.create_all(self._engine)

            # Verify table creation
            if self._tablename in Base.metadata.tables:
                print(f"Table {self._tablename} created successfully.")
                return DataTable  # Return DataTable instance
            else:
                raise ValueError(f"Failed to create table {self._tablename}.")


    def insert_data(self, data):
        with self._lock:
            if not self._DataTable:
                raise ValueError("DataTable is not initialized correctly.")
            
            Session = sessionmaker(bind=self._engine)
            session = Session()
            try:
                entry = self._DataTable(timestamp=data['timestamp'], **data['values'])
                session.add(entry)
                session.commit()
                print("Dados inseridos com sucesso no banco de dados!")
            except Exception as e:
                session.rollback()
                print(f"Erro ao inserir dados no banco de dados: {e}")
                raise
            finally:
                session.close()


    def select_data(self, start_time, end_time, columns):
        Session = sessionmaker(bind=self._engine)
        session = Session()
        
        try:
            # Constrói a consulta para selecionar os dados
            query = session.query(self._DataTable).filter(self._DataTable.timestamp.between(start_time, end_time))
            
            # Executa a consulta e obtém os resultados
            data = query.all()

            # Transforma os resultados em um formato de dicionário
            result = []
            for row in data:
                row_data = {
                    'timestamp': row.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }
                for col in columns:
                    row_data[col] = getattr(row, col)
                result.append(row_data)

            return result

        except Exception as e:
            print(f"Erro ao consultar o banco de dados: {e}")
            return None
        finally:
            session.close()



