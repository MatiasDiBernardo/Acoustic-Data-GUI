import numpy as np
import pandas as pd


def cargar_datos_materiales():
	check_database = True
	try:
		df = pd.read_excel('database_materiales.xlsx')
		materiales = list(df['Material'])
		densidad = df['Densidad']
		mod_young = df['Módulo de Young']
		nu = df['Factor de pérdidas']
		mod_poss = df['Módulo Poisson']
	except:
		check_database = False

	return materiales, densidad, mod_young, nu, mod_poss, check_database

""" def add_material(lista_materiales, nombre_matrial, densidad, mod_y, nu, mod_p):
	index = len(lista_materiales) + 1
	ind_excel = index + 2

	df3 = pd.DataFrame([[index, nombre_matrial, densidad, mod_y, nu, mod_p]])

	with pd.ExcelWriter('database_materiales.xlsx') as writer:
		df3.to_excel(writer, sheet_name='Hoja 1', index=False, startrow=ind_excel, header=False) """


def index_material_acutal(lista_materiales, material_actual):
	return lista_materiales.index(material_actual)

def frec_corte(espesor, densidad, mod_young, mod_poss):
	m = densidad * espesor

	B = (mod_young*espesor**3)/(12*(1 - mod_poss**2))

	fc = 343**2/(2*np.pi)*np.sqrt(m/B)

	fd = mod_young/(2*np.pi)*np.sqrt(m/B)

	return fc, fd

def correccion_nu(nu, f, m):

	return nu + m/(485*np.sqrt(f))

def modelo_cramer(espesor, densidad, mod_young, mod_poss, nu):

	mod_cramer = []
	band_frecs = [20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000]

	m = densidad * espesor

	fc, fd = frec_corte(espesor, densidad, mod_young, mod_poss)

	for f in band_frecs:
		if f < fc:
			mod_cramer.append(20*np.log10(f*m)-47)

		if f >= fc and f <= fd:
			#mod_cramer.append(20*np.log10(f*m) - 10*np.log10(np.pi/(4*correccion_nu(nu, f, m))) + 10*np.log10(f/fc) - 10*np.log10(fc/(f-fc)) - 47)
			mod_cramer.append(20*np.log10(f*m) - 10*np.log10(np.pi/(4*correccion_nu(nu, f, m))) - 10 *np.log10(fc/(f - fc)) - 47)
		if f > fd:
			mod_cramer.append(20*np.log10(f*m)-47)

	return mod_cramer

def modelo_sharp(espesor, densidad, mod_young, mod_poss, nu):

	modelo_sharp = []
	band_frecs = [20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000]

	m = densidad * espesor

	fc, fd = frec_corte(espesor, densidad, mod_young, mod_poss)

	for f in band_frecs:
		if f < fc/2:
			modelo_sharp.append(10*np.log10(1 + ((np.pi*m*f)/(343*1.18))**2) - 5.5)

		if f >= fc:
			R1 =  10*np.log10(1 + ((np.pi*m*f)/(343*1.18))**2) + 10*np.log10((2*correccion_nu(nu, f, m)*f)/(np.pi*fc))

			R2 = 10*np.log10(1 + ((np.pi*m*f)/(343*1.18))**2) - 5.5

			modelo_sharp.append(min(R1, R2))

		if f >= fc/2 and f < fc:
			modelo_sharp.append(0)

	if 0 in modelo_sharp:
		num_ceros = modelo_sharp.count(0)

		ind_1 = modelo_sharp.index(0) - 1
		ind_2 = modelo_sharp.index(0) + num_ceros

		delta = modelo_sharp[ind_2] - modelo_sharp[ind_1]

		for i in range(len(modelo_sharp)):
			if modelo_sharp[i] == 0:
				modelo_sharp[i] = modelo_sharp[i - 1] + delta/(num_ceros + 1)

	return modelo_sharp

def modelo_davy(t, L1, L2, p, E, nint, o): #Esp, L1, L2, densi, Youn, nu, pois
	p_o = 1.18
	c_o = 343
	averages = 3

	m = p*t	

	filtro = [20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000]
	dB = 0.236
	octave = 3

	B = (E/(1-o**2)) * ((t**3)/12)
	Fc = (c_o**2/(2*np.pi))*np.sqrt(m/B)

	R = []

	for i in range(len(filtro)):
		f = filtro[i]
		Ntot = nint + (m/(485*np.sqrt(f)))
		ratio = f/Fc
		limit = 2**(1/(2*octave))

		if ratio < (1/limit) or ratio > limit:
			TLost = Single_leaf_davy(f, p, E, o, t, Ntot, L2, L1)
		else:
			Avsingle_leaf = 0

			for j in range(1,averages):
				factor = 2**((2*j-1- averages)/(2 * averages* octave))
				aux = 10**(-1*Single_leaf_davy(f*factor, p, E, o, t, Ntot, L2, L1)/10)
				Avsingle_leaf = Avsingle_leaf + aux

			TLost = -10*np.log10(Avsingle_leaf/averages)

		R.append(TLost)

	return R

