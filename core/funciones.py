#-*-coding:utf8;-*-
from halfHandshake import hmac4times


def isWPAPass(passPhrase, ssid, clientMac, APMac, Anonce, Snonce, mic, data):
    pke = "Pairwise key expansion" + '\x00' + min(APMac,clientMac)+max(APMac,clientMac)+min(Anonce,Snonce)+max(Anonce,Snonce)
    pmk = pbkdf2_bin(passPhrase, ssid, 4096, 32)
    ptk = hmac4times(pmk,pke)
    if ord(data[6]) & 0b00000010 == 2:
        calculatedMic = hmac.new(ptk[0:16],data,sha1).digest()[0:16]
    else:
        calculatedMic = hmac.new(ptk[0:16],data).digest()
    return mic == calculatedMic:

def perm(universo, longitud, comienzo=False):
	""" 
	Calcula permutaciones.
	universo = lista de caracteres que compondra las combinaciones.
	longitud = longitud que tendra cada permutacion.
	comienzo = permutacion desde la cual iniciar a calcular permutaciones.
	"""
	#inicializa numero de tabulaciones
	nt = 2
	continuee = False
	if comienzo:
		last = comienzo
		indexes = [lis.index(x) - 1 for x in last]
		indexes[-1] += 2
		continuee = True
	code = """def yield_perm():
	try:
		lis = '%s'
		n = n2 = %s
		continuee = %s
		indexes = %s
"""	% (universo, longitud, str(continuee), str(indexes if continuee else []))
	c = -1
	while n > 0:
		c += 1
		i = -1
		code += ("\t" * nt) + "if continuee:\n" + ("\t" * (nt + 1)) + "c{0} = indexes[{0}]; indexes[{0}] = -1\n".format(c)
		code += ("\t" * nt) + "else:\n" + ("\t" * (nt + 1)) + "c%d = -1\n" % (c)
		# code += ("\t" * nt) + "c%d = -1\n" % (c)
		code += ("\t" * nt) + ("while c%d < len(lis) - 1:\n" % c)
		nt += 1
		code += ("\t" * nt) + "c%d += 1\n" % c
		code += ('\t' * nt) + "d{0} = lis[c{0}]\n".format(c)
		n -= 1
	code += ('\t' * nt) + "comb = " + ("d%d + " * n2) % tuple(range(n2)) + "'\\n'\n"
	code += ('\t' * nt) + "yield comb\n"
	code += """	except KeyboardInterrupt:
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
	print "peso -->",peso," bit"

#ingresar Datos
def ingresar():
	"""
	Pide al usuario todos los datos a utilizar 
	saca en orden
	(universo, longitud, inicio, fin, cola)
	"""
	cola=input("ingrese tamaño de buffer en bit->")
	universo=[]
	datos=raw_input("datos que quiere que compongan el dicionario->")
	for x in datos:
		universo.append(x)
	longitud=input("longitud que tendra cada permutacion.->")
	aux=True
	while(len(inicio)!=longitud) or (aux==True):
		aux=False
		inicio=raw_input"ingrese la combinacion inicio->"
	while (len(fin)!=longitud) or (aux==False):
		aux=True
		fin=raw_input"ingrese la combinacion final->"
	return universo, longitud,inicio,fin,cola
	#no le e echo salida de otro tipo por que no se que quieres

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