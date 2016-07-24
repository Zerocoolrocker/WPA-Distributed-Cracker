#-*-coding:utf8;-*-
from cracker import hmac4times, numOfPs, crackProcess
from pcapParser import load_savefile
from halfHandshake import crackClients
from Queue import Queue
from datetime import datetime
from sys import getsizeof
from threading import Thread
from time import sleep
import termios, atexit, sys, os, time
import shell


def isWPAPass(passPhrase, ssid, clientMac, APMac, Anonce, Snonce, mic, data):
    pke = "Pairwise key expansion" + '\x00' + min(APMac,clientMac)+max(APMac,clientMac)+min(Anonce,Snonce)+max(Anonce,Snonce)
    pmk = pbkdf2_bin(passPhrase, ssid, 4096, 32)
    ptk = hmac4times(pmk,pke)
    if ord(data[6]) & 0b00000010 == 2:
        calculatedMic = hmac.new(ptk[0:16],data,sha1).digest()[0:16]
    else:
        calculatedMic = hmac.new(ptk[0:16],data).digest()
    return mic == calculatedMic

def perm(universo, longitud, inicio=False, fin=False):
    """ 
    Calcula permutaciones.
    universo = lista de caracteres que compondra las combinaciones.
    longitud = longitud que tendra cada permutacion.
    inicio = lista de posiciones desde la cual comenzara a iterar cada caracter. Sirve para especificar la permutacion desde la cual debe iniciar a calcular permutaciones.
    fin = lista de posiciones para la permu final.
    """
    lis = universo
    nt = 1
    n = n2 = longitud
    if inicio:
        assert len(inicio) == longitud
        inicio = list(inicio)
        indexes = [x - 1 for x in inicio]
    if fin:
        assert len(fin) == longitud
        fin = list(fin)
    code = """def yield_perm():
    try:
        lis = '%s'
        n = n2 = %s
        inicio = %s
        fin = %s
        indexes = %s
""" % (''.join(map(str, universo)) if type(universo) == list else universo, longitud, str(inicio), str(fin), str(indexes if inicio else []))
    c = -1
    while n > 0:
        c += 1
        i = -1
        code += ("\t" * nt) + "if inicio:\n" + ("\t" * (nt + 1)) + "c{0} = indexes[{0}]; indexes[{0}] = -1\n".format(c)
        code += ("\t" * nt) + "else:\n" + ("\t" * (nt + 1)) + "c%d = -1\n" % (c)
        code += ("\t" * nt) + ("while c%d < len(lis) - 1:\n" % c)
        nt += 1
        code += ("\t" * nt) + "c%d += 1\n" % c
        code += ('\t' * nt) + "d{0} = lis[c{0}]\n".format(c)
        n -= 1
    contadores = (("c%d , " * n2) % tuple(range(n2)))[:-2]
    code += ('\t' * nt) + "comb = " + (("d%d + " * n2) % tuple(range(n2)))[:-2]  + "\n"
    # code += ('\t' * nt) + "print comb\n"
    code += ('\t' * nt) + "yield comb\n"
    code += ('\t' * nt) + "if [" + contadores + "] == fin:\n"
    code += ('\t' * (nt + 1)) + "indexes = [" + (str(len(universo)) + ', ') * longitud  + "]\n"
    code += ('\t' * (nt + 1)) + "%s = indexes; break\n" % contadores
    code += """    except KeyboardInterrupt:
        pass"""
    exec code
    return yield_perm()

def peso(n,r):#usando permutacion con repeticion
    """
    Muestra el peso en bit de un (diccionario) usando permutacion con repeticion n**r 
    n=todos los elementos que hay ->una lista
    r=tamaño de elementos a combinar->int
    Tomando en cuenta los salto de lineas
    """
    espacios=0;cont=0
    for x in n:
        cont=cont+1
    cantidad=cont**r
    bit=r*8
    peso=cantidad*bit
    for x in xrange(1,cantidad):#contando el ultimo salto
        espacios=espacios+16
    peso=peso+espacios

