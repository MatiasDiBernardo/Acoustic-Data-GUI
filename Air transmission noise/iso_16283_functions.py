import numpy as np
import pandas as pd

def L1_by_dimensions(data_frame, lista_frecs, sup_piso, vol):
    L1_A = []
    L1_B = []

    index_s_menor_50 =[2,3]
    index_s_50_a_100 = [7,8]
    index_v_menor_25_A = [12,16]
    index_v_menor_25_B = [16,20]

    for f in lista_frecs:
        data = data_frame[f].to_numpy()
        data_1 = data[index_s_menor_50]
        data_2 = data[index_s_50_a_100]
        data_3 = data[index_v_menor_25_A[0]:index_v_menor_25_A[1]]
        data_4 = data[index_v_menor_25_B[0]:index_v_menor_25_B[1]]

        if sup_piso < 50:
            L1_A.append(data_1[0])
            L1_B.append(data_1[1])

        if sup_piso >= 50:
            L1_A.append(10*np.log10( (10**(data_1[0]/10) + 10**(data_2[0]/10))/2 ))
            L1_B.append(10*np.log10( (10**(data_1[1]/10) + 10**(data_2[1]/10))/2 ))

        if vol < 25 and f < 90:
            L_max_A = max(data_3)
            L_max_B = max(data_4)

            L_corner = 10*np.log10( (10**(L_max_A/10) + 10**(L_max_B/10))/2 )

            L1_A[-1] = 10*np.log10( (10**(L_corner/10) + 2 * 10**(L1_A[-1]/10))/3 )
            L1_B[-1] = 10*np.log10( (10**(L_corner/10) + 2 * 10**(L1_B[-1]/10))/3 )

    return L1_A, L1_B

def L2_by_dimensions(data_frame_reciver, data_frame_ruido , lista_frecs, sup_piso, vol):
    L2_A = []
    L2_B = []

    index_s_menor_50 =[1,2]
    index_s_50_a_100 = [6,7]
    index_v_menor_25_A = [11,15]
    index_v_menor_25_B = [15,19]


    for f in lista_frecs:
        data = data_frame_reciver[f].to_numpy()
        data_1 = data[index_s_menor_50]
        data_2 = data[index_s_50_a_100]
        data_3 = data[index_v_menor_25_A[0]:index_v_menor_25_A[1]]
        data_4 = data[index_v_menor_25_B[0]:index_v_menor_25_B[1]]

        data_rudio = data_frame_ruido[f].to_numpy()
        data_ruido_1 = data_rudio[0]
        data_ruido_2 = data_rudio[3::]

        if sup_piso < 50:
            data_correccion1 = compara_dinamica(data_1[0], data_ruido_1)
            data_correccion2 = compara_dinamica(data_1[1], data_ruido_1)

            L2_A.append(data_correccion1)
            L2_B.append(data_correccion2)

        if sup_piso >= 50:
            L2A = 10*np.log10( (10**(data_1[0]/10) + 10**(data_2[0]/10))/2 )
            L2B = 10*np.log10( (10**(data_1[1]/10) + 10**(data_2[1]/10))/2 )

            L2_A.append(compara_dinamica(L2A, data_ruido_1))
            L2_B.append(compara_dinamica(L2B, data_ruido_1))

        if vol < 25 and f < 90:
            data_3_norm = compara_dinamica(data_3, data_ruido_2)
            data_4_norm = compara_dinamica(data_4, data_ruido_2)


            L_max_A = max(data_3_norm)
            L_max_B = max(data_4_norm)

            L_corner = 10*np.log10( (10**(L_max_A/10) + 10**(L_max_B/10))/2 )

            L2_A[-1] = 10*np.log10( (10**(L_corner/10) + 2 * 10**(L2_A[-1]/10))/3 )
            L2_B[-1] = 10*np.log10( (10**(L_corner/10) + 2 * 10**(L2_B[-1]/10))/3 )
        

    return L2_A, L2_B


def compara_dinamica(Nivel_L2, Nivel_Ruido):
    dinamica = Nivel_L2 - Nivel_Ruido

    if type(dinamica) == np.float64:

        if dinamica > 10:
            return Nivel_L2

        if dinamica <= 10 and dinamica > 6:
            return 10*np.log10( (10**(np.round(Nivel_L2, 1)/10) - (10**(np.round(Nivel_Ruido, 1)/10)) ) )
        
        if dinamica <= 6:
            return Nivel_L2 - 1.3
    
    if len(dinamica) != 0:
        rta = []
        for i in range(len(dinamica)):
            if dinamica[i] > 10:
                rta.append(Nivel_L2[i])

            if dinamica[i] <= 10 and dinamica[i] > 6:
                rta.append( 10*np.log10( (10**(np.round(Nivel_L2[i], 1)/10) - (10**(np.round(Nivel_Ruido[i], 1)/10)) ) ) )
            
            if dinamica[i] <= 6:
                rta.append(Nivel_L2[i] - 1.3)

        return rta


def t20_and_absortion(data_frame, frecs, vol):
    t_20_prom = []

    for f in frecs:
        mesuraments_per_frec = data_frame[f].to_numpy()
        lin_sum = sum(mesuraments_per_frec)/len(mesuraments_per_frec)
        t_20_prom.append(round(lin_sum, 2))
    
    if vol < 25:
        t_20_prom[0] = t_20_prom[1]
        t_20_prom[2] = t_20_prom[1]
    
    t_20_prom = np.array(t_20_prom)

    absortion = (0.161 * vol)/t_20_prom

    return t_20_prom, absortion