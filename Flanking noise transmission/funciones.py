import numpy as np
import pandas as pd


def input_datos(path_datos):  #Usar también para la iso 162
    try:
        data_inicial = pd.read_excel(path_datos, sheet_name='Datos Iniciales')
        data_emisora = pd.read_excel(path_datos, sheet_name='Revestimiento Sala Emisora')
        data_receptora = pd.read_excel(path_datos, sheet_name='Revestimiento Sala Receptora')


        return [data_inicial, data_emisora, data_receptora]
    except:
        return []  #Chekear length para input validation


def datos_incial_array(data_inicial_df):
	L1 = data_inicial_df['L1'].to_numpy()
	T2 = data_inicial_df['T2'].to_numpy()
	RD = data_inicial_df['RD'].to_numpy()
	RR = data_inicial_df['RR'].to_numpy()
	RL = data_inicial_df['RL'].to_numpy()
	RT = data_inicial_df['RT'].to_numpy()
	RP = data_inicial_df['RP'].to_numpy()

	masas = [RD[-1], RR[-1], RL[-1], RT[-1], RP[-1]]

	return [L1[2:-1], T2[2:-1], RD[2:-1], RR[2:-1], RL[2:-1], RT[2:-1], RP[2:-1]], masas

def datos_revestimientos(emisora_df, receptora_df):
	Delta_RD = emisora_df['Delta_RD'].to_numpy()
	Delta_RR = emisora_df['Delta_RR'].to_numpy()
	Delta_RL = emisora_df['Delta_RL'].to_numpy()
	Delta_RT = emisora_df['Delta_RT'].to_numpy()
	Delta_RP = emisora_df['Delta_RP'].to_numpy()

	Delta_Rd = receptora_df['Delta_Rd'].to_numpy()
	Delta_Rr = receptora_df['Delta_Rr'].to_numpy()
	Delta_Rl = receptora_df['Delta_Rl'].to_numpy()
	Delta_Rt = receptora_df['Delta_Rt'].to_numpy()
	Delta_Rp = receptora_df['Delta_Rp'].to_numpy()

	return [Delta_RD, Delta_RR, Delta_RL, Delta_RT, Delta_RP], [Delta_Rd, Delta_Rr, Delta_Rl, Delta_Rt, Delta_Rp]


def suma_deltas(a, b):
	rta = []
	for i in range(len(a)):
		if a[i] > b[i]:
			rta.append(a[i] + b[i]/2)
		else:
			rta.append(b[i] + a[i]/2)
	return rta 


def calcular_deltas(del_RD, del_Rd):  #Entra RD, RR, RL, RT, RP
	lista_con_deltas = []

	lista_con_deltas.append(suma_deltas(del_RD[0], del_Rd[0])) #RDd
	lista_con_deltas.append(suma_deltas(del_RD[1], del_Rd[1])) #RRr
	lista_con_deltas.append(suma_deltas(del_RD[2], del_Rd[2])) #RLl
	lista_con_deltas.append(suma_deltas(del_RD[3], del_Rd[3])) #RTt
	lista_con_deltas.append(suma_deltas(del_RD[4], del_Rd[4])) #RPp
	lista_con_deltas.append(suma_deltas(del_RD[0], del_Rd[1])) #RDr
	lista_con_deltas.append(suma_deltas(del_RD[0], del_Rd[2])) #RDl
	lista_con_deltas.append(suma_deltas(del_RD[0], del_Rd[3])) #RDt
	lista_con_deltas.append(suma_deltas(del_RD[0], del_Rd[4])) #RDp
	lista_con_deltas.append(suma_deltas(del_RD[1], del_Rd[0])) #RRd
	lista_con_deltas.append(suma_deltas(del_RD[2], del_Rd[0])) #RLd
	lista_con_deltas.append(suma_deltas(del_RD[3], del_Rd[0])) #RTd
	lista_con_deltas.append(suma_deltas(del_RD[4], del_Rd[0])) #RPd

	return lista_con_deltas


def m(masa, tipo_inter, flanco):
	M = np.log10(masa[0]/masa[flanco])

	if tipo_inter == 'X13':
		return 8.7 + 17.1 * M + 5.7 * M**2
	
	if tipo_inter == 'X12':
		return 8.7 + 5.7 * M**2

	if tipo_inter == 'T13':
		return 5.7 + 14.1 * M + 5.7 * M**2
	
	if tipo_inter == 'T12':
		return 5.7 + 5.7 * M**2



