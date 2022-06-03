import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from jinja2 import Environment, FileSystemLoader


def logaritmic_average(data_frame, frecs_to_evaluate):
	average_log = []
	for f in frecs_to_evaluate:
		log_sum = 0
		mesuraments_per_frec = data_frame[f].to_numpy()

		for i in mesuraments_per_frec:
			log_sum += 10**(i/10) 

		average_log.append(round(10*np.log10(log_sum/len(data_frame[frecs_to_evaluate[0]])), 2))

	return np.array(average_log)

def second_room_correction(L2_prom, noise):
	L2 = []
	room_dinamics = L2_prom - noise
	for i in range(len(L2_prom)):
		if room_dinamics[i] >= 10:
			L2.append(L2_prom[i])

		if room_dinamics[i] >= 6 and room_dinamics[i] < 10:
			L2.append(round(10*np.log10(10**(L2_prom[i]/10) - 10**(noise[i]/10)),2 ))

		if room_dinamics[i] < 6:
			L2.append(round(L2_prom[i] - 1.3, 2))

	return L2

def linear_average(data_frame, frecs_to_evaluate):
	average_lin = []

	for f in frecs_to_evaluate:
		mesuraments_per_frec = data_frame[f].to_numpy()
		lin_sum = sum(mesuraments_per_frec)/len(mesuraments_per_frec)
		average_lin.append(round(lin_sum, 2))

	return np.array(average_lin)

def R_w_calc(data, iso):
	data = data[3:-2]  #Ver como automarizar esto

	for i in range(64):
		iso_shif = iso + 32 - i

		dif_iso_data = iso_shif - data

		dif_iso_data = np.where(dif_iso_data<0, 0, dif_iso_data)

		if sum(dif_iso_data) < 32:

			return iso_shif[7], 32 - i
	
	return None, None

def R_w_calc_STC(data, iso):
	data = data[4:-1]

	for i in range(64):
		iso_shif = iso + 32 - i

		dif_iso_data = iso_shif - data

		dif_iso_data = np.where(dif_iso_data<0, 0, dif_iso_data)

		if sum(dif_iso_data) <= 32 and max(dif_iso_data) <= 8:

			 return iso_shif[7], 32 - i


def calc_C(data, R_w):
	C_ref = np.array([-29, -26, -23, -21, -19, -17, -15, -13, -12, -11, -10, -9,-9, -9, -9, -9]) #De 100 a 3150
	data = data[3:-2]

	X_j = -10*np.log10(sum(10**((C_ref-data)/10)))

	return np.round(X_j, 0) - R_w

def calc_C_100_5000(data, R_w):
	C_ref = np.array([-30, -27, -24, -22, -20, -18, -16, -14, -13, -12, -11, -10, -10,- 10, -10, -10, -10, -10])
	data = data[3:]

	X_j = -10*np.log10(sum(10**((C_ref-data)/10)))

	return np.round(X_j, 0) - R_w

def calc_C_50_3150(data, R_w):
	C_ref = np.array([-40, -36, -33, -29, -26, -23, -21, -19, -17, -15, -13, -12, -11, -10, -9, -9, -9, -9, -9])
	data = data[:-2]

	X_j = -10*np.log10(sum(10**((C_ref-data)/10)))

	return np.round(X_j, 0) - R_w

def calc_C_50_5000(data, R_w):
	C_ref = np.array([-41, -37, -34, -30, -27, -24, -22, -20, -18, -16, -14, -13, -12, -11, -10, -10, -10, -10, -10, -10, -10])

	X_j = -10*np.log10(sum(10**((C_ref-data)/10)))

	return np.round(X_j, 0) - R_w


def calc_Ctr(data, R_w):
	C_ref = np.array([-20, -20, -18, -16, -15, -14, -13, -12, -11, -9, -8, -9, -10, -11, -13, -15])  #De 100 a 3150
	data = data[3:-2]

	X_j = -10*np.log10(sum(10**((C_ref-data)/10)))

	return np.round(X_j, 0) - R_w

def calc_Ctr_100_5000(data, R_w):
	C_ref = np.array([-20, -20, -18, -16, -15, -14, -13, -12, -11, -9, -8, -9, -10, -11, -13, -15, -16, -18])
	data = data[3:]

	X_j = -10*np.log10(sum(10**((C_ref-data)/10)))

	return np.round(X_j, 0) - R_w

def calc_Ctr_50_3150(data, R_w):
	C_ref = np.array([-25, -23, -21, -20, -20, -18, -16, -15, -14, -13, -12, -11, -9, -8, -9, -10, -11, -13, -15])
	data = data[:-2]

	X_j = -10*np.log10(sum(10**((C_ref-data)/10)))

	return np.round(X_j, 0) - R_w

def calc_Ctr_50_5000(data, R_w):
	C_ref = np.array([-25, -23, -21, -20, -20, -18, -16, -15, -14, -13, -12, -11, -9, -8, -9, -10, -11, -13, -15, -16, -18])

	X_j = -10*np.log10(sum(10**((C_ref-data)/10)))

	return np.round(X_j, 0) - R_w