def Single_leaf_davy(frequency, density, Young, Poisson, thickness, lossfactor, lenght, width):
	po = 1.18
	c0 = 343
	cos21Max = 0.9

	surface_density = density * thickness
	critical_frequency = np.sqrt(12*density*(1-Poisson**2)/Young) * c0**2/(2*thickness*np.pi)
	normal = (po*c0) /(np.pi*frequency*surface_density)
	normal2 = normal * normal

	e = 2* lenght * width/(lenght+width)

	cos2l = c0/(2*np.pi*frequency*e)

	if cos2l > cos21Max:
		cos2l = cos21Max

	tau1 = normal2 * np.log((normal2+1)/(normal2+cos2l)) #Log base e
	ratio = frequency/critical_frequency

	r = 1 - 1/ratio

	if r < 0:
		r = 0

	G = np.sqrt(r)

	rad = Sigma(G, frequency, lenght, width)
	rad2 = rad * rad

	netatotal = lossfactor + rad * normal

	z = 2/netatotal

	y = np.arctan(z) - np.arctan(z*(1-ratio))

	tau2 = normal2 * rad2 * y/(netatotal *2 *ratio)
	tau2 = tau2 * shear(frequency, density, Young, Poisson, thickness)

	if frequency < critical_frequency:
		tau = tau1 + tau2
	else:
		tau = tau2

	return -10 * np.log10(tau)

def Sigma(G, freq, width, lenght):
	c0 = 343
	w = 1.3
	beta = 0.234
	n = 2
	S = lenght * width
	U = 2* (lenght + width)

	twoa = 4 * S/U

	k = 2 * np.pi * freq / c0
	f = w * np.sqrt(np.pi/(k*twoa))

	if f > 1:
		f = 1

	h = 1/(np.sqrt(k * twoa/np.pi) * 2 /3 - beta)
	q = 2*np.pi / (k*k*S)
	qn = q**n

	if G < f:
		alpha = h/f - 1
		xn = (h- alpha * G)**n
	else:
		xn = G**n

	return (xn + qn)**(-1/n)

def shear(frequency, density, Young, Poisson, thickness):
	omega = 2*np.pi * frequency

	chi = (1 + Poisson) / (0.87 + 1.12 * Poisson)
	chi = chi * chi

	X = thickness * thickness/12
	QP = Young/(1- Poisson* Poisson)

	C = -omega * omega
	B = C * (1+ 2 * chi /(1 - Poisson)) * X
	A = X * QP/density

	kbcor2 = (-B + np.sqrt(B**2-4*A*C))/(2*A)
	kb2 = np.sqrt(-C/A)

	G = Young/(2 * (1+ Poisson))

	kT2 = -C * density * chi/G
	kL2 = -C * density/ QP
	kS2 = kT2 + kL2

	ASI = 1 + X * (kbcor2 * kT2/kL2 - kT2)
	ASI *= ASI

	BSI = 1 - X * kT2 + kbcor2 * kS2 / (kb2**2)
	CSI = np.sqrt(1 - X * kT2 + kS2**2/(4*kb2**2))

	return ASI/(BSI*CSI) 

