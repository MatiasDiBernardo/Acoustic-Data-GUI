import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd
import iso140_4_functions as iso140
import iso_16283_functions as iso162
import matplotlib


#Funciones importantes, hacer pdf, hacer gráfico, sacar datos de cada medición

def input_datos_iso_140_4(path_datos):  #Usar también para la iso 162
    dir_iso140_4 = path_datos

    try:
        emisora_data = pd.read_excel(dir_iso140_4, sheet_name='Sala Emisora')
        receptora_data = pd.read_excel(dir_iso140_4, sheet_name='Sala Receptora')
        ruido_data = pd.read_excel(dir_iso140_4, sheet_name='Nivel Ruido')
        t20_data = pd.read_excel(dir_iso140_4, sheet_name='T20')

        return [emisora_data, receptora_data, ruido_data, t20_data]
    except:
        return []  #Chekear length para input validation

def input_datos_iso_16283(path_datos):
    try:
        emisora_data = pd.read_excel(path_datos, sheet_name='Sala Emisora')
        receptora_data = pd.read_excel(path_datos, sheet_name='Sala Receptora')
        ruido_data = pd.read_excel(path_datos, sheet_name='Nivel Ruido')
        t20_data = pd.read_excel(path_datos, sheet_name='T20 Data')

        return [emisora_data, receptora_data, ruido_data, t20_data]
    except:
        return []

def input_R_directo(path_datos):
    try:
        r_directo = pd.read_excel(path_datos)
        return [r_directo]
    except:
        return []


def calcular_datos_iso_140_4(emitter_data, reciver_data, noise_data, t20_data, Volume_2, Sup_pared, tipo_dato):

    #Saco los datos necesarios
    band_frecs = [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000]

    L1 = iso140.logaritmic_average(emitter_data, band_frecs)

    L2_prom = iso140.logaritmic_average(reciver_data, band_frecs)

    noise = iso140.logaritmic_average(noise_data, band_frecs)

    room_dinamics = L2_prom - noise

    L2 = iso140.second_room_correction(L2_prom, noise)

    T20 = iso140.linear_average(t20_data, band_frecs)

    abosortion_area = 0.161 * Volume_2/T20

    D = L1 - L2

    #Obtengo los parametros necesarios

    Iso = np.array([33, 36, 39, 42, 45, 48, 51, 52, 53, 54, 55, 56, 56, 56, 56, 56])
    if tipo_dato == 'R':
        parametro = np.round(D + 10*np.log10(Sup_pared /abosortion_area),1)

    elif tipo_dato == 'STC':
        parametro = np.round(D + 10*np.log10(Sup_pared /abosortion_area),0)
        Iso = np.array([36, 39, 42, 45, 48, 51, 52, 53, 54, 55, 56, 56, 56, 56, 56, 56])

    elif tipo_dato == 'Dn':
        parametro = np.round(D - 10*np.log10(abosortion_area/10),1)
    
    elif tipo_dato == 'Dnt':
        parametro = np.round(D + 10*np.log10(T20 /0.5),1)

    R_w, R_w_index = iso140.R_w_calc(parametro, Iso)
    C = iso140.calc_C(parametro, R_w)
    C_100_5000 = iso140.calc_C_100_5000(parametro, R_w)
    C_50_3150 = iso140.calc_C_50_3150(parametro, R_w)
    C_50_5000 = iso140.calc_C_50_5000(parametro, R_w)

    Ctr = iso140.calc_Ctr(parametro, R_w)
    Ctr_100_5000 = iso140.calc_Ctr_100_5000(parametro, R_w)
    Ctr_50_3150 = iso140.calc_Ctr_50_3150(parametro, R_w)
    Ctr_50_5000 = iso140.calc_Ctr_50_5000(parametro, R_w)



    return parametro, [R_w, R_w_index], [C, C_50_3150, C_50_5000, C_100_5000], [Ctr, Ctr_50_3150, Ctr_50_5000, Ctr_100_5000]

def calcular_datos_iso_16283(emitter_data, reciver_data, noise_data, t20_data, Volume_1, Volume_2, Sup_1, Sup_2, Sup_pared, tipo_dato):

    band_frecs = [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000]

    L1_A, L1_B = iso162.L1_by_dimensions(emitter_data, band_frecs, Sup_1, Volume_1)

    L2_A, L2_B = iso162.L2_by_dimensions(reciver_data, noise_data, band_frecs, Sup_2, Volume_2)

    T20_prom, absorcion = iso162.t20_and_absortion(t20_data, band_frecs, Volume_2)

    D_A = np.array(L1_A) - np.array(L2_A)
    D_B = np.array(L1_B) - np.array(L2_B)

    Iso = np.array([33, 36, 39, 42, 45, 48, 51, 52, 53, 54, 55, 56, 56, 56, 56, 56])
    if tipo_dato == 'R':
        parametro_A = D_A + 10*np.log10(Sup_pared /absorcion)
        parametro_B = D_B + 10*np.log10(Sup_pared /absorcion)

    elif tipo_dato == 'STC':
        parametro_A = D_A + 10*np.log10(Sup_pared /absorcion)
        parametro_B = D_B + 10*np.log10(Sup_pared /absorcion)
        Iso = np.array([36, 39, 42, 45, 48, 51, 52, 53, 54, 55, 56, 56, 56, 56, 56, 56])

    elif tipo_dato == 'Dn':
        parametro_A = D_A - 10*np.log10(absorcion/10)
        parametro_B = D_B - 10*np.log10(absorcion/10)
    
    elif tipo_dato == 'Dnt':
        parametro_A = D_A + 10*np.log10(T20_prom /0.5)
        parametro_B = D_B + 10*np.log10(T20_prom /0.5)


    parametro = np.round(-10 * np.log10( (10**(-parametro_A/10) + 10**(-parametro_B/10))/2 ), 1)
    if tipo_dato == 'STC':
        parametro = np.round(-10 * np.log10( (10**(-parametro_A/10) + 10**(-parametro_B/10))/2 ), 0)


    R_w, R_w_index = iso140.R_w_calc(parametro, Iso)
    C = iso140.calc_C(parametro, R_w)
    C_100_5000 = iso140.calc_C_100_5000(parametro, R_w)
    C_50_3150 = iso140.calc_C_50_3150(parametro, R_w)
    C_50_5000 = iso140.calc_C_50_5000(parametro, R_w)

    Ctr = iso140.calc_Ctr(parametro, R_w)
    Ctr_100_5000 = iso140.calc_Ctr_100_5000(parametro, R_w)
    Ctr_50_3150 = iso140.calc_Ctr_50_3150(parametro, R_w)
    Ctr_50_5000 = iso140.calc_Ctr_50_5000(parametro, R_w)

    return parametro, [R_w, R_w_index], [C, C_50_3150, C_50_5000, C_100_5000], [Ctr, Ctr_50_3150, Ctr_50_5000, Ctr_100_5000]

