from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import grey, red, black



def draw_square(main, p):
    for i in range(3):
        main.line(p[i][0], p[i][1], p[i+1][0], p[i+1][1])
    main.line(p[3][0], p[3][1], p[0][0], p[0][1])
    
def hacer_tabla(main, pos_x, pos_y, frecs, datos, tipo):
    width_col = 20
    hight_row = 13.5
    
    draw_square(main, [[pos_x * mm,pos_y*mm],[(pos_x + 2*width_col)*mm, pos_y*mm],
                 [(pos_x + 2*width_col)*mm, (pos_y - 8*hight_row)*mm],
                 [pos_x*mm, (pos_y - 8*hight_row)*mm]])
    
    for i in range(8):
        main.line(pos_x * mm, (pos_y - i* hight_row)*mm, (pos_x + 2*width_col)*mm, (pos_y - i* hight_row)*mm )
    
    main.line((pos_x + width_col) * mm, pos_y*mm, (pos_x + width_col) * mm, (pos_y - 8 * hight_row)*mm)
    
    #Text
    main.setFont('Helvetica', 10)
    main.drawCentredString((pos_x + (width_col/2))*mm, (pos_y -1- (hight_row/2))*mm, 'F (Hz)')
    main.drawCentredString((pos_x + width_col + (width_col/2))*mm, (pos_y - 1-(hight_row/2))*mm, f'{tipo} (dB)')
    
    count = 0
    for i in range(7):
        x_frecs = pos_x + (width_col/2)
        y_frecs = pos_y - i * hight_row - (hight_row/2) - 11
        main.drawCentredString(x_frecs *mm, y_frecs*mm, str(frecs[count]))
        main.drawCentredString(x_frecs *mm, (y_frecs - 4) *mm, str(frecs[count + 1]))
        main.drawCentredString(x_frecs *mm, (y_frecs - 8) *mm, str(frecs[count + 2]))
        
        x_datos = pos_x + (width_col/2) + width_col
        main.drawCentredString(x_datos *mm, y_frecs*mm, str(datos[count]))
        main.drawCentredString(x_datos *mm, (y_frecs - 4) *mm, str(datos[count + 1]))
        main.drawCentredString(x_datos *mm, (y_frecs - 8) *mm, str(datos[count + 2]))
        
        count += 3
    
#Inputs
norma = 0
tipo = 'R'
imagen = 'Grafico_R.png'
vol_emisor = 20
vol_receptor = 30
data_ac = [1,2,3,4,5,6,7,8,9]
ruta_para_guardar = 'test.pdf'