def crack_WPA_sin_dicc(capFilePath, usersMac, SSID, universo, longitud, inicio=False, fin=False, bufferSize=1231231, dataQueue=Queue()):
    global numOfPs
    foundPassQ = Queue()
    dataQueue.status = "activo"
    ingresar_comb_thread = Thread(
        target=insertar_combinaciones, 
        args=(universo, longitud),
        kwargs=({"dataQueue": dataQueue, "inicio": inicio, "fin" : fin, "bufferSize": bufferSize})
    )
    ingresar_comb_thread.start()

    clients = extraer_cap_info(capFilePath)
    clientHandshakes = []
    for client in clients:
        handshake = []
        for message in clients[client]:
            if message['message'] == 1:
                handshake = [message]
            elif len(handshake) == 1:
                handshake.append(message)
                clientHandshakes.append(handshake)
                break
            else:
                handshake = []
    for clientHandshake in clientHandshakes:
        if clientHandshake[0]['AP'] == usersMac:
            threads = [
                Thread(
                    target=crackProcess, 
                    args=(
                        SSID, 
                        clientHandshake[0]['client'], 
                        clientHandshake[0]['AP'], 
                        clientHandshake[0]['Anonce'], 
                        clientHandshake[1]['Snonce'], 
                        clientHandshake[1]['mic'], 
                        clientHandshake[1]['data'], 
                        dataQueue, 
                        foundPassQ
                    )
                ) 
                for x in xrange(numOfPs)
            ]
            for th in threads:
                th.start()
            shell.init_anykey()
            try:
                while True:
                    # sleep(0.001)
                    # os.system("clear")
                    # print 'crackeando handshake...\npuedes detener el proceso presionando la letra "c" (despues podra ser reanudado)\n'
                    #TODO: IMPRIMIR AQUI INFORMACION SOBRE EL PROCESO DE CRACKEO
                    key = os.read(sys.stdin.fileno(), 1)
                    if key == 'c':
                        dataQueue.status = "detener"
                        break
                    if foundPassQ.empty():
                        if dataQueue.status != "activo":
                            returnVal = None
                            # print "fin de sesion."
                            return
                    else:
                        passphrase = foundPassQ.get()
                        dataQueue.status = "finalizado"
                        return passphrase

                shell.term_anykey()
            except Exception as e:
                shell.term_anykey()
                raise e


def insertar_combinaciones(universo, longitud, inicio=False, fin=False, bufferSize=1231231, dataQueue=Queue()):
    """Inserta las combinaciones de un rango dado en una Queue."""
    for comb in perm(universo, longitud, inicio=inicio, fin=fin):
        if dataQueue.status != "activo":
            return
        while getsizeof(dataQueue) >= bufferSize:
            pass
        dataQueue.put(comb)
    dataQueue.status = "finalizado"

def extraer_cap_info(readFile):
    try:
        caps, header = load_savefile(open(readFile))
    except IOError:
        print "Error reading file"
        exit(2)

    if header.ll_type != 1 and header.ll_type != 105:
        print "unsupported linklayer type, only supports ethernet and 802.11"
        exit(2)
    clients = {}
    if header.ll_type == 105:
        for packet in caps.packets:
            auth = packet[1].raw()[32:34]
            if auth == '\x88\x8e':
                AP = packet[1].raw()[16:22]
                dest = packet[1].raw()[4:10]
                source = packet[1].raw()[10:16]
                part = packet[1].raw()[39:41]
                relivent = True
                if part == '\x00\x8a':
                    message = 1
                    client = dest
                    Anonce = packet[1].raw()[51:83]
                    info = {'AP': AP, 'client': client, 'Anonce': Anonce, 'message': message}
                elif part == '\x01\x0a':
                    Snonce = packet[1].raw()[51:83]
                    client = source
                    mic = packet[1].raw()[115:131]
                    data = packet[1].raw()[34:115] + "\x00"*16 + packet[1].raw()[131:]
                    message = 2
                    info = {'AP': AP, 'data': data, 'client': client, 'Snonce': Snonce, 'mic': mic, 'message': message}
                else:
                    relivent = False
                if relivent:
                    if info['client'] in clients:
                        clients[info['client']].append(info)
                    else:
                        clients[info['client']] = [info]
    else:
        for packet in caps.packets:
            auth = packet[1].raw()[12:14]
            if auth == '\x88\x8e':
                relivent = True
                part = packet[1].raw()[19:21]
                if part == '\x00\x8a':
                    message = 1
                    client = packet[1].raw()[0:6]
                    AP = packet[1].raw()[6:12]
                    Anonce = packet[1].raw()[31:63]
                    info = {'AP': AP, 'client': client, 'Anonce': Anonce, 'message': message}
                elif part == '\x01\x0a':
                    Snonce = packet[1].raw()[31:63]
                    AP = packet[1].raw()[0:6]
                    client = packet[1].raw()[6:12]
                    mic = packet[1].raw()[95:111]
                    data = packet[1].raw()[14:95] + "\x00"*16 + packet[1].raw()[111:]
                    message = 2
                    info = {'AP': AP, 'data': data, 'client': client, 'Snonce': Snonce, 'mic': mic, 'message': message}
                else:
                    relivent = False
                if relivent:
                    if info['client'] in clients:
                        clients[info['client']].append(info)
                    else:
                        clients[info['client']] = [info]
    return clients