def modelo_ISO(espesor, densidad, mod_young, mod_poss, nu, L1, L2):
	band_frecs = [20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000]
	m = espesor * densidad

	po = 1.18
	c0 = 343
	fc, fd = frec_corte(espesor, densidad, mod_young, mod_poss)

	#fc = c0**2/(espesor*1.8*c0)

	tau = []

	for f in band_frecs:
		k0 = 2*np.pi*f/c0
		tri = -0.964 - (0.5 + L2/(np.pi*L1)) * np.log(L2/L1) + (5*L2)/(2*np.pi*L1) - 1/(4*np.pi*L1*L2*k0**2)
		sigmaf = 0.5 * (np.log(k0*np.sqrt(L1*L2))-tri)

		if sigmaf >= 2:
			sigmaf = 2

		if sigmaf < 0:
			sigmaf = 0

		sig1 = 1/(np.sqrt(1 - fc/f))
		sig2 = 4*L1*L2*(f/c0)**2
		sig3 = np.sqrt((2*np.pi*f*(L1 + L2))/(16*c0))

		f11 = c0**2/(4*fc) * (1/L1**2 + 1/L2**2)

		if f11 < fc/2:
			lamba = np.sqrt(f/fc)

			delta1 = ((1- lamba**2) * np.log((1+lamba)/(1-lamba)) + 2*lamba ) / (4*np.pi**2 * (1- lamba**2)**1.5)

			if f > fc/2:
				delta2 = 0
			else:
				delta2 = (8*c0**2 * (1- 2* lamba**2))/(fc**2 * np.pi**4*L1*L2*lamba*np.sqrt(1- lamba**2))

			if f > fc:
				sigma = sig1

			if f <= fc:
				sigma = (2*(L1+L2))/(L1*L2) * c0/fc * delta1 + delta2

			if f11 > f and f11 < fc and sigma > sig2:
				sigma = sig2

		if f11 >= fc/2:
			if f < fc and sig2 < sig3:
				sigma = sig2

			if f > fc and sig1 < sig3:
				sigma = sig1

			else:
				sigma = sig3

		if sigma >= 2: 
			sigma = 2

		if sigma < 0:
			sigma = 0


		termino = (2* po * c0)/(2*np.pi*f*m)
		if f > fc:
			tau.append(termino**2 * (np.pi * fc * sigma**2)/(2* f * correccion_nu(nu, f, m)))

		#if f > fc - 10 and f < fc + 10:  #Que entiendo por aprox
			#tau.append(termino**2 * (np.pi * sigma**2)/(2* correccion_nu(nu,f, m)))

		if f < fc:
			tau.append(termino**2 * (2*sigmaf + (L1+L2)**2/(L1**2+L2**2) * np.sqrt(fc/f) * sigma**2/correccion_nu(nu,f, m)))

	return -10* np.log10(np.array(tau))



def crea_excel(ruta, crammer, sharp, shavy, Iso, material, L1, L2, Fc):
	band_frecs = [20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000]

	crammer = [round(i, 2) for i in crammer]
	sharp = [round(i, 2) for i in sharp]
	shavy = [round(i, 2) for i in shavy]
	Iso = [round(i, 2) for i in Iso]

	dicc_excel = {'Modelo':['Crammer', 'Sharp', 'Davy', 'Iso']}

	for i in range(len(band_frecs)):
		dicc_excel[band_frecs[i]] = [crammer[i], sharp[i], shavy[i], Iso[i]]
	pd.set_option("display.precision", 2)
	df = pd.DataFrame(dicc_excel)

	dicc_info = {'Material': [material], 'L1': [L1], 'L2' : [L2], 'Fc':[Fc]}
	df2 = pd.DataFrame(dicc_info)

	df3 = pd.DataFrame([['Añado esto', 'Para ver',3]])

	with pd.ExcelWriter(ruta) as writer:
		df.to_excel(writer, sheet_name=f'Datos {material}', index=False, startrow=4)
		df2.to_excel(writer, index=False, sheet_name=f'Datos {material}')
		#df3.to_excel(writer, sheet_name=f'Datos {material}', index=False, startrow=12, header=False)
	#Ver si agregar algo que diga el ancho o el alto de los materiales

def validar_datos(esp, L1, L2, check):
	datos_ok = False

	if not check:
		return 'La base de datos no sigue el formato esperado. Seguir la database de ejemplo.'

	if esp == '' or L1 == '' or L2 == '':
		return 'Ingrese espesor y dimensiones del material elegido.'

	try:
		esp = float(esp)
		L1 = float(L1)
		L2 = float(L2)
	except:
		return 'Ingrese datos númericos válidos.'
	
	if esp > 0 and L1 > 0 and L2 > 0:
		datos_ok = True
	else:
		return 'Ingrese valores positivos de espesor y longitud.'
	
	if datos_ok:
		return ''


materiales, densidad, mod_young, nu, mod_poss, c = cargar_datos_materiales()

index = index_material_acutal(materiales, 'Ladrillo')

espesor = 0.1

crammer = modelo_cramer(espesor, densidad[index], mod_young[index], mod_poss[index], nu[index])  #La segunda formula de cramer me da distinto
sharp = modelo_sharp(espesor, densidad[index], mod_young[index], mod_poss[index], nu[index])   #Mi formula de inter da distinto, la del profe empieza la inter uno después del que debería

#Esp, L1, L2, densi, Youn, nu, pois

L1 = 4
L2 = 3

savy = modelo_davy(espesor, L1, L2, densidad[index], mod_young[index], nu[index], mod_poss[index])
iso = modelo_ISO(espesor,  densidad[index], mod_young[index], mod_poss[index], nu[index], L1, L2)


""" print(crammer)
print(sharp)
print(savy)
print(iso) """