def R_flancos(data_inicial, data_delta, sup_pared, distancias, masa, tipo_inter):
	r_final = []
	m_flanco = {'R': 1, 'L': 2, 'T': 3, 'P': 4}
	right_left_coef = 10* np.log10(np.ones(len(data_delta[1]))*(sup_pared/distancias[1]))
	techo_piso_coef = 10* np.log10(np.ones(len(data_delta[1]))*(sup_pared/distancias[0]))

	data_delta[0][1] = -2  #Esto hay que ver si es un error del profe o es así
    
	r_final.append(data_inicial[2] + data_delta[0])  #RDd
	r_final.append(data_inicial[3] + data_delta[1] + right_left_coef + m(masa, tipo_inter['R'] + '13', m_flanco['R'])) #RRr
	r_final.append(data_inicial[4] + data_delta[2] + right_left_coef + m(masa, tipo_inter['L'] + '13', m_flanco['L']))  #RLl
	r_final.append(data_inicial[5] + data_delta[3] + techo_piso_coef + m(masa, tipo_inter['T'] + '13', m_flanco['T']))  #RTt
	r_final.append(data_inicial[6] + data_delta[4] + techo_piso_coef + m(masa, tipo_inter['P'] + '13', m_flanco['P']))  #Rpp
	r_final.append((data_inicial[2] + data_inicial[3])/2 + data_delta[5] + right_left_coef + m(masa, tipo_inter['R'] + '12', m_flanco['R'] ))  #RDr
	r_final.append((data_inicial[2] + data_inicial[4])/2 + data_delta[6] + right_left_coef + m(masa, tipo_inter['L'] + '12', m_flanco['L']))  #RDl
	r_final.append((data_inicial[2] + data_inicial[5])/2 + data_delta[7] + techo_piso_coef + m(masa, tipo_inter['T'] + '12', m_flanco['T']))  #RDt
	r_final.append((data_inicial[2] + data_inicial[6])/2 + data_delta[8] + techo_piso_coef + m(masa, tipo_inter['P'] + '12', m_flanco['P']))  #RDp
	r_final.append((data_inicial[2] + data_inicial[3])/2 + data_delta[9] + right_left_coef + m(masa, tipo_inter['R'] + '12', m_flanco['R'] ))  #RRd
	r_final.append((data_inicial[2] + data_inicial[4])/2 + data_delta[10] + right_left_coef + m(masa, tipo_inter['L'] + '12', m_flanco['L']))  #RLd
	r_final.append((data_inicial[2] + data_inicial[5])/2 + data_delta[11] + techo_piso_coef + m(masa, tipo_inter['T'] + '12', m_flanco['T']))  #RTd
	r_final.append((data_inicial[2] + data_inicial[6])/2 + data_delta[12] + techo_piso_coef + m(masa, tipo_inter['P'] + '12', m_flanco['P']))  #RPd  
	return r_final


def R_total(lista_flancos):
    suma = 0
    for i in range(len(lista_flancos)):
        suma += 10**(-0.1*lista_flancos[i])
        
    return -10*np.log10(suma) 


def suma_dB(lista):
	log_sum = 0
	for i in lista:
		log_sum += 10**(i/10)
	
	average_log = (round(10*np.log10(log_sum), 2)) 
	
	return average_log

def suma_pond_A(lista):
	lista = np.array(lista)
	ponderacion = [-30.2, -26.3, -22.5, -19.1, -16.1, -13.4, -10.9, -8.6, -6.6, -4.8, -3.2, -1.9, -0.8, 0, 0.6, 1, 1.2, 1.3, 1.2, 1, 0.5]

	lista = lista + ponderacion

	return suma_dB(lista)

def L2(L1, R, TR2, Volumen, Sup_total, Sup_pared_division):
	TR2 = list(map(float, TR2))

	alpha_prom = (0.161*Volumen)/(np.array(TR2)*Sup_total)
	R_sala_2 = alpha_prom*Sup_total/(1-alpha_prom)

	return np.array(L1) - np.array(R) + 10 * np.log10(Sup_pared_division/R_sala_2)

def validacion_de_inputs(lista_dimensiones, datos_excel):
    datos_dimensiones_es = False
    datos_excel_es = False

    if len(datos_excel) != 0:
        datos_excel_es = True

    try:
        lista_dimensiones[0] = float(lista_dimensiones[0])
        lista_dimensiones[1] = float(lista_dimensiones[1])
        lista_dimensiones[2] = float(lista_dimensiones[2])
        lista_dimensiones[3] = float(lista_dimensiones[3])
        dimensiones_son_numeros = True
    except:
        datos_dimensiones_es = False
        dimensiones_son_numeros = False

    if dimensiones_son_numeros:
        if all(i >= 0 for i in lista_dimensiones):
            datos_dimensiones_es = True

    if datos_dimensiones_es and datos_excel_es:
        return True
    else:
        return False

def crear_excel(path, main_data, flancos):  #Main data tiene L1, R y L2 y se hago después el Dn
    frecs = [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000]
    df = pd.DataFrame({'Frecuencia': frecs, 'L1': main_data[0], 'R Total': main_data[1], 'L2': main_data[2]})

    flancos_dicc = {}

    flancos_dicc['Frecuencia'] = frecs

    name_flancos = ['RDd', 'RRr', 'RLl', 'RTt', 'RPp', 'RDr', 'RDl', 'RDt', 'RDp', 'RRd', 'RLd', 'RTd', 'RPd']
    for i in range(len(flancos)):
        flancos_dicc[name_flancos[i]] = flancos[i]

    df2 = pd.DataFrame(flancos_dicc)

    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, sheet_name='Valores generales')
        df2.to_excel(writer, sheet_name='Flancos')