def to_pdf(ruta_para_guardar, datos, data_ac, vol_receptor, vol_emisor, norma, tipo, datos_plantilla, descripcion):
    main = canvas.Canvas(ruta_para_guardar, pagesize=A4,)

    if norma == 0:
        norma_text = 'Norma Iso 140-4'

    if norma == 1:
        norma_text = 'Norma Iso 16283-1'
    
    if norma == 2:
        norma_text = ''
        

    #Variables cambian segun tipo
    if tipo == 'R':
        titulo = f'Indice de reducción sonora de acuerdo con la {norma_text}'
        norma_valoracion = 'Norma ISO 717-1'
        correccion_recuadro = 0
        
    if tipo == 'STC':
        titulo = f'Sound Transsmision Class STC de acuerdo con la {norma_text}'
        norma_valoracion = 'Norma ASTM E413'
        correccion_recuadro = 5
        
    if tipo == 'Dn' or tipo == 'Dnt':
        titulo = f'Diferencia de niveles normalizada de acuerdo con la {norma_text}'
        norma_valoracion = 'Norma ISO 717-1'
        correccion_recuadro = 0

    #Variables constantes
    subtitulo = 'Medidas in situ del asilamiento de ruido aéreo entre recintos'
    desc = 'Descripción e identificación del elemento de construcción y disposición del ensayo:'


    if norma == 2:
        if tipo == 'R':
            titulo = 'Indice de reducción sonora R'
        if tipo == 'STC':
            titulo = 'Sound Transmission Class STC'
        subtitulo = ''
        desc = 'Descripción del elemento de construcción:'

    #Variables que cambian segun imput usario
    txt_cliente = datos_plantilla[0]
    txt_fecha_ensayo = datos_plantilla[1]
    txt_n_inf = datos_plantilla[2]
    txt_instituto = datos_plantilla[3]
    txt_fecha_actual = datos_plantilla[4]

    if norma == 2:
        txt_fecha_ensayo = ''
        txt_instituto = ''
    

    #Text
    main.setFont('Times-Bold', 12)
    main.drawCentredString(105 * mm, 282 * mm, titulo)
    main.drawCentredString(105 * mm, 277 * mm, subtitulo)
    main.drawString(15*mm, 260*mm, 'Cliente: ')
    main.drawString(15*mm, 250*mm, desc)
    #main.drawString(18*mm, 212*mm, f'Volumen emisora: {str(vol_emisor)} m3')
    #main.drawString(18*mm, 205*mm, f'Volumen receptora: {str(vol_receptor)} m3')
    main.drawString(20*mm, 72*mm, f'Valoración según la {norma_valoracion}')
    main.drawString(15*mm, 22*mm, 'N° de Informe:')
    main.drawString(15*mm, 12*mm, 'Fecha:')
    #main.drawString(110*mm, 22*mm, 'Nombre del instituto de ensayo:')
    main.drawString(110*mm, 12*mm, 'Firma:')

    if norma != 2:
        main.drawString(18*mm, 212*mm, f'Volumen emisora: {str(vol_emisor)} m3')
        main.drawString(18*mm, 205*mm, f'Volumen receptora: {str(vol_receptor)} m3')
        main.drawString(110*mm, 22*mm, 'Nombre del instituto de ensayo:')
        main.drawString(110*mm, 260*mm, 'Fecha del ensayo: ')

    #Text Input
    main.setFont('Times-Roman', 12)
    main.drawString(31*mm, 260*mm, txt_cliente)
    main.drawString(144*mm, 260*mm, txt_fecha_ensayo)
    main.drawString(43*mm, 22*mm, txt_n_inf)
    main.drawString(28*mm, 12*mm, txt_fecha_actual)
    main.drawString(168*mm, 22*mm, txt_instituto)
    if len(descripcion) > 95:
        main.drawString(18*mm,240*mm, descripcion[:95])
        main.drawString(18*mm,234*mm, descripcion[95:])
    else:
        main.drawString(18*mm,240*mm, descripcion)


    #Text_ac
    main.setFont('Times-Roman', 11)
    main.drawString(20*mm, 60*mm, f'{tipo} (C ; Ctr): {data_ac[0]}    ({data_ac[1]};{data_ac[2]}) dB')
    main.drawString(75*mm, 60*mm, f'C_50_3150: {data_ac[3]} dB;')
    main.drawString(115*mm, 60*mm, f'C_50_5000: {data_ac[4]} dB;')
    main.drawString(155*mm, 60*mm, f'C_100_5000: {data_ac[5]} dB;')

    main.drawString(75*mm, 45*mm, f'Ctr_50_3150: {data_ac[6]} dB;')
    main.drawString(115*mm, 45*mm, f'Ctr_50_5000: {data_ac[7]} dB;')
    main.drawString(155*mm, 45*mm, f'Ctr_100_5000: {data_ac[8]} dB;')


    main.setFont('Times-Roman', 12)
    main.drawString(110*mm, 212*mm, 'Rango de frecuencias según los valores de')
    main.drawString(110*mm, 205*mm, 'la curva de referencia (ISO 717-1) ')

    main.setFont('Times-Roman', 10)
    main.drawString(20*mm, 50*mm, 'Evaluación basada en resultado de')
    main.drawString(20*mm, 45*mm, 'medidas in situ mediante un')
    main.drawString(20*mm, 40*mm, 'método de Ingeniería.')

    #Lineas
    draw_square(main, [[5*mm,292*mm],[205*mm,292*mm],[205*mm,5*mm],[5*mm,5*mm]])
    main.line(5*mm, 270*mm,205*mm,270*mm)
    draw_square(main, [[15*mm, 245*mm],[195*mm,245*mm],[195*mm,225*mm],[15*mm,225*mm]])
    draw_square(main, [[15*mm, 80*mm],[195*mm,80*mm],[195*mm,35*mm],[15*mm,35*mm]])
    main.line(5*mm,30*mm,205*mm,30*mm)


    #Tabla
    frecs = [50,63,80,100,125,160,200,250, 315,400,500,630, 800,1000,1250, 1600,2000,2500, 3150,4000,5000]

    hacer_tabla(main, 25, 198, frecs, datos, 'R')

    #Lines style
    main.setStrokeColor(red)
    main.line(93*mm,206*mm,105*mm,206*mm)

    main.setStrokeColor(grey)
    draw_square(main, [[15*mm, 220*mm],[195*mm,220*mm],[195*mm,85*mm],[15*mm,85*mm]])
    main.setDash([2,4],0)
    draw_square(main, [[47*mm,(172-correccion_recuadro)*mm],[63*mm,(172-correccion_recuadro)*mm],
                [63*mm,(99-correccion_recuadro)*mm],[47*mm,(99-correccion_recuadro)*mm]])

    main.setStrokeColor(black)
    main.line(93*mm,213*mm,105*mm,213*mm)


    #Gráfico
    imagen = f'Grafico_{tipo}.png'
    main.drawImage(imagen, 71*mm, 88*mm, width=350 , height=330)

    main.save()


