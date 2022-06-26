from cProfile import label
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib
import main_functions as mf
import numpy as np
from GUI_design import Ui_Dialog

class MainWindow(QDialog):
	def __init__(self):
		super(MainWindow, self).__init__()
		self.ui = Ui_Dialog()
		self.ui.setupUi(self)


		#Carga datos de la database
		self.materiales, self.densidad, self.mod_young, self.nu, self.mod_poss, self.check = mf.cargar_datos_materiales()

		#Crea lista desplegable de materiales
		self.ui.lista_materiales.addItems(self.materiales)

		#Validación de las dimensiones
		self.ui.input_espesor.setValidator(QRegExpValidator(QRegExp(r"[0-9].+")))
		self.ui.input_L1.setValidator(QRegExpValidator(QRegExp(r"[0-9].+")))
		self.ui.input_L2.setValidator(QRegExpValidator(QRegExp(r"[0-9].+")))
		self.datos_validos = False

		#Label errores
		self.ui.label_main_data_6.setText('')  #Cambiar nombre

		#Graficar_datos
		self.ui.boton_graficar.clicked.connect(self.mostrar_grafico)
		self.ui.boton_limpiar.clicked.connect(self.limpiar_grafico)

		#Crea grafico
		self.layout_plot = QtWidgets.QHBoxLayout(self.ui.frame)
		self.layout_plot.setObjectName('layout_plot')


		self.figure = plt.figure()
		self.canvas = FigureCanvas(self.figure)

		self.layout_plot.addWidget(self.canvas)

		#Guardar Excel
		self.ui.boton_guardar.clicked.connect(self.generar_excel)



	def material_actual(self): 
		return self.ui.lista_materiales.currentText()


	def validar_datos(self, esp, L1, L2, check):
		return mf.validar_datos(esp, L1, L2, check)

	def limpiar_grafico(self):
		self.figure.clear()
		self.canvas.draw()

	def mostrar_error(self, error_msg):
		self.ui.label_main_data_6.setText(error_msg) 		

	def mostrar_grafico(self):
		validacion = self.validar_datos(self.ui.input_espesor.text(), 
		self.ui.input_L1.text(), self.ui.input_L2.text(), self.check)

		if len(validacion) == 0:
			self.datos_validos = True
			self.espesor = float(self.ui.input_espesor.text())
			self.L1 = float(self.ui.input_L1.text())
			self.L2 = float(self.ui.input_L2.text())
			self.display_grafico()
		else:
			self.datos_validos = False
			self.mostrar_error(validacion)

	def modelo_elegido(self):
		crammer = self.ui.modelo_crammer.isChecked()
		sharp = self.ui.modelo_sharp.isChecked()
		davy = self.ui.modelo_davy.isChecked()
		Iso = self.ui.modelo_ISO.isChecked()

		return [crammer, sharp, davy, Iso]


	def display_grafico(self):
		self.figure.clear()
		graficar = True
		
		modelo = self.modelo_elegido()

		band_frecs = [20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000]
		rango = [i for i in range(len(band_frecs))]
		index = mf.index_material_acutal(self.materiales,  self.material_actual())
		data_crammer = mf.modelo_cramer(self.espesor, self.densidad[index], self.mod_young[index], self.mod_poss[index], self.nu[index])
		data_sharp = mf.modelo_sharp(self.espesor, self.densidad[index], self.mod_young[index], self.mod_poss[index], self.nu[index])
		data_davy = mf.modelo_davy(self.espesor, self.L1, self.L2, self.densidad[index], self.mod_young[index], self.nu[index], self.mod_poss[index])
		data_ISO = mf.modelo_ISO(self.espesor, self.densidad[index], self.mod_young[index], self.mod_poss[index], self.nu[index], self.L1, self.L2)


		if graficar:
			ax1 = self.figure.add_axes([0.10,0.17,0.85,0.8])

			if modelo[0]:
				ax1.plot(data_crammer, label='Crammer')

			if modelo[1]:
				ax1.plot(data_sharp, label='Sharp')
			
			if modelo[2]:
				ax1.plot(data_davy, label='Davy')
			
			if modelo[3]:
				ax1.plot(data_ISO, label='ISO 12354-1')
			
			ax1.set_xlabel('Hz')
			ax1.set_ylabel('dB')
			ax1.set_xticks(rango, band_frecs, rotation=45, fontsize=8)
			#ax1.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
			ax1.legend()
			ax1.grid()

		self.canvas.draw()
		
	def generar_excel(self):  #Cambiar decripcion excel a que haga todos los modelos
		validacion = self.validar_datos(self.ui.input_espesor.text(), 
		self.ui.input_L1.text(), self.ui.input_L2.text(), self.check)

		if len(validacion) == 0:
			self.datos_validos = True
		else:
			self.datos_validos = False
			self.mostrar_error(validacion)

		if self.datos_validos:
			ruta_guardar = QFileDialog.getSaveFileName(self, 'Save File', 'C:\\', 'Excel file (*.xlsx)')

			if len(ruta_guardar[0]) != 0:
				index = mf.index_material_acutal(self.materiales,  self.material_actual())
				data_crammer = mf.modelo_cramer(self.espesor, self.densidad[index], self.mod_young[index], self.mod_poss[index], self.nu[index])
				data_sharp = mf.modelo_sharp(self.espesor, self.densidad[index], self.mod_young[index], self.mod_poss[index], self.nu[index])
				data_davy = mf.modelo_davy(self.espesor, self.L1, self.L2, self.densidad[index], self.mod_young[index], self.nu[index], self.mod_poss[index])
				data_ISO = mf.modelo_ISO(self.espesor, self.densidad[index], self.mod_young[index], self.mod_poss[index], self.nu[index], self.L1, self.L2)
				fc, _ = mf.frec_corte(self.espesor, self.densidad[index], self.mod_young[index], self.mod_poss[index])
				mf.crea_excel(ruta_guardar[0], data_crammer, data_sharp, data_davy, data_ISO, self.material_actual(), self.L1, self.L2, fc)  #Creo de todos sin importar cual este tildado no?


if __name__ == '__main__':
	app = QApplication(sys.argv)
	mainwindow = MainWindow()
	widget = QtWidgets.QStackedWidget()
	widget.addWidget(mainwindow)
	widget.show()
	widget.setFixedWidth(745)
	widget.setFixedHeight(689)
	sys.exit(app.exec_())
