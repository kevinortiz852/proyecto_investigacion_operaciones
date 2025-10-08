import flet as ft
import numpy as np
from scipy.optimize import linear_sum_assignment

def asignacion(costos):
    row_ind, col_ind = linear_sum_assignment(costos)
    asignaciones = list(zip(row_ind, col_ind))
    costo_total = costos[row_ind, col_ind].sum()
    return asignaciones, costo_total

def main_asignacion(page: ft.Page):
    # Configuración del fondo con imagen (coherente con el menú)
    fondo = ft.Image(
        src="fondo6.jpg",
        fit=ft.ImageFit.COVER,
        width=page.width,
        height=page.height,
        expand=True
    )

    # Componentes UI con estilo consistente
    title = ft.Container(
        content=ft.Text(
            "Modelo de Asignación (Algoritmo Húngaro)",
            size=24,
            weight=ft.FontWeight.BOLD,
            color="#FFFFFF"
        ),
        alignment=ft.alignment.center,
        padding=10
    )

    # Estilo común para inputs
    field_style = {
        "width": 400,
        "height": 50,
        "text_align": ft.TextAlign.CENTER,
        "color": "#FFFFFF",
        "bgcolor": "#80333333",
        "border_color": "#FFFFFF",
        "border_radius": 10
    }

    # Campos de entrada
    n_input = ft.TextField(label="Cantidad de tareas/personas", value="3", **field_style)
    nombres_filas_input = ft.TextField(label="Nombres de personas (separados por coma)", value="A,B,C", **field_style)
    nombres_columnas_input = ft.TextField(label="Nombres de tareas (separados por coma)", value="T1,T2,T3", **field_style)

    tabla = ft.Column([], spacing=2, visible=False)
    error_text = ft.Text("", color="red", size=16, visible=False)
    resultado_text = ft.Text("", color="green", size=16, visible=False)
    tabla_resultado = ft.Column([], spacing=2, visible=False)
    tabla_calculo = ft.Column([], spacing=2, visible=False)

    celdas = []

    def crear_tabla(e):
        try:
            tabla.controls.clear()
            celdas.clear()
            tabla_resultado.visible = False
            tabla_calculo.visible = False
            resultado_text.visible = False

            n = int(n_input.value)
            nombres_filas = [n.strip() for n in nombres_filas_input.value.split(",") if n.strip() != ""]
            nombres_columnas = [n.strip() for n in nombres_columnas_input.value.split(",") if n.strip() != ""]

            if len(nombres_filas) != n or len(nombres_columnas) != n:
                error_text.value = "La cantidad de nombres debe coincidir con la cantidad ingresada."
                error_text.visible = True
                tabla.visible = False
                page.update()
                return

            error_text.visible = False

            # Estilo para headers de tabla
            header_style = {
                "weight": ft.FontWeight.BOLD,
                "bgcolor": "#00bcd4",
                "width": 100,
                "text_align": ft.TextAlign.CENTER,
                "color": "#000000"
            }

            headers = [ft.Text("", width=120, text_align=ft.TextAlign.CENTER)] + [
                ft.Text(name, **header_style)
                for name in nombres_columnas
            ]
            tabla.controls.append(ft.Row(headers))

            for i, fila_nombre in enumerate(nombres_filas):
                fila = [ft.Text(fila_nombre, width=120, text_align=ft.TextAlign.CENTER, color="#FFFFFF")]
                fila_celdas = []
                for j in range(n):
                    tf = ft.TextField(
                        value="", 
                        width=100, 
                        text_align=ft.TextAlign.CENTER,
                        color="#FFFFFF",
                        bgcolor="#80333333",
                        border_color="#FFFFFF"
                    )
                    fila.append(tf)
                    fila_celdas.append(tf)
                celdas.append(fila_celdas)
                tabla.controls.append(ft.Row(fila))

            tabla.visible = True
            page.update()
        except Exception as ex:
            error_text.value = f"Error: {str(ex)}"
            error_text.visible = True
            tabla.visible = False
            tabla_resultado.visible = False
            tabla_calculo.visible = False
            resultado_text.visible = False
            page.update()

    def resolver_click(e):
        try:
            n = int(n_input.value)
            nombres_filas = [n.strip() for n in nombres_filas_input.value.split(",") if n.strip() != ""]
            nombres_columnas = [n.strip() for n in nombres_columnas_input.value.split(",") if n.strip() != ""]

            costos = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    val = celdas[i][j].value
                    costos[i, j] = float(val) if val.strip() != "" else 0

            asignaciones, costo_total = asignacion(costos)

            # Estilo para headers de tabla de resultados
            header_style = {
                "weight": ft.FontWeight.BOLD,
                "bgcolor": "#00bcd4",
                "width": 120,
                "text_align": ft.TextAlign.CENTER,
                "color": "#000000"
            }

            # Tabla de resultados (asignaciones)
            tabla_resultado.controls.clear()
            tabla_resultado.controls.append(ft.Row([
                ft.Text("Persona", **header_style),
                ft.Text("Tarea asignada", **header_style),
                ft.Text("Costo", **header_style)
            ]))
            for i, j in asignaciones:
                tabla_resultado.controls.append(ft.Row([
                    ft.Text(nombres_filas[i], width=120, text_align=ft.TextAlign.CENTER, color="#FFFFFF"),
                    ft.Text(nombres_columnas[j], width=120, text_align=ft.TextAlign.CENTER, color="#FFFFFF"),
                    ft.Text(str(costos[i, j]), width=120, text_align=ft.TextAlign.CENTER, color="#FFFFFF")
                ]))
            tabla_resultado.visible = True

            # Tabla de cálculo (asignación × costo)
            tabla_calculo.controls.clear()
            tabla_calculo.controls.append(ft.Row([
                ft.Text("Cálculo de costo total", weight=ft.FontWeight.BOLD, color="#00bcd4", size=16)
            ]))
            suma = 0
            for i, j in asignaciones:
                suma += costos[i, j]
                tabla_calculo.controls.append(
                    ft.Row([
                        ft.Text(f"{nombres_filas[i]} → {nombres_columnas[j]}: {costos[i, j]}", 
                               width=350, color="#FFFFFF")
                    ])
                )
            tabla_calculo.controls.append(ft.Row([
                ft.Text(f"Suma total: {suma:.2f}", weight=ft.FontWeight.BOLD, color="green", width=350)
            ]))
            tabla_calculo.visible = True

            resultado_text.value = f"Costo total mínimo de asignación: {costo_total:.2f}"
            resultado_text.visible = True
            error_text.visible = False
            page.update()
        except Exception as ex:
            resultado_text.visible = False
            tabla_resultado.visible = False
            tabla_calculo.visible = False
            error_text.value = f"Error: {str(ex)}"
            error_text.visible = True
            page.update()

    crear_btn = ft.ElevatedButton(
        text="Crear tabla",
        on_click=crear_tabla,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
            color=ft.Colors.BLACK,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        width=200
    )

    resolver_btn = ft.ElevatedButton(
        text="Resolver",
        on_click=resolver_click,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
            color=ft.Colors.BLACK,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        width=200
    )

    # Contenedor principal con scroll
    form_column = ft.Column(
        [
            title,
            n_input,
            nombres_filas_input,
            nombres_columnas_input,
            ft.Row([crear_btn, resolver_btn], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(error_text, alignment=ft.alignment.center),
            tabla,
            resultado_text,
            tabla_resultado,
            tabla_calculo
        ],
        spacing=15,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=False
    )

    # Layout principal
    main_content = ft.Container(
        content=ft.Column(
            controls=[
                form_column,
            ],
            spacing=20,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        expand=True,
    )

    # Diseño final con Stack para el fondo
    return ft.Stack(
        controls=[
            fondo,
            main_content
        ],
        expand=True
    )