import flet as ft
import numpy as np
import re

def clean_expression(expr):
    return expr.replace(" ", "").lower()

def detect_variables(func_obj_str, restricciones_str):
    text = func_obj_str + "\n" + restricciones_str
    vars_found = set(re.findall(r"x\d+", text.lower()))
    vars_sorted = sorted(vars_found, key=lambda x: int(x[1:]))
    return vars_sorted

def parse_function_objective(line, variables):
    line = line.lower()
    if line.startswith("z="):
        line = line[2:]
    line = clean_expression(line)

    coefs = [0] * len(variables)
    for i, var in enumerate(variables):
        pattern = re.compile(r"([+-]?[\d\.]*)" + re.escape(var))
        matches = pattern.findall(line)
        total = 0.0
        for m in matches:
            if m in ("", "+"):
                total += 1
            elif m == "-":
                total -= 1
            else:
                total += float(m)
        coefs[i] = total
    return coefs

def parse_restriction(line, variables):
    line = line.lower().replace(" ", "")
    if "<=" in line:
        left, right = line.split("<=")
    elif ">=" in line:
        left, right = line.split(">=")
        left = "-(" + left + ")"
        right = "-" + right
    else:
        raise ValueError("Cada restricción debe contener '<=' o '>='")
    coefs = [0] * len(variables)
    for i, var in enumerate(variables):
        pattern = re.compile(r"([+-]?[\d\.]*)" + re.escape(var))
        matches = pattern.findall(left)
        total = 0.0
        for m in matches:
            if m in ("", "+"):
                total += 1
            elif m == "-":
                total -= 1
            else:
                total += float(m)
        coefs[i] = total
    return coefs, float(right)

def simplex_solver(c, A, b):
    num_vars = len(c)
    num_constraints = len(b)

    slack = np.eye(num_constraints)
    tableau = np.hstack((A, slack, np.array(b).reshape(-1, 1)))
    c_row = np.hstack((-np.array(c), np.zeros(num_constraints + 1)))

    tableau = np.vstack((c_row, tableau))

    tablas = []
    iteracion = 0

    while True:
        iteracion += 1
        tablas.append((iteracion, tableau.copy()))

        col_pivote = np.argmin(tableau[0, :-1])
        if tableau[0, col_pivote] >= 0:
            break

        razones = []
        for i in range(1, tableau.shape[0]):
            if tableau[i, col_pivote] > 0:
                razones.append(tableau[i, -1] / tableau[i, col_pivote])
            else:
                razones.append(np.inf)
        fila_pivote = np.argmin(razones) + 1

        tableau[fila_pivote] /= tableau[fila_pivote, col_pivote]
        for i in range(tableau.shape[0]):
            if i != fila_pivote:
                tableau[i] -= tableau[i, col_pivote] * tableau[fila_pivote]

    return tablas

def format_tableau(tab, variables, num_constraints):
    slack_vars = [f"x{i+len(variables)+1}" for i in range(num_constraints)]
    all_vars = variables + slack_vars
    headers = ["Ecuación", "Variable Básica", "Z"] + all_vars + ["LD"]

    rows = []
    # Fila Z (ecuación 0)
    z_row = ["0", "z", "1"] + [f"{v:.3f}" for v in tab[0, :-1]] + [f"{tab[0, -1]:.3f}"]
    rows.append(z_row)

    # Filas de restricciones (ecuaciones 1..n)
    for i in range(1, tab.shape[0]):
        var_name = slack_vars[i-1] if i-1 < len(slack_vars) else f"x?"
        row_vals = [f"{v:.3f}" for v in tab[i, :-1]]
        row = [str(i), var_name, "0"] + row_vals + [f"{tab[i, -1]:.3f}"]
        rows.append(row)

    return headers, rows

def obtener_resultados(tab, variables, num_constraints):
    slack_vars = [f"x{i+len(variables)+1}" for i in range(num_constraints)]
    all_vars = variables + slack_vars
    resultados = {v: 0.0 for v in all_vars}

    # Detectar variables básicas (columna con un solo 1 y demás 0)
    for j, var in enumerate(all_vars):
        columna = tab[1:, j]  # sin fila z
        if np.count_nonzero(columna) == 1 and np.isclose(columna.max(), 1.0):
            fila = np.argmax(columna) + 1
            resultados[var] = tab[fila, -1]

    # Valor de Z
    z_val = tab[0, -1]

    # Filtrar solo los mayores a 0
    resultados_positivos = {v: val for v, val in resultados.items() if val > 0}

    return resultados_positivos, z_val

