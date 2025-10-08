import flet as ft
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from scipy.spatial import ConvexHull
from itertools import combinations
from io import BytesIO
from PIL import Image
import base64

x, y = sp.symbols("x y")

def descomponer_restricciones(expr):
    if isinstance(expr, sp.And):
        return list(expr.args)
    return [expr]

def cumple_restricciones(punto, restricciones):
    subs = {x: punto[0], y: punto[1]}
    return all(bool(r.subs(subs)) for r in restricciones)

def generar_grafico(z_str, restricciones_str, objetivo):
    z = sp.sympify(z_str)
    restricciones = []
    for r_str in restricciones_str:
        if not r_str.strip():
            continue
        expr = sp.sympify(r_str)
        restricciones.extend(descomponer_restricciones(expr))

    puntos = []

    # Intersecciones entre restricciones
    for r1, r2 in combinations(restricciones, 2):
        try:
            sols = sp.solve([sp.Eq(r1.lhs, r1.rhs), sp.Eq(r2.lhs, r2.rhs)], (x, y), dict=True)
            for sol in sols:
                if x in sol and y in sol:
                    puntos.append((float(sol[x]), float(sol[y])))
        except:
            continue

    # Intersecciones con ejes (x=0 o y=0)
    for r in restricciones:
        try:
            sol_x = sp.solve([sp.Eq(r.lhs, r.rhs), sp.Eq(x, 0)], (x, y), dict=True)
            sol_y = sp.solve([sp.Eq(r.lhs, r.rhs), sp.Eq(y, 0)], (x, y), dict=True)
            for sol in sol_x + sol_y:
                if x in sol and y in sol:
                    puntos.append((float(sol[x]), float(sol[y])))
        except:
            continue

    # Filtro puntos factibles
    puntos = list(set(puntos))  # Elimina duplicados
    factibles = [p for p in puntos if cumple_restricciones(p, restricciones)]

    if len(factibles) < 3:
        raise ValueError("No hay suficientes puntos factibles para formar una región.")

    factibles = np.array(factibles)
    hull = ConvexHull(factibles)
    region = factibles[hull.vertices]

    # Estimar máximos dinámicos y limitar a 500
    x_max = min(max(region[:, 0]) + 10, 500)
    y_max = min(max(region[:, 1]) + 10, 500)

    # Puntos de referencia ajustados
    puntos += [(0, 0), (0, y_max), (x_max, 0), (x_max, y_max)]
    factibles = [p for p in puntos if cumple_restricciones(p, restricciones)]
    factibles = np.array(factibles)
    hull = ConvexHull(factibles)
    region = factibles[hull.vertices]

    fig, ax = plt.subplots(figsize=(7, 7))
    plt.style.use("seaborn-v0_8")

    x_vals = np.linspace(0, x_max, 1000)

    # Graficar restricciones y sombrear zona
    for r in restricciones:
        try:
            y_expr = sp.solve(sp.Eq(r.lhs, r.rhs), y)
            if y_expr:
                y_func = sp.lambdify(x, y_expr[0], "numpy")
                y_vals = y_func(x_vals)

                if '<=' in str(r):
                    ax.fill_between(x_vals, y_vals, y_max, color='gray', alpha=0.1)
                elif '>=' in str(r):
                    ax.fill_between(x_vals, 0, y_vals, color='gray', alpha=0.1)

                ax.plot(x_vals, y_vals, label=str(r))
        except:
            continue

    # Región factible
    ax.fill(region[:, 0], region[:, 1], color='green', alpha=0.3, label="Región Factible")

    # Evaluar Z en vértices
    puntos_z = []
    for vx, vy in region:
        val = float(z.subs({x: vx, y: vy}))
        puntos_z.append((vx, vy, val))
        ax.plot(vx, vy, 'o')
        ax.text(vx + 0.5, vy + 0.5, f"Z={val:.1f}")

    # Punto óptimo
    optimo = max(puntos_z, key=lambda t: t[2]) if objetivo == "Maximizar" else min(puntos_z, key=lambda t: t[2])
    ax.plot(optimo[0], optimo[1], 'r*', markersize=15, label=f"Óptimo: Z={optimo[2]:.1f}")

    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Optimización Lineal")
    ax.legend()

    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def main_programacion_lineal(page: ft.Page):
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
            "Programación Lineal - Método Gráfico",
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
    func_input = ft.TextField(label="Función Objetivo", value="10*x + 20*y", **field_style)
    restr_1 = ft.TextField(label="Restricción 1", value="3*x + y <= 90", **field_style)
    restr_2 = ft.TextField(label="Restricción 2", value="x + y <= 50", **field_style)
    restr_3 = ft.TextField(label="Restricción 3", value="y <= 35", **field_style)

    tipo_combo = ft.Dropdown(
        label="Tipo de optimización",
        options=[
            ft.dropdown.Option("Maximizar"),
            ft.dropdown.Option("Minimizar")
        ],
        value="Maximizar",
        **{k: v for k, v in field_style.items() if k != "height"}
    )

    image_display = ft.Container(
            content=ft.Image(
                width=700,
                height=400,
                fit=ft.ImageFit.CONTAIN,
                visible=False
            ),
            padding=10,
            alignment=ft.alignment.center,
            expand=False
        )

    error_text = ft.Text(color="red", visible=False)

    def graficar_click(e):
        error_text.visible = False
        try:
            img_data = generar_grafico(
                func_input.value,
                [restr_1.value, restr_2.value, restr_3.value],
                tipo_combo.value,
            )
            image_display.content.src_base64 = img_data
            image_display.content.visible = True 
            image_display.content.update()
        except Exception as ex:
                error_text.value = f"Error: {str(ex)}"
                error_text.visible = True
                image_display.content.src_base64 = ""  
                image_display.content.visible = False 
                image_display.content.update()
                page.update()

    graficar_btn = ft.ElevatedButton(
        text="Graficar",
        on_click=graficar_click,
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
            func_input,
            restr_1,
            restr_2,
            restr_3,
            tipo_combo,
            ft.Container(graficar_btn, alignment=ft.alignment.center),
            ft.Container(error_text, alignment=ft.alignment.center),
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
            image_display,
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