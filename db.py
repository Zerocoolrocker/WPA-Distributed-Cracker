
def connect_db():
	from sqlite3 import connect
	return connect("./databases/db.sqlite3")

def create_tables():
	querys = [
		"""CREATE TABLE IF NOT EXISTS universos(
			id INTEGER PRIMARY KEY,
			universo VARCHAR
		)""",
		"""CREATE TABLE IF NOT EXISTS usuarios(
			id INTEGER PRIMARY KEY,
			nombre VARCHAR(20)
		)""",
		"""CREATE TABLE IF NOT EXISTS procesadores(
			id INTEGER PRIMARY KEY,
			modelo VARCHAR(100),
			cantidad_nucleos INTEGER	

		)""",
		"""CREATE TABLE IF NOT EXISTS maquinas(
			id INTEGER PRIMARY KEY,
			usuario_id INTEGER,
			procesador_id INTEGER,
			memoria_ram INTEGER,
			os VARCHAR(50),
			FOREIGN KEY(usuario_id) REFERENCES usuario(id),
			FOREIGN KEY(procesador_id) REFERENCES procesador(id)
		)""",
		"""CREATE TABLE IF NOT EXISTS sesiones(
			id INTEGER PRIMARY KEY,
			maquina_id INTEGER,
			fecha_inicio TIMESTAMP,
			fecha_fin TIMESTAMP,
			status VARCHAR(10),
			FOREIGN KEY(maquina_id) REFERENCES maquina(id)
		)""",
		"""CREATE TABLE IF NOT EXISTS detalles_rangos(
			id INTEGER PRIMARY KEY,
			universo_id INTEGER,
			longitud_combinaciones INTEGER,
			inicio_combinaciones VARCHAR,
			combinacion_actual VARCHAR,
			fin_combinaciones VARCHAR,
			cola_combinaciones_pendientes VARCHAR,
			session_id INTEGER,
			procesado INTEGER,
			FOREIGN KEY(session_id) REFERENCES sesion(id),
			FOREIGN KEY(universo_id) REFERENCES universos(id),
			CHECK (procesado IN (0,1))
		)""",
		"""CREATE TABLE IF NOT EXISTS maquina_anfitrion(
			id INTEGER PRIMARY KEY,
			maquina_id INTEGER,
			FOREIGN KEY(maquina_id) REFERENCES maquina(id),
			CHECK (id = 1)
		)"""
	]
	for query in querys:
		cursor.execute(query)


conn = connect_db()
cursor = conn.cursor()