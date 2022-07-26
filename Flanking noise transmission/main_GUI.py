import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib
import funciones as func
import numpy as np
import os
from GUI_design import Ui_Dialog

class MainWindow(QDialog):
	def __init__(self):
		super(MainWindow, self).__init__()

		self.ui = Ui_Dialog()
		self.ui.setupUi(self)

		#Cargar datos excel
		self.try_to_load = False
		self.ui.browse_button.clicked.connect(self.load_data)

		#Validación de las dimensiones
		self.ui.input_altura.setValidator(QRegExpValidator(QRegExp(r"[0-9].+")))
		self.ui.input_ancho.setValidator(QRegExpValidator(QRegExp(r"[0-9].+")))
		self.ui.input_largo1.setValidator(QRegExpValidator(QRegExp(r"[0-9].+")))
		self.ui.input_largo2.setValidator(QRegExpValidator(QRegExp(r"[0-9].+")))
		self.datos_validos = False

		#Validar datos
		self.ui.boton_validar.clicked.connect(self.validar_datos)

		#Info de carga datos
		self.ui.boton_informacion.setToolTip('Seguir esquema y excel de ejemplo para cargar datos.')

		#Crea grafico
		self.layout_plot = QtWidgets.QHBoxLayout(self.ui.frame)
		self.layout_plot.setObjectName('layout_plot')

		self.figure = plt.figure()
		self.canvas = FigureCanvas(self.figure)

		self.layout_plot.addWidget(self.canvas)

		#Ajusta tabla inicio
		[self.ui.tabla.setRowHeight(inx, 4) for inx in range(22)]
		[self.ui.tabla.setColumnWidth(i, 70) for i in range(4)]

		#Guardar Excel
		self.ui.exportar_excel.clicked.connect(self.generar_excel)

	def tipo_interseccion(self):  #Hacer que dependa de las boxes QComboBox
		tipo_inter = {'L': self.ui.inter_L.currentText(), 
						'R': self.ui.inter_R.currentText(), 
						'T': self.ui.inter_T.currentText(), 
						'P':self.ui.inter_P.currentText()}
		return tipo_inter

	def load_data(self):
		self.fname = QFileDialog.getOpenFileName(self, 'Open File', 'C:\\', 'Excel file (*.xlsx)')
		self.ui.mostrar_archivo.setText(os.path.basename(self.fname[0]))
		self.try_to_load = True


	def dimensiones_sala(self):
		if self.datos_validos:
			HIGHT = float(self.ui.input_altura.text())
			WIDTH = float(self.ui.input_ancho.text())
			LARGE1 = float(self.ui.input_largo1.text())
			LARGE2 = float(self.ui.input_largo2.text())

			self.Volume_1 = HIGHT * WIDTH * LARGE1
			self.Volume_2 = HIGHT * WIDTH * LARGE2
			self.Sup_floor_1 = WIDTH * LARGE1
			self.Sup_floor_2 = WIDTH * LARGE2
			self.Sup_pared = HIGHT * WIDTH
			self.Sup_total2 = HIGHT *WIDTH *2 + WIDTH *LARGE2 * 2 + HIGHT * LARGE2 * 2

	def validar_datos(self):
		self.interseccion = self.tipo_interseccion()
		lista_dimensiones = [self.ui.input_altura.text(), self.ui.input_ancho.text(),
		self.ui.input_largo1.text(), self.ui.input_largo2.text()]


		if self.try_to_load and all(i != '' for i in lista_dimensiones):
			data = func.input_datos(self.fname[0])
			self.datos_validos = func.validacion_de_inputs(lista_dimensiones, data) 

		if self.datos_validos: 
			self.ui.label_validado_o_no.setText('Datos Validos')
			self.ui.label_validado_o_no.setStyleSheet("font: 11pt Technic; font-style: italic; color: rgb(6, 255, 27)")
			
			self.mostrar_data()
		else:
			self.ui.label_validado_o_no.setText('Datos no Validados')
			self.ui.label_validado_o_no.setStyleSheet("font: 11pt Technic; font-style: italic; color: rgb(223, 0, 0);")
			self.mostrar_data_default()

	def mostrar_data_default(self):
		
		self.ui.tabla.clear()
		[self.ui.tabla.setRowHeight(inx, 4) for inx in range(22)]
		[self.ui.tabla.setColumnWidth(i, 70) for i in range(4)]

		
		lista_labels = [self.ui.label_L1_db, self.ui.label_L2_dB, self.ui.label_L1_dBA,
		 self.ui.label_L2_dBA, self.ui.label_dif_dB, self.ui.label_dif_dBA]
		for i in range(len(lista_labels)):
			lista_labels[i].setText('')

		self.figure.clear()
		self.canvas.draw()


	def mostrar_data(self):
		if self.datos_validos:
			self.dimensiones_sala()
			distancias = [ float(self.ui.input_ancho.text()), float(self.ui.input_altura.text())]
			tipo_inter = self.tipo_interseccion()
			
			data, emi, rec = func.input_datos(self.fname[0])

			self.data_inicial, masa = func.datos_incial_array(data)
			emi_data, rec_data = func.datos_revestimientos(emi, rec)

			lista_delta = func.calcular_deltas(emi_data, rec_data)

			self.lista_flancos = func.R_flancos(self.data_inicial, lista_delta, distancias[0] * distancias[1],
			 distancias, masa, tipo_inter)

			self.R_final = func.R_total(self.lista_flancos)

			self.L2 = func.L2(self.data_inicial[0], self.R_final, self.data_inicial[1], self.Volume_2, self.Sup_total2,  distancias[0] * distancias[1])

			#LLenar Tabla
			data_tabla = [self.data_inicial[0], self.R_final, self.L2 ]
			self.llenar_data_tablas(self.ui.tabla, data_tabla)

			#Llenar datos
			lista_labels = [self.ui.label_L1_db, self.ui.label_L2_dB, self.ui.label_L1_dBA,self.ui.label_L2_dBA, self.ui.label_dif_dB, self.ui.label_dif_dBA]
			L1_db = func.suma_dB(self.data_inicial[0])
			L2_db = func.suma_dB(self.L2)
			L1_dbA = func.suma_pond_A(self.data_inicial[0])
			L2_dBA = func.suma_pond_A(self.L2)
			dist1 = L1_db - L2_db
			dist2 = L1_dbA - L2_dBA
			lista_datos = [L1_db, L2_db, L1_dbA, L2_dBA, dist1, dist2]

			self.llenar_datos_acusticos(lista_labels, lista_datos)

			#LLena data gráfico
			self.mostrar_grafico(self.lista_flancos, self.R_final)

	def llenar_data_tablas(self, tabla, data_tabla):
		frecs_table = [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000]
		tabla.setRowCount(len(frecs_table))
		tabla.setStyleSheet("font-size: 11px; border-collapse: collapse;text-align: center;")

		for i in range(len(frecs_table)):
			tabla.setItem(i, 0,  QtWidgets.QTableWidgetItem(str(frecs_table[i])))
			tabla.setItem(i, 1,  QtWidgets.QTableWidgetItem(str(np.round(data_tabla[0][i], 2))))
			tabla.setItem(i, 2,  QtWidgets.QTableWidgetItem(str(np.round(data_tabla[1][i], 2))))
			tabla.setItem(i, 3,  QtWidgets.QTableWidgetItem(str(np.round(data_tabla[2][i], 2))))
			tabla.setRowHeight(i, 4)
			


	def llenar_datos_acusticos(self, lista_labels, lista_datos):
		text1 = f'{str(np.round(lista_datos[0], 2))} dB'
		text2 = f'{str(np.round(lista_datos[1], 2))} dB'
		text3 = f'{str(np.round(lista_datos[2], 2))} dBA'
		text4 = f'{str(np.round(lista_datos[3], 2))} dBA'
		text5 = f'{str(np.round(lista_datos[4], 2))} dB'
		text6 = f'{str(np.round(lista_datos[5], 2))} dBA'
		
		text_in_labels = [text1, text2, text3, text4, text5, text6]

		for i in range(len(text_in_labels)):
			lista_labels[i].setText(text_in_labels[i])


	def mostrar_grafico(self, flancos, R):
		self.figure.clear()
		graficar = True
		
		band_frecs = [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000]
		nombre_flancos = ['RDd', 'RRr', 'RLl', 'RTt', 'RPp', 'RDr', 'RDl', 'RDt', 'RDp', 'RRd', 'RLd', 'RTd', 'RPd']
		if graficar:
			ax1 = self.figure.add_axes([0.14,0.14,0.81,0.8])

			for i in range(len(flancos) - 1):
				ax1.plot(band_frecs, flancos[i], '--')

			ax1.plot(band_frecs, flancos[-1], '--', label='Flancos')
			ax1.plot(band_frecs, R, label='R TOTAL')
			ax1.set_xscale('log')
			ax1.set_xlabel('Hz')
			ax1.set_ylabel('dB')
			ax1.set_xticks([50, 100, 200, 400, 800, 1600, 3200])
			ax1.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
			ax1.legend()
			ax1.grid()

		self.canvas.draw()
		
	def generar_excel(self):
		if self.datos_validos:

			main_data = [self.data_inicial[0], self.R_final, self.L2]
			ruta_guardar = QFileDialog.getSaveFileName(self, 'Save File', 'C:\\', 'Excel file (*.xlsx)')

			if len(ruta_guardar[0]) != 0:

				func.crear_excel(ruta_guardar[0], main_data, self.lista_flancos)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	mainwindow = MainWindow()
	widget = QtWidgets.QStackedWidget()
	widget.addWidget(mainwindow)
	widget.show()
	widget.setFixedWidth(1023)
	widget.setFixedHeight(687)
	sys.exit(app.exec_())
