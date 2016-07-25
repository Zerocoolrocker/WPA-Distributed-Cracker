import db, utils, pwd, os, platform
import cpuinfo
from datetime import datetime
from settings import USUARIO

def host_info():
	username = USUARIO or pwd.getpwuid(os.getuid())[0]
	maq_anf = db.cursor.execute("select maquina_id from maquina_anfitrion").fetchone()
	if maq_anf is None:
		user_id = db.cursor.execute("INSERT INTO usuarios(nombre) VALUES(?)", (username,)).lastrowid
		cpu_info = cpuinfo.get_cpu_info()
		cpu_model = cpu_info["brand"]
		cores = cpu_info["count"]
		cpu_id = db.cursor.execute("INSERT INTO procesadores(modelo, cantidad_nucleos) VALUES(?,?)", (cpu_model, cores)).lastrowid
		machine_id = db.cursor.execute(
			"INSERT INTO maquinas(usuario_id, procesador_id, memoria_ram, os) VALUES(?,?,?,?)", 
			(
				user_id,
				cpu_id,
				utils.get_ram(),
				platform.platform()
			)
		).lastrowid
		db.cursor.execute("INSERT INTO maquina_anfitrion(maquina_id) VALUES(?)", (machine_id,))
		maq_anf = db.cursor.execute("select maquina_id from maquina_anfitrion").fetchone()
	db.conn.commit()
	info = db.cursor.execute("SELECT * FROM maquinas WHERE id=?", (maq_anf[0],)).fetchone()
	return info

def init_session():
	maquina_id = host_info()[0]
	fecha_inicio = datetime.now()
	fecha_fin = None
	status = "iniciada"
	f_cursor = db.cursor.execute(
		"INSERT INTO sesiones(maquina_id, fecha_inicio, fecha_fin, status) VALUES(?,?,?,?)", 
		(maquina_id, fecha_inicio, fecha_fin, status)
	)
	db.conn.commit()