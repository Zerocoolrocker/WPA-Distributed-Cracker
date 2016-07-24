
def connect_db():
	from sqlite3 import connect
	return connect("./databases/db.sqlite3")

def create_tables(cursor):
	querys = [
		"""CREATE TABLE IF NOT EXISTS usuario(
			id INTEGER PRIMARY KEY,
			nombre VARCHAR(20)
		)""",
		"""CREATE TABLE IF NOT EXISTS procesador(
			id INTEGER PRIMARY KEY,
			modelo VARCHAR(100),
			frecuencia REAL,
			cantidad_nucleos INTEGER	

		)""",
		"""CREATE TABLE IF NOT EXISTS maquina(
			id INTEGER PRIMARY KEY,
			usuario_id INTEGER,
			procesador_id INTEGER,
			memoria_ram INTEGER,
			FOREIGN KEY(usuario_id) REFERENCES usuario(id),
			FOREIGN KEY(procesador_id) REFERENCES procesador(id)
		)""",
		"""CREATE TABLE IF NOT EXISTS sesion(
			id INTEGER PRIMARY KEY,
			maquina_id INTEGER,
			fecha_inicio TIMESTAMP,
			fecha_fin TIMESTAMP,
			status VARCHAR(10),
			FOREIGN KEY(maquina_id) REFERENCES maquina(id)
		)""",
		"""CREATE TABLE IF NOT EXISTS detalles_rango(
			id INTEGER PRIMARY KEY,
			universo VARCHAR,
			longitud_combinaciones INTEGER,
			inicio_combinaciones VARCHAR,
			combinacion_actual VRAHCAR,
			fin_combinaciones VARCHAR,
			cola_combinaciones_pendientes VARCHAR,
			session_id INTEGER,
			procesado INTEGER,
			FOREIGN KEY(session_id) REFERENCES sesion(id),
			CHECK (procesado IN (0,1))
		)"""
	]
	for query in querys:
		cursor.execute(query)