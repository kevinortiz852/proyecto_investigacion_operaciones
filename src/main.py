import flet as ft
from datetime import datetime
import time
import threading
from programacion_lineal import main_programacion_lineal
from aproximacion_vogel import main_vogel
from metodo_costo_minimo import main_costo_minimo
from modelo_de_asignacion import main_asignacion
from esquina_noreste import main_esquina_noroeste  



def main(page: ft.Page):
    fondo = ft.Image(
        src="fondo6.jpg",
        fit=ft.ImageFit.COVER,
        expand=True
)
    


    #---------------------reloj---------------------------
    
    
    
   

    reloj_texto = ft.Text(
        value="",
        size=40,
        color="#FFFFFF",
        weight=ft.FontWeight.BOLD
    )
    reloj_texto2 = ft.Text(
        value="",
        size=10,
        color="#FFFFFF",
        weight=ft.FontWeight.BOLD
    )
    tarjeta2 = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(name=ft.Icons.ACCESS_TIME, color="#FFFFFF", size=30),
                reloj_texto2
                
            ],
            alignment=ft.MainAxisAlignment.START
        ),
        padding=15,
        border_radius=15,
        bgcolor="#80333333",
        shadow=ft.BoxShadow(
            blur_radius=10,
            color="#00000088",
            offset=ft.Offset(0, 4)
    )
    )

    tarjeta = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(name=ft.Icons.ACCESS_TIME, color="#FFFFFF", size=30),
                reloj_texto
                
            ],
            alignment=ft.MainAxisAlignment.END
        ),
        padding=15,
        border_radius=15,
        bgcolor="#80333333",
        shadow=ft.BoxShadow(
            blur_radius=10,
            color="#00000088",
            offset=ft.Offset(0, 4)
    )
    )

    


#-------------------------------------------------

    
    def actualizar_hora():
        while True:
            reloj_texto.value = datetime.now().strftime("%H:%M:%S")
            page.update()
            time.sleep(1)
    threading.Thread(target=actualizar_hora, daemon=True).start()


    def abrir_programacion_lineal(e=None):
        dynamic_content.content = main_programacion_lineal(page)
        page.update()

    def abrir_main_vogel(e=None):
        dynamic_content.content = main_vogel(page)
        page.update()

    def abrir_main_minimo(e=None):
        dynamic_content.content = main_costo_minimo(page)
        page.update()
    
    def abrir_main_asignacion(e=None):
        dynamic_content.content = main_asignacion(page)
        page.update()

    def abrir_main_esquina_noroeste(e=None):
        dynamic_content.content = main_esquina_noroeste(page)
        page.update()
    
   

    

#------------------------------regresar al menu--------------
    










        


#-----------------Iconos--------------------------------------------------
#-----------icono de imagenes-------------------------------------------------------------
    logocolasCirculares = ft.Image(
    src="colasSimples.png",
    width=120,
    height=120,
    fit=ft.ImageFit.CONTAIN,
    border_radius=ft.border_radius.all(20)  # Bordes redondeados
)
    logocolaSimples = ft.Image(
    src="colaCirculares.png",
    width=120,
    height=120,
    fit=ft.ImageFit.CONTAIN,
    border_radius=ft.border_radius.all(20)  # Bordes redondeados
)

    logoCarros = ft.Image(
    src="carros.png",
    
    width=120,
    height=120,
    fit=ft.ImageFit.CONTAIN,
    border_radius=ft.border_radius.all(20)  # Bordes redondeados
)
    
    logoEstudiantes = ft.Image(
    src="estudiante.png",
    
    width=120,
    height=120,
    fit=ft.ImageFit.CONTAIN,
    border_radius=ft.border_radius.all(20)  # Bordes redondeados
)

    logolistasEnlazadasSimples = ft.Image(
    src="listasEnlazadasSimples.png",
    
    width=180,
    height=180,
    fit=ft.ImageFit.CONTAIN,
    border_radius=ft.border_radius.all(20)  # Bordes redondeados
)
    
    logoTablasHash = ft.Image(
    src="tablashash.png",
    width=180,
    height=180,
    fit=ft.ImageFit.CONTAIN,
    border_radius=ft.border_radius.all(20)  # Bordes redondeados
)
  


