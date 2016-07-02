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
	espacios=0;cont=0
	for x in n:
		cont=cont+1
	cantidad=cont**r
	bit=r*8
	peso=cantidad*bit
	for x in xrange(1,cantidad):#contando el ultimo salto
		espacios=espacios+16
	peso=peso+espacios
	print "peso -->",peso,"bit"
