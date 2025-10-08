import flet as ft
import numpy as np

def costo_minimo(costos, oferta, demanda):
    m, n = len(oferta), len(demanda)
    x = np.zeros((m, n))
    oferta = oferta.copy()
    demanda = demanda.copy()
    usados = np.zeros((m, n), dtype=bool)
    while np.any(oferta) and np.any(demanda):
        min_val = float('inf')
        min_i, min_j = -1, -1
        for i in range(m):
            if oferta[i] == 0:
                continue
            for j in range(n):
                if demanda[j] == 0 or usados[i, j]:
                    continue
                if costos[i, j] < min_val:
                    min_val = costos[i, j]
                    min_i, min_j = i, j
        if min_i == -1 or min_j == -1:
            break
        asignacion = min(oferta[min_i], demanda[min_j])
        x[min_i, min_j] = asignacion
        oferta[min_i] -= asignacion
        demanda[min_j] -= asignacion
        if oferta[min_i] == 0:
            usados[min_i, :] = True
        if demanda[min_j] == 0:
            usados[:, min_j] = True
    return x

def main_costo_minimo(page: ft.Page):
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
            "Método de Costo Mínimo de Transporte",
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
    col_names_input = ft.TextField(label="Nombres de almacenes (separados por coma)", value="W1,W2,W3", **field_style)
    row_names_input = ft.TextField(label="Nombres de plantas (separados por coma)", value="P1,P2,P3", **field_style)
    oferta_input = ft.TextField(label="Oferta por planta (separados por coma)", value="300,500,100", **field_style)
    demanda_input = ft.TextField(label="Demanda por almacén (separados por coma)", value="200,400,300", **field_style)

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

            col_names = [n.strip() for n in col_names_input.value.split(",") if n.strip() != ""]
            row_names = [n.strip() for n in row_names_input.value.split(",") if n.strip() != ""]
            oferta = [float(x) for x in oferta_input.value.split(",") if x.strip() != ""]
            demanda = [float(x) for x in demanda_input.value.split(",") if x.strip() != ""]

            if len(row_names) != len(oferta) or len(col_names) != len(demanda):
                error_text.value = "La cantidad de nombres debe coincidir con la oferta y demanda."
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
                for name in col_names
            ] + [ft.Text("Oferta", **header_style)]
            tabla.controls.append(ft.Row(headers))

            for i, fila_nombre in enumerate(row_names):
                fila = [ft.Text(fila_nombre, width=120, text_align=ft.TextAlign.CENTER, color="#FFFFFF")]
                fila_celdas = []
                for j in range(len(col_names)):
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
                fila.append(ft.Text(str(oferta[i]), width=100, text_align=ft.TextAlign.CENTER, color="#FFFFFF"))
                celdas.append(fila_celdas)
                tabla.controls.append(ft.Row(fila))

            demanda_row = [ft.Text("Demanda", width=120, text_align=ft.TextAlign.CENTER, color="#FFFFFF")]
            for d in demanda:
                demanda_row.append(ft.Text(str(d), width=100, text_align=ft.TextAlign.CENTER, color="#FFFFFF"))
            demanda_row.append(ft.Text(str(sum(oferta)), width=100, text_align=ft.TextAlign.CENTER, color="#FFFFFF"))
            tabla.controls.append(ft.Row(demanda_row))

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
            col_names = [n.strip() for n in col_names_input.value.split(",") if n.strip() != ""]
            row_names = [n.strip() for n in row_names_input.value.split(",") if n.strip() != ""]
            oferta = [float(x) for x in oferta_input.value.split(",") if x.strip() != ""]
            demanda = [float(x) for x in demanda_input.value.split(",") if x.strip() != ""]

            costos = np.zeros((len(row_names), len(col_names)))
            for i in range(len(row_names)):
                for j in range(len(col_names)):
                    val = celdas[i][j].value
                    costos[i, j] = float(val) if val.strip() != "" else 0

            x = costo_minimo(costos, oferta, demanda)
            costo_total = np.sum(x * costos)

            # Tabla de resultados (asignaciones)
            header_style = {
                "weight": ft.FontWeight.BOLD,
                "bgcolor": "#00bcd4",
                "width": 100,
                "text_align": ft.TextAlign.CENTER,
                "color": "#000000"
            }

            resultado_headers = [ft.Text("", width=120, text_align=ft.TextAlign.CENTER)] + [
                ft.Text(name, **header_style)
                for name in col_names
            ]
            tabla_resultado.controls.clear()
            tabla_resultado.controls.append(ft.Row(resultado_headers))
            for i, planta in enumerate(row_names):
                fila = [ft.Text(planta, width=120, text_align=ft.TextAlign.CENTER, color="#FFFFFF")]
                for j in range(len(col_names)):
                    valor = int(x[i, j]) if x[i, j] > 0 else ""
                    fila.append(ft.Text(str(valor), width=100, text_align=ft.TextAlign.CENTER, color="#FFFFFF"))
                tabla_resultado.controls.append(ft.Row(fila))
            tabla_resultado.visible = True

            # Tabla de cálculo (asignación × costo)
            tabla_calculo.controls.clear()
            tabla_calculo.controls.append(ft.Row([ft.Text("Cálculo de costo por celda", weight=ft.FontWeight.BOLD, color="#00bcd4")]))
            suma = 0
            for i, planta in enumerate(row_names):
                for j, almacen in enumerate(col_names):
                    if x[i, j] > 0:
                        celda_costo = x[i, j] * costos[i, j]
                        suma += celda_costo
                        tabla_calculo.controls.append(
                            ft.Row([
                                ft.Text(f"{planta} → {almacen}: {int(x[i, j])} x {costos[i, j]} = {celda_costo:.2f}", 
                                       width=350, color="#FFFFFF")
                            ])
                        )
            tabla_calculo.controls.append(ft.Row([
                ft.Text(f"Suma total: {suma:.2f}", weight=ft.FontWeight.BOLD, color="green", width=350)
            ]))
            tabla_calculo.visible = True

            resultado_text.value = f"Costo total mínimo: {costo_total:.2f}"
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
            col_names_input,
            row_names_input,
            oferta_input,
            demanda_input,
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