def calcular_R_directo(datos, tipo):
    parametro = np.array(datos[0].iloc[0])

    Iso = np.array([33, 36, 39, 42, 45, 48, 51, 52, 53, 54, 55, 56, 56, 56, 56, 56])

    if tipo == 'R':
        parametro = np.round(parametro, 1)
    
    if tipo == 'STC':
        parametro = np.round(parametro, 0)
        Iso = np.array([36, 39, 42, 45, 48, 51, 52, 53, 54, 55, 56, 56, 56, 56, 56, 56])


    R_w, R_w_index = iso140.R_w_calc(parametro, Iso)
    C = iso140.calc_C(parametro, R_w)
    C_100_5000 = iso140.calc_C_100_5000(parametro, R_w)
    C_50_3150 = iso140.calc_C_50_3150(parametro, R_w)
    C_50_5000 = iso140.calc_C_50_5000(parametro, R_w)

    Ctr = iso140.calc_Ctr(parametro, R_w)
    Ctr_100_5000 = iso140.calc_Ctr_100_5000(parametro, R_w)
    Ctr_50_3150 = iso140.calc_Ctr_50_3150(parametro, R_w)
    Ctr_50_5000 = iso140.calc_Ctr_50_5000(parametro, R_w)

    return parametro, [R_w, R_w_index], [C, C_50_3150, C_50_5000, C_100_5000], [Ctr, Ctr_50_3150, Ctr_50_5000, Ctr_100_5000]

def crear_grafico_iso_140(valor, index_valor, tipo_dato, guardar_graph):

    band_frecs = [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000]

    ISO_frecs = [100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150]
    ISO = np.array([33, 36, 39, 42, 45, 48, 51, 52, 53, 54, 55, 56, 56, 56, 56, 56])
    x1_line = 100
    x2_line = 3150

    if tipo_dato == 'STC':
        ISO_frecs = [125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150,4000]
        ISO = np.array([36, 39, 42, 45, 48, 51, 52, 53, 54, 55, 56, 56, 56, 56, 56, 56])
        x1_line = 125
        x2_line = 4000

    fig1, ax1 = plt.subplots()

    ax1.plot(ISO_frecs, ISO + index_valor, label='ISO 717-1', color='r')
    ax1.plot(band_frecs, valor, label=tipo_dato)
    ax1.set_xscale('log')
    ax1.set_xlabel('Hz')
    ax1.set_ylabel('dB')
    ax1.set_xticks([50, 100, 200, 400, 800, 1600, 3150])
    ax1.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    plt.axvline(x=x1_line, color='grey', linestyle='--')
    plt.axvline(x=x2_line, color='grey', linestyle='--')
    ax1.legend()
    ax1.grid()

    if guardar_graph:
        plt.savefig(f'Grafico_{tipo_dato}.png')


def validacion_de_inputs(lista_dimensiones, datos_excel, tipo_de_norma):
    datos_dimensiones_es = False
    datos_norma = False
    datos_excel_es = False

    if tipo_de_norma == 2:
        datos_dimensiones_es = True

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

    if len(datos_excel) != 0 and datos_excel[0].columns[-1] == 5000: #Ver si vale la pena chequear esto de todos o no
        datos_excel_es = True

    if tipo_de_norma != 3:
        datos_norma = True

    if datos_dimensiones_es and datos_norma and datos_excel_es:
        return True
    else:
        return False

def validacion_R_directo(input_user):
    if len(input_user) == 0:
        return False
    return True

def crear_excel(path, main_data, data_ac, tipo):
    frecs = [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000]
    df = pd.DataFrame({'Frecuencia (Hz)': frecs, f'{tipo} (dB)': main_data})

    df2 = pd.DataFrame({f'{tipo}' : data_ac[0], 'C': data_ac[1], 'Ctr': data_ac[2], 'C_50_3150' : data_ac[3], 'C_50_5000': data_ac[4],
    'C_100_5000': data_ac[5], 'Ctr_50_3150' : data_ac[6], 'Ctr_50_5000': data_ac[7], 'Ctr_100_5000': data_ac[8]}, index=[0])

    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, sheet_name=f'Data {tipo}')
        df2.to_excel(writer, sheet_name='Valores Acústicos')