# ----- ----------1. Contenidos -------------------------------------------------
    # Contenido de INICIO

    

    
  
    logo = ft.Image(
    src="logo.png",
    width=180,
    height=180,
    fit=ft.ImageFit.CONTAIN,
    border_radius=ft.border_radius.all(20)  # Bordes redondeados
)

    contenido = ft.Column(
    controls=[
        logo,
        
        
        ft.Text("INVESTIGACIÓN DE OPERACIONES", 
               color="#FFFFFF", 
               size=40,
               weight=ft.FontWeight.BOLD,
               text_align=ft.TextAlign.CENTER),
        
        ft.Divider(height=20, color="transparent"),
        
        ft.Container(
            content=ft.Column([
                ft.Text("INTEGRANTES", 
                       size=25, 
                       weight=ft.FontWeight.BOLD,
                       color="#ffe033"),
                
                ft.Divider(height=10, color="transparent"),
                
                ft.Container(
                    content=ft.Column([
                        ft.Text("Kevin Josué Ortiz Rivera", size=18),
                        ft.Text("Juan Luis Carrera Lopez", size=18),
                        ft.Text("Allan Paolo Bran Ortega", size=18),
                    ],
                    spacing=5,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK26),
                    padding=20,
                    border_radius=15,
                    width=400
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        ),



    


#------------------------------------------------------------------------
        # Sección opcional para botones de navegación
        ft.Container(
            padding=ft.padding.only(top=10),
            content=ft.Text("Seleccione una estructura del menú lateral",
                            
                            
                          italic=True,
                          color=ft.Colors.WHITE54)
        )
        
    ],
    alignment=ft.MainAxisAlignment.START,
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    spacing=20,
    expand=True,
    scroll=ft.ScrollMode.AUTO
)

# Diseño final con Stack
    inicio_content = ft.Stack(
    expand=True,
    
    controls=[
        fondo,
        tarjeta,

        ft.Container(
            content=contenido,
            expand=True, 
            padding=ft.padding.symmetric(vertical=40),
            alignment=ft.alignment.top_center
        ),
        
        
    ]
)

    




#----------------------------------------------------------------------#




 #-----------------sub menu pilas ---------------------------------------------------   

   


#*********************************************************



    # ----- 2. Función para cambiar secciones -----
    def on_rail_change(e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            dynamic_content.content = inicio_content
        elif selected_index == 1 :
            abrir_programacion_lineal()
        elif selected_index == 2 :
            abrir_main_vogel()
        elif selected_index == 3 :
            abrir_main_minimo()
        elif selected_index == 4 :
            abrir_main_asignacion()
        elif selected_index == 5 :
            abrir_main_esquina_noroeste()
            
        
        



    # ----- 3. Área dinámica -----
    dynamic_content = ft.Container(content=inicio_content, expand=True)

    # ----- 4. Barra de navegación -----
    rail = ft.NavigationRail(
        selected_index=0,
        group_alignment=-0.80,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.APPS, label="Inicio"),
            ft.NavigationRailDestination(icon=ft.Icons.CALCULATE, label="Programacion lineal"),
            ft.NavigationRailDestination(icon=ft.Icons.MONEY, label="vogel "),
            ft.NavigationRailDestination(icon=ft.Icons.SHOPPING_CART, label="Costo minimo"),
            ft.NavigationRailDestination(icon=ft.Icons.EXIT_TO_APP, label="modelo de asignacion"),
            ft.NavigationRailDestination(icon=ft.Icons.LOGOUT, label="Esquina Noroeste"),

        ],
        on_change=on_rail_change,
    )
    # ----- 5. Diseño final -----
    page.add(
    ft.Row(
        controls=[
            ft.Container(rail, expand=False),  
            ft.VerticalDivider(width=1),
            dynamic_content
        ],
        expand=True,
    )
)
ft.app(target=main,assets_dir="assets")