def success(clave):
    print "ENCONTRADA!:", clave

def not_found():
    print "La clave no ha sido encontrada."

#ingresar Datos
# def ingresar():
#     """
#     Pide al usuario todos los datos a utilizar 
#     saca en orden
#     (universo, longitud, inicio, fin, cola)
#     """
#     cola=input("ingrese tamaño de buffer en bit->")
#     universo=[]
#     datos=raw_input("datos que quiere que compongan el dicionario->")
#     for x in datos:
#         universo.append(x)
#     longitud=input("longitud que tendra cada permutacion.->")
#     aux=True
#     while(len(inicio)!=longitud) or (aux==True):
#         aux=False
#         inicio=raw_input"ingrese la combinacion inicio->"
#     while (len(fin)!=longitud) or (aux==False):
#         aux=True
#         fin=raw_input"ingrese la combinacion final->"
#     return universo, longitud,inicio,fin,cola
#     #no le e echo salida de otro tipo por que no se que quieres

#Esperar Tamaño Buffer

def buffer(lista):#no es muy eficiente por que si se utiliza en un for por ejemplo entonces comparara una y otra vez para poder obtener lo que quiere
	"""
	Va sacando el peso de la lista
	y comparandolo con el buffer deseado
	la funcion pide lista a sacar peso para comparar
	devuelve = valor booleano
	"""
	resp=False
	peso=0
	aux=ingresar()
	cola=aux[4]
	peso=len(lista)*8
	for x in xrange(1,lista):#contando el ultimo salto
		peso=peso+16
	if(cola==peso):
		resp=True
	return resp

def escritura(dato):
	"""
	recibe un dato tipo = lista
	lo escribe en C:/Users/Public/diccionario.txt
	cada vez que ingrese otra lista salta de linea
	"""
	aux=open("C:/Users/Public/diccionario.txt","a")
	#aux.write("\n" ) <--no se si ponerlo por que no se si interfiera con el proceso de utilizarlas posibles claves
	aux.write(dato)
	aux.close()


def tiempo_proceso(funcion, cantidad_datos, longitud_datos, *test_args, **test_kwargs):
    """Calcula tiempo aproximado en segundos que tardara aplicar un mismo proceso a una cantidad de datos de entrada de la misma longitud."""
    dataQueue = Queue()
    number_test_data = 100
    generador = perm(range(10), longitud_datos)
    for cn in range(number_test_data):
        dataQueue.put(generador.next())
    test_kwargs["dataQueue"] = dataQueue
    tiempo_inicio = datetime.now()
    funcion(*test_args, **test_kwargs)
    tiempo_fin = datetime.now()
    tiempo_transcurrido = (tiempo_fin - tiempo_inicio).total_seconds()
    tiempo_total = (tiempo_transcurrido * cantidad_datos) / number_test_data
    return tiempo_total