def main_simplex(page: ft.Page):
    # Configuración del fondo con imagen
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
            "Método Simplex - Maximización",
            size=24,
            weight=ft.FontWeight.BOLD,
            color="#FFFFFF"
        ),
        alignment=ft.alignment.center,
        padding=10
    )

    # Estilo común para inputs
    field_style = {
        "width": 500,
        "height": 50,
        "text_align": ft.TextAlign.LEFT,
        "color": "#FFFFFF",
        "bgcolor": "#80333333",
        "border_color": "#FFFFFF",
        "border_radius": 10,
        "multiline": False
    }

    # Campos de entrada
    info = ft.Text(
        "Ej: z=4x1+6x2",
        color="#FFFFFF",
        size=12
    )
    
    func_obj_field = ft.TextField(
        label="Función Objetivo", 
        value="z=4x1+6x2",
        **field_style
    )
    
    restricciones_field = ft.TextField(
        label="Restricciones (una por línea)", 
        value="x1+2x2<=8\n3x1+2x2<=12",
        width=500,
        height=150,
        text_align=ft.TextAlign.LEFT,
        color="#FFFFFF",
        bgcolor="#80333333",
        border_color="#FFFFFF",
        border_radius=10,
        multiline=True
    )

    # Área de resultados
    salida = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        height=400
    )

    error_text = ft.Text(color="red", visible=False)

    def resolver(e):
        salida.controls.clear()
        error_text.visible = False
        
        try:
            func_obj_str = func_obj_field.value.strip()
            restr_str = restricciones_field.value.strip()

            if not func_obj_str or not restr_str:
                raise ValueError("Por favor complete todos los campos")

            variables = detect_variables(func_obj_str, restr_str)
            if not variables:
                raise ValueError("No se detectaron variables, asegúrate de usar formato x1, x2, ...")

            c = parse_function_objective(func_obj_str, variables)

            restr_lines = [line for line in restr_str.split("\n") if line.strip()]
            A = []
            b = []
            for line in restr_lines:
                coefs, val = parse_restriction(line, variables)
                A.append(coefs)
                b.append(val)

            # Mostrar información del problema
            salida.controls.append(ft.Text(
                f"Problema detectado: {len(variables)} variables, {len(b)} restricciones",
                weight=ft.FontWeight.BOLD,
                color="#FFFFFF"
            ))
            salida.controls.append(ft.Text(
                f"Función objetivo: {func_obj_str}",
                color="#FFFFFF"
            ))
            salida.controls.append(ft.Text("Restricciones:", color="#FFFFFF"))
            for i, line in enumerate(restr_lines, 1):
                salida.controls.append(ft.Text(f"  {i}. {line}", color="#FFFFFF"))

            tablas = simplex_solver(c, np.array(A), np.array(b))
            num_constraints = len(b)

            # Mostrar tablas de iteraciones
            for it, tab in tablas:
                salida.controls.append(ft.Text(
                    f"\nIteración {it}:",
                    weight=ft.FontWeight.BOLD,
                    color="#90EE90"
                ))
                headers, rows = format_tableau(tab, variables, num_constraints)
                
                # Crear tabla con estilo
                data_columns = []
                for h in headers:
                    data_columns.append(
                        ft.DataColumn(
                            ft.Text(
                                h, 
                                color="#FFFFFF", 
                                weight=ft.FontWeight.BOLD,
                                size=12
                            )
                        )
                    )
                
                data_rows = []
                for row in rows:
                    cells = []
                    for cell in row:
                        cells.append(
                            ft.DataCell(
                                ft.Text(
                                    cell, 
                                    color="#FFFFFF",
                                    size=11
                                )
                            )
                        )
                    data_rows.append(ft.DataRow(cells=cells))
                
                grid = ft.DataTable(
                    columns=data_columns,
                    rows=data_rows,
                    border=ft.border.all(1, "#FFFFFF"),
                    border_radius=5,
                    horizontal_margin=5,
                    vertical_lines=ft.border.BorderSide(1, "#FFFFFF"),
                    horizontal_lines=ft.border.BorderSide(1, "#FFFFFF"),
                )
                salida.controls.append(grid)

            # Mostrar resultados finales
            resultados, z_val = obtener_resultados(tablas[-1][1], variables, num_constraints)
            salida.controls.append(ft.Text(
                "\nResultados finales:",
                weight=ft.FontWeight.BOLD,
                color="#90EE90",
                size=16
            ))
            for var, val in resultados.items():
                salida.controls.append(ft.Text(
                    f"{var} = {val:.3f}",
                    color="#FFFFFF"
                ))
            salida.controls.append(ft.Text(
                f"Z = {z_val:.3f}",
                weight=ft.FontWeight.BOLD,
                color="#FFD700",
                size=18
            ))

        except Exception as ex:
            error_text.value = f"Error: {ex}"
            error_text.visible = True

        page.update()

    resolver_btn = ft.ElevatedButton(
        text="Resolver con Simplex",
        on_click=resolver,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
            color=ft.Colors.BLACK,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        width=250
    )

    # Contenedor principal con scroll
    form_column = ft.Column(
        [
            title,
            info,
            func_obj_field,
            restricciones_field,
            ft.Container(resolver_btn, alignment=ft.alignment.center),
            ft.Container(error_text, alignment=ft.alignment.center),
            ft.Text("Proceso de solución:", color="#FFFFFF", weight=ft.FontWeight.BOLD),
            salida
        ],
        spacing=15,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
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

