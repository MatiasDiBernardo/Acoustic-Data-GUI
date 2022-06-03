import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import main_functions as mf
import numpy as np
from crea_pdf import to_pdf
import os
from datos_plantilla import Ui_ventana_2



class MainWindow(QDialog):
	def __init__(self):
		super(MainWindow, self).__init__()
		loadUi("GUI_design.ui", self)

		#Chequea que norma queremos usar
		self.check_iso_140.setChecked(True)
		self.tipo_norma = self.tipo_norma_elegido()

		#Cargar datos excel
		self.try_to_load = False
		self.browse_button.clicked.connect(self.load_data)

		#Sacar datos según las dimensiones
		self.input_altura.setValidator(QRegExpValidator(QRegExp(r"[0-9].+")))
		self.input_ancho.setValidator(QRegExpValidator(QRegExp(r"[0-9].+")))
		self.input_largo1.setValidator(QRegExpValidator(QRegExp(r"[0-9].+")))
		self.input_largo2.setValidator(QRegExpValidator(QRegExp(r"[0-9].+")))
		self.datos_validos = False

		#Validar datos
		self.hay_grafico = False
		self.set_layer = True
		self.boton_validar_calcular.clicked.connect(self.validar_datos)

		#Crea grafico
		self.layout_plot = QtWidgets.QHBoxLayout(self.frame)
		self.layout_plot.setObjectName('layout_plot')


		self.figure = plt.figure()
		self.canvas = FigureCanvas(self.figure)

		self.layout_plot.addWidget(self.canvas)

		#Detecta que cambia de pestaña
		self.tipos_dato.currentChanged.connect(self.mostrar_nuevo_grafico)

		#Carga datos del pdf
		self.configurar_datos_pdf.clicked.connect(self.datos_user_pdf)
		self.datos_plantilla_pdf = ['','','','','']
		self.datos_plantilla_descripcion = ''

		#Generar pdf
		botones_gen = [self.exportar_pdf_R, self.exportar_pdf_STC,self.exportar_pdf_dn, self.exportar_pdf_dnt]

		for boton in botones_gen:
			boton.clicked.connect(self.generar_pdf)

		#Genera excel
		botones_ex = [self.exportar_excel_R, self.exportar_excel_STC,self.exportar_excel_dn, self.exportar_excel_dnt]

		for boton in botones_ex:
			boton.clicked.connect(self.generar_excel)

		#Ajusta tabla inicio
		tabla_all = [self.tabla_Rw, self.tabla_STC, self.tabla_dn, self.tabla_dnt]

		for tabla in tabla_all:

			[tabla.setRowHeight(inx, 4) for inx in range(22)]
			tabla.setColumnWidth(0, 70)
			tabla.setColumnWidth(1, 70)


	def tipo_norma_elegido(self):
		opciones = [self.check_iso_140.checkState(),
					self.check_iso_162.checkState(),
					self.check_R_directo.checkState()]

		if opciones == [2,0,0]:
			tipo_norma_actual = 0  #Iso 140

		elif opciones == [0,2,0]:
			tipo_norma_actual = 1  #Iso 162

		elif opciones == [0,0,2]:
			tipo_norma_actual = 2  #Directo

		else:
			tipo_norma_actual = 3  #Error

		return  tipo_norma_actual

	def load_data(self):
		self.fname = QFileDialog.getOpenFileName(self, 'Open File', 'C:\\', 'Excel file (*.xlsx)')
		self.mostrar_archivo.setText(os.path.basename(self.fname[0]))
		self.try_to_load = True


	def dimensiones_sala(self):

		if self.datos_validos:
			HIGHT = float(self.input_altura.text())
			WIDTH = float(self.input_ancho.text())
			LARGE1 = float(self.input_largo1.text())
			LARGE2 = float(self.input_largo2.text())

			self.Volume_1 = HIGHT * WIDTH * LARGE1
			self.Volume_2 = HIGHT * WIDTH * LARGE2
			self.Sup_floor_1 = WIDTH * LARGE1
			self.Sup_floor_2 = WIDTH * LARGE2
			self.Sup_pared = HIGHT * WIDTH

		return None

	def validar_datos(self):
		self.tipo_norma = self.tipo_norma_elegido()
		lista_dimensiones = [self.input_altura.text(), self.input_ancho.text(),
		self.input_largo1.text(), self.input_largo2.text()]

		if self.try_to_load:
			if self.tipo_norma == 0:
				self.datos = mf.input_datos_iso_140_4(self.fname[0])

			if self.tipo_norma == 1:
				self.datos = mf.input_datos_iso_16283(self.fname[0])
			
			if self.tipo_norma == 2:
				self.datos = mf.input_R_directo(self.fname[0])
				if self.try_to_load:
					self.datos_validos = mf.validacion_R_directo(self.datos)
			if self.tipo_norma == 3:
				self.datos = []

		if self.try_to_load and all(i != '' for i in lista_dimensiones):
			self.datos_validos = mf.validacion_de_inputs(lista_dimensiones, self.datos, self.tipo_norma)

		if self.datos_validos: 
			self.boton_validar_calcular.setText('Validar')
			self.label_validado_o_no.setText('Datos Validos')
			self.label_validado_o_no.setStyleSheet("font: 11pt Technic; font-style: italic; color: rgb(6, 255, 27)")
			
			self.mostrar_data()
		else:
			self.label_validado_o_no.setText('Datos no Validados')
			self.label_validado_o_no.setStyleSheet("font: 11pt Technic; font-style: italic; color: rgb(223, 0, 0);")
			self.mostrar_data_default()

	def mostrar_data_default(self):
		tabla_all = [self.tabla_Rw, self.tabla_STC, self.tabla_dn, self.tabla_dnt]
		
		for tabla in tabla_all:
			tabla.clear()
			[tabla.setRowHeight(inx, 4) for inx in range(23)]
			tabla.setColumnWidth(0, 70)
			tabla.setColumnWidth(1, 70)
		
		lista_labels = [[self.label_Rw_R, self.label_50_3150_R, self.label_50_5000_R, self.label_100_5000_R],
							[self.label_Rw_STC, self.label_50_3150_STC, self.label_50_5000_STC, self.label_100_5000_STC],
							[self.label_Rw_dn, self.label_50_3150_dn, self.label_50_5000_dn, self.label_100_5000_dn],
							[self.label_Rw_dnt, self.label_50_3150_dnt, self.label_50_5000_dnt, self.label_100_5000_dnt]]
		for i in range(4):
			for j in range(4):
				lista_labels[i][j].setText('')

		self.figure.clear()
		self.canvas.draw()


	def mostrar_data(self):

		if self.datos_validos:

			if self.tipo_norma == 0:
				self.dimensiones_sala()
				self.main_data_r, self.Rw_r, self.C_r, self.Ctr_r = mf.calcular_datos_iso_140_4(self.datos[0], self.datos[1], self.datos[2], self.datos[3], 
				self.Volume_2, self.Sup_pared, 'R')

				self.main_data_st, self.Rw_st, self.C_st, self.Ctr_st = mf.calcular_datos_iso_140_4(self.datos[0], self.datos[1], self.datos[2], self.datos[3], 
				self.Volume_2, self.Sup_pared, 'STC')

				self.main_data_dn, self.Rw_dn, self.C_dn, self.Ctr_dn = mf.calcular_datos_iso_140_4(self.datos[0], self.datos[1], self.datos[2], self.datos[3], 
				self.Volume_2, self.Sup_pared, 'Dn')

				self.main_data_dnt, self.Rw_dnt, self.C_dnt, self.Ctr_dnt = mf.calcular_datos_iso_140_4(self.datos[0], self.datos[1], self.datos[2], self.datos[3], 
				self.Volume_2, self.Sup_pared, 'Dnt')
			
			if self.tipo_norma == 1:
				self.dimensiones_sala()
				self.main_data_r, self.Rw_r, self.C_r, self.Ctr_r = mf.calcular_datos_iso_16283(self.datos[0], self.datos[1], self.datos[2], self.datos[3], 
				self.Volume_1, self.Volume_2, self.Sup_floor_1, self.Sup_floor_2, self.Sup_pared, 'R')

				self.main_data_st, self.Rw_st, self.C_st, self.Ctr_st = mf.calcular_datos_iso_16283(self.datos[0], self.datos[1], self.datos[2], self.datos[3], 
				self.Volume_1, self.Volume_2, self.Sup_floor_1, self.Sup_floor_2, self.Sup_pared, 'STC')

				self.main_data_dn, self.Rw_dn, self.C_dn, self.Ctr_dn = mf.calcular_datos_iso_16283(self.datos[0], self.datos[1], self.datos[2], self.datos[3], 
				self.Volume_1, self.Volume_2, self.Sup_floor_1, self.Sup_floor_2, self.Sup_pared, 'Dn')

				self.main_data_dnt, self.Rw_dnt, self.C_dnt, self.Ctr_dnt = mf.calcular_datos_iso_16283(self.datos[0], self.datos[1], self.datos[2], self.datos[3], 
				self.Volume_1, self.Volume_2, self.Sup_floor_1, self.Sup_floor_2, self.Sup_pared, 'Dnt')

			if self.tipo_norma == 2:
				self.main_data_r, self.Rw_r, self.C_r, self.Ctr_r = mf.calcular_R_directo(self.datos, 'R')

				self.main_data_st, self.Rw_st, self.C_st, self.Ctr_st = mf.calcular_R_directo(self.datos, 'STC')

				self.main_data_dn, self.Rw_dn, self.C_dn, self.Ctr_dn = [0,0,0,0]

				self.main_data_dnt, self.Rw_dnt, self.C_dnt, self.Ctr_dnt = [0,0,0,0]




			tabla = [self.tabla_Rw, self.tabla_STC, self.tabla_dn, self.tabla_dnt]
			main_data = [self.main_data_r, self.main_data_st, self.main_data_dn, self.main_data_dnt]
			index_para = [self.Rw_r, self.Rw_st, self.Rw_dn, self.Rw_dnt]
			tipo = ['R', 'STC', 'Dn', 'Dnt']
			C_value = [self.C_r, self.C_st, self.C_dn, self.C_dnt]
			Ctr_value = [self.Ctr_r, self.Ctr_st, self.Ctr_dn, self.Ctr_dnt]
			lista_labels = [[self.label_Rw_R, self.label_50_3150_R, self.label_50_5000_R, self.label_100_5000_R],
							[self.label_Rw_STC, self.label_50_3150_STC, self.label_50_5000_STC, self.label_100_5000_STC],
							[self.label_Rw_dn, self.label_50_3150_dn, self.label_50_5000_dn, self.label_100_5000_dn],
							[self.label_Rw_dnt, self.label_50_3150_dnt, self.label_50_5000_dnt, self.label_100_5000_dnt]]

			if self.tipo_norma == 2:
				show = 2
			else:
				show = len(tabla)

			for i in range(show):
				self.llenar_data_tablas(tabla[i], main_data[i])
				self.llenar_datos_acusticos(lista_labels[i], index_para[i], C_value[i], Ctr_value[i])

			pest_act = self.tipos_dato.currentIndex()
			self.mostrar_grafico(main_data[pest_act], index_para[pest_act], tipo[pest_act])

		else:
			self.mostrar_data_default()
		

	def llenar_data_tablas(self, tabla, main_data):
		frecs_table = [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000]
		tabla.setRowCount(len(frecs_table))
		tabla.setStyleSheet("font-size: 11px; border-collapse: collapse;text-align: center;")

		for inx, frec in enumerate(frecs_table):
			tabla.setItem(inx, 0, QtWidgets.QTableWidgetItem(str(frec)))
			tabla.setRowHeight(inx, 4)
		for inx, R_w in enumerate(main_data):
			tabla.setItem(inx, 1, QtWidgets.QTableWidgetItem(str(R_w)))

	def llenar_datos_acusticos(self, lista_labels, main_para, C_para, Ctr_para):
		
		text1 = f'{str(main_para[0])} ({str(C_para[0])} ; {str(Ctr_para[0])}) dB'
		text2 = f'({str(C_para[1])} ; {str(Ctr_para[1])}) dB'
		text3 = f'({str(C_para[2])} ; {str(Ctr_para[2])}) dB'
		text4 = f'({str(C_para[3])} ; {str(Ctr_para[3])}) dB'
		
		text_in_labels = [text1, text2, text3, text4]

		for i in range(len(lista_labels)):
			lista_labels[i].setText(text_in_labels[i])


	def mostrar_grafico(self, main_data, index, tipo):
		self.figure.clear()
		graficar = True
		norma = self.tipo_norma_elegido()
		if norma == 2 and tipo == 'Dn':
			graficar = False
		if norma == 2 and tipo == 'Dnt':
			graficar = False

		band_frecs = [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000]

		ISO_frecs = [100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150]
		ISO = np.array([33, 36, 39, 42, 45, 48, 51, 52, 53, 54, 55, 56, 56, 56, 56, 56])
		x1_line = 100
		x2_line = 3150

		if tipo == 'STC':
			ISO_frecs = [125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150,4000]
			ISO = np.array([36, 39, 42, 45, 48, 51, 52, 53, 54, 55, 56, 56, 56, 56, 56, 56])
			x1_line = 125
			x2_line = 4000

		if graficar:
			plt.plot(ISO_frecs, ISO + index[1], label='ISO 717-1', color='r')
			plt.plot(band_frecs, main_data, label=tipo)
			plt.xscale('log')
			plt.xlabel('Hz')
			plt.ylabel('dB')
			plt.xticks([50, 100, 200, 400, 800, 1600, 3150])
			#plt.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
			plt.axvline(x=x1_line, color='grey', linestyle='--')
			plt.axvline(x=x2_line, color='grey', linestyle='--')
			plt.legend()
			plt.grid()

		self.canvas.draw()
	
	def mostrar_nuevo_grafico(self):
		if self.datos_validos:
			print('Here')
			tipo = self.tab_actual(self.tipos_dato.currentIndex())

			if tipo == 'R':
					datos = self.main_data_r
					index = self.Rw_r
					
			if tipo == 'STC':
				datos = self.main_data_st
				index = self.Rw_st
				
			if tipo == 'Dn':
				datos = self.main_data_dn
				index = self.Rw_dn
				
			if tipo == 'Dnt':
				datos = self.main_data_dnt
				index = self.Rw_dnt

			self.mostrar_grafico(datos, index, tipo)
	
	def generar_pdf(self):

		if self.datos_validos:
			pest = self.tipos_dato.currentIndex()
			tipo = self.tab_actual(pest)

			if tipo == 'R':
				datos = self.main_data_r
				data_ac = [self.Rw_r[0], self.C_r[0], self.Ctr_r[0],self.C_r[1], self.C_r[2], self.C_r[3],
				self.Ctr_r[1],  self.Ctr_r[2],self.Ctr_r[3]]
				ind_graph = self.Rw_r[1]
			if tipo == 'STC':
				datos = self.main_data_st
				data_ac = [self.Rw_st[0], self.C_st[0], self.Ctr_st[0],self.C_st[1], self.C_st[2], self.C_st[3],
				self.Ctr_st[1],  self.Ctr_st[2],self.Ctr_st[3]]
				ind_graph = self.Rw_st[1]
			if tipo == 'Dn':
				datos = self.main_data_dn
				data_ac = [self.Rw_dn[0], self.C_dn[0], self.Ctr_dn[0],self.C_dn[1], self.C_dn[2], self.C_dn[3],
				self.Ctr_dn[1],  self.Ctr_dn[2],self.Ctr_dn[3]]
				ind_graph = self.Rw_dn[1]
			if tipo == 'Dnt':
				datos = self.main_data_dnt
				data_ac = [self.Rw_dnt[0], self.C_dnt[0], self.Ctr_dnt[0],self.C_dnt[1], self.C_dnt[2], self.C_dnt[3],
				self.Ctr_dnt[1],  self.Ctr_dnt[2],self.Ctr_dnt[3]]
				ind_graph = self.Rw_dnt[1]

			ruta_guardar = QFileDialog.getSaveFileName(self, 'Save File', 'C:\\', 'PDF file (*.pdf)')
			norma = self.tipo_norma_elegido()

			#Crea imagen para agregar y la borra depues
			mf.crear_grafico_iso_140(datos, ind_graph, tipo, True)
			
			if len(ruta_guardar[0]) != 0 and norma != 2:
				to_pdf(ruta_guardar[0], datos, data_ac, np.round(self.Volume_1, 2), np.round(self.Volume_2, 2),norma, tipo, 
				self.datos_plantilla_pdf, self.datos_plantilla_descripcion)

			if norma == 2:
				to_pdf(ruta_guardar[0], datos, data_ac, '', '', norma, tipo, self.datos_plantilla_pdf, self.datos_plantilla_descripcion)

			os.remove(f'Grafico_{tipo}.png')

	def tab_actual(self, pest):
		if pest == 0:
			return 'R'
		if pest == 1:
			return 'STC'
		if pest == 2:
			return 'Dn'
		if pest == 3:
			return 'Dnt'
		
	def generar_excel(self):
		if self.datos_validos:
			pest = self.tipos_dato.currentIndex()
			tipo = self.tab_actual(pest)

			if tipo == 'R':
				datos = self.main_data_r
				data_ac = [self.Rw_r[0], self.C_r[0], self.Ctr_r[0],self.C_r[1], self.C_r[2], self.C_r[3],
				self.Ctr_r[1],  self.Ctr_r[2],self.Ctr_r[3]]
			if tipo == 'STC':
				datos = self.main_data_st
				data_ac = [self.Rw_st[0], self.C_st[0], self.Ctr_st[0],self.C_st[1], self.C_st[2], self.C_st[3],
				self.Ctr_st[1],  self.Ctr_st[2],self.Ctr_st[3]]
			if tipo == 'Dn':
				datos = self.main_data_dn
				data_ac = [self.Rw_dn[0], self.C_dn[0], self.Ctr_dn[0],self.C_dn[1], self.C_dn[2], self.C_dn[3],
				self.Ctr_dn[1],  self.Ctr_dn[2],self.Ctr_dn[3]]
			if tipo == 'Dnt':
				datos = self.main_data_dnt
				data_ac = [self.Rw_dnt[0], self.C_dnt[0], self.Ctr_dnt[0],self.C_dnt[1], self.C_dnt[2], self.C_dnt[3],
				self.Ctr_dnt[1],  self.Ctr_dnt[2],self.Ctr_dnt[3]]


			ruta_guardar = QFileDialog.getSaveFileName(self, 'Save File', 'C:\\', 'Excel file (*.xlsx)')
			print(ruta_guardar)

			if len(ruta_guardar[0]) != 0:

				mf.crear_excel(ruta_guardar[0], datos, data_ac, tipo)
	
	def datos_user_pdf(self):
		self.Dialog = QtWidgets.QDialog()
		self.ui = Ui_ventana_2()
		self.ui.setupUi(self.Dialog)
		self.Dialog.show()

		self.ui.guardar_plantilla.clicked.connect(self.guardar_plantilla)

	
	def guardar_plantilla(self):
		self.datos_plantilla_pdf = [self.ui.input_cliente.text(), self.ui.input_fecha_ensayo.text(), self.ui.input_num_ensayo.text(), 
		self.ui.input_instituto_ensayo.text(), self.ui.input_fecha_actual.text()]

		self.datos_plantilla_descripcion = self.ui.text_descripcion.toPlainText()
		self.ui.label_guardado.setText('Datos guardados')

#Cuando paso de alguna norma a R los datos del dn y del dnt no se borran
#Cuando exporto pdf los gráficos no se actualizan

if __name__ == '__main__':
	app = QApplication(sys.argv)
	mainwindow = MainWindow()
	widget = QtWidgets.QStackedWidget()
	widget.addWidget(mainwindow)
	widget.show()
	widget.setFixedWidth(950)
	widget.setFixedHeight(734)
	sys.exit(app.exec_())
