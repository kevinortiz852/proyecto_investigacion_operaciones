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
    if line.startswith("z=") or line.startswith("min="):
        line = line[line.find("=")+1:]
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
        sentido = "<="
    elif ">=" in line:
        left, right = line.split(">=")
        sentido = ">="
    elif "=" in line:
        left, right = line.split("=")
        sentido = "="
    else:
        raise ValueError("Cada restricción debe contener '<=', '>=' o '='")
    
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
    
    return coefs, float(right), sentido

def simplex_dos_fases(c, A, b, sentidos):
    """
    Método de dos fases para minimización corregido
    """
    num_vars = len(c)
    num_rest = len(b)
    
    # FASE 1: Minimizar suma de variables artificiales
    print("=== FASE 1 ===")
    
    # Identificar restricciones que necesitan variables artificiales
    restricciones_artificiales = [i for i, s in enumerate(sentidos) if s in [">=", "="]]
    num_artificiales = len(restricciones_artificiales)
    
    # Matriz aumentada para Fase 1
    total_cols_f1 = num_vars + num_rest + num_artificiales  # +1 para LD después
    
    # Tableau Fase 1
    tableau_f1 = np.zeros((num_rest + 1, total_cols_f1 + 1))  # +1 para LD
    
    # Configurar nombres de variables para Fase 1
    nombres_f1 = [f"x{i+1}" for i in range(num_vars)]
    nombres_f1 += [f"s{i+1}" for i in range(num_rest)]  # Holguras
    nombres_f1 += [f"a{i+1}" for i in range(num_artificiales)]  # Artificiales
    nombres_f1.append("LD")
    
    # Llenar restricciones
    idx_artificial = 0
    for i in range(num_rest):
        # Variables originales
        tableau_f1[i+1, :num_vars] = A[i]
        
        # Variables de holgura
        if sentidos[i] == "<=":
            tableau_f1[i+1, num_vars + i] = 1  # Holgura positiva
        elif sentidos[i] == ">=":
            tableau_f1[i+1, num_vars + i] = -1  # Exceso negativo
            # Variable artificial
            tableau_f1[i+1, num_vars + num_rest + idx_artificial] = 1
            idx_artificial += 1
        elif sentidos[i] == "=":
            # Variable artificial
            tableau_f1[i+1, num_vars + num_rest + idx_artificial] = 1
            idx_artificial += 1
        
        # Lado derecho
        tableau_f1[i+1, -1] = b[i]
    
    # Función objetivo Fase 1: Minimizar suma de artificiales
    for i in range(num_artificiales):
        tableau_f1[0, num_vars + num_rest + i] = 1
    
    # Hacer cero los coeficientes de variables básicas en Z
    for i in range(num_rest):
        if sentidos[i] in [">=", "="]:
            # Encontrar la columna artificial correspondiente
            for j in range(num_artificiales):
                col_art = num_vars + num_rest + j
                if tableau_f1[i+1, col_art] == 1:
                    tableau_f1[0] -= tableau_f1[i+1]
                    break
    
    tablas = []
    tablas.append(("FASE 1 - Tabla Inicial", tableau_f1.copy(), nombres_f1))
    
    # Iteraciones Fase 1
    print("Iterando Fase 1...")
    for iter_f1 in range(10):
        # Verificar optimalidad Fase 1 (minimización)
        if np.all(tableau_f1[0, :-1] >= -1e-8):
            break
        
        # Columna pivote (más negativo)
        col_pivote = np.argmin(tableau_f1[0, :-1])
        
        # Razón mínima
        ratios = []
        for i in range(1, tableau_f1.shape[0]):
            if tableau_f1[i, col_pivote] > 1e-8:
                ratio = tableau_f1[i, -1] / tableau_f1[i, col_pivote]
                if ratio >= 0:
                    ratios.append(ratio)
                else:
                    ratios.append(np.inf)
            else:
                ratios.append(np.inf)
        
        if all(r == np.inf for r in ratios):
            break
        
        fila_pivote = np.argmin(ratios) + 1
        
        # Pivoteo
        pivot_val = tableau_f1[fila_pivote, col_pivote]
        tableau_f1[fila_pivote] /= pivot_val
        
        for i in range(tableau_f1.shape[0]):
            if i != fila_pivote:
                factor = tableau_f1[i, col_pivote]
                tableau_f1[i] -= factor * tableau_f1[fila_pivote]
        
        tablas.append((f"FASE 1 - Iteración {iter_f1 + 1}", tableau_f1.copy(), nombres_f1))
    
    # Verificar factibilidad
    z_fase1 = tableau_f1[0, -1]
    if abs(z_fase1) > 1e-6:
        raise ValueError("El problema no tiene solución factible")
    
    print("=== FASE 2 ===")
    # FASE 2: Usar la función objetivo original
    
    # Preparar tableau para Fase 2
    # Eliminar columnas de variables artificiales
    columnas_a_mantener = []
    for j in range(tableau_f1.shape[1] - 1):  # Excluir LD
        es_artificial = j >= (num_vars + num_rest) and j < (num_vars + num_rest + num_artificiales)
        if not es_artificial:
            columnas_a_mantener.append(j)
    
    # Agregar columna LD
    columnas_a_mantener.append(tableau_f1.shape[1] - 1)
    
    tableau_f2 = tableau_f1[:, columnas_a_mantener]
    
    # Nombres para Fase 2
    nombres_f2 = [nombres_f1[j] for j in columnas_a_mantener[:-1]] + ["LD"]
    
    # CORRECCIÓN: Reemplazar función objetivo por la original con limpieza mejorada
    nueva_fila_z = np.zeros(tableau_f2.shape[1])
    nueva_fila_z[:num_vars] = c  # Coeficientes originales
    nueva_fila_z[-1] = 0  # LD
    
    # CORRECCIÓN MEJORADA: Limpiar coeficientes de variables básicas
    # Iterar múltiples veces para asegurar que todos los coeficientes básicos sean 0
    for _ in range(3):  # Hacer varias pasadas para mayor precisión
        for i in range(1, tableau_f2.shape[0]):
            # Identificar la variable básica en esta fila
            col_basica = -1
            for j in range(tableau_f2.shape[1] - 1):
                if abs(tableau_f2[i, j] - 1.0) < 1e-6:
                    # Verificar si es realmente variable básica
                    es_basica = True
                    for k in range(tableau_f2.shape[0]):
                        if k != i and abs(tableau_f2[k, j]) > 1e-6:
                            es_basica = False
                            break
                    if es_basica:
                        col_basica = j
                        break
            
            if col_basica != -1:
                # Restar la fila multiplicada por el coeficiente de Z
                coef = nueva_fila_z[col_basica]
                if abs(coef) > 1e-10:
                    nueva_fila_z -= coef * tableau_f2[i]
    
    tableau_f2[0] = nueva_fila_z
    
    tablas.append(("FASE 2 - Tabla Inicial", tableau_f2.copy(), nombres_f2))
    
    # Iteraciones Fase 2
    print("Iterando Fase 2...")
    for iter_f2 in range(20):
        # Verificar optimalidad Fase 2 (minimización)
        # Para minimización: óptimo cuando todos los coeficientes en Z son >= 0
        if np.all(tableau_f2[0, :-1] >= -1e-8):
            break
        
        # Columna pivote (más negativo)
        col_pivote = np.argmin(tableau_f2[0, :-1])
        
        # Si el más negativo es >= 0, hemos terminado
        if tableau_f2[0, col_pivote] >= -1e-8:
            break
        
        # Razón mínima
        ratios = []
        for i in range(1, tableau_f2.shape[0]):
            if tableau_f2[i, col_pivote] > 1e-8:
                ratio = tableau_f2[i, -1] / tableau_f2[i, col_pivote]
                if ratio >= 0:
                    ratios.append(ratio)
                else:
                    ratios.append(np.inf)
            else:
                ratios.append(np.inf)
        
        if all(r == np.inf for r in ratios):
            break
        
        fila_pivote = np.argmin(ratios) + 1
        
        # Pivoteo
        pivot_val = tableau_f2[fila_pivote, col_pivote]
        tableau_f2[fila_pivote] /= pivot_val
        
        for i in range(tableau_f2.shape[0]):
            if i != fila_pivote:
                factor = tableau_f2[i, col_pivote]
                tableau_f2[i] -= factor * tableau_f2[fila_pivote]
        
        tablas.append((f"FASE 2 - Iteración {iter_f2 + 1}", tableau_f2.copy(), nombres_f2))
    
    return tablas

def crear_tabla_visual(tabla_data, nombres_vars, titulo):
    """Crea una visualización de tabla para Flet"""
    
    # Encabezados
    headers = ["Ec", "VB"] + nombres_vars
    
    rows = []
    
    # Fila Z (fila 0)
    z_row = ["0", "Z"] + [f"{val:.3f}" for val in tabla_data[0]]
    rows.append(z_row)
    
    # Filas de restricciones
    for i in range(1, tabla_data.shape[0]):
        # Determinar variable básica
        vb = "-"
        for j in range(len(tabla_data[i]) - 1):  # Excluir LD
            if abs(tabla_data[i, j] - 1) < 0.001:
                # Verificar si es la única en la columna
                col_vals = [tabla_data[k, j] for k in range(tabla_data.shape[0])]
                ones_count = sum(1 for val in col_vals if abs(val - 1) < 0.001)
                zeros_count = sum(1 for val in col_vals if abs(val) < 0.001)
                
                if ones_count == 1 and zeros_count == len(col_vals) - 1:
                    vb = nombres_vars[j]
                    break
        
        row_vals = [f"{val:.3f}" for val in tabla_data[i]]
        row = [str(i), vb] + row_vals
        rows.append(row)
    
    # Crear widget de tabla
    data_columns = []
    for header in headers:
        data_columns.append(
            ft.DataColumn(
                ft.Text(
                    header,
                    color="#FFFFFF",
                    weight=ft.FontWeight.BOLD,
                    size=10
                )
            )
        )
    
    data_rows = []
    for row in rows:
        cells = []
        for j, cell in enumerate(row):
            color = "#FFFFFF"
            if j == 1:  # Columna VB
                color = "#87CEEB"
            elif cell.startswith("x") or cell.startswith("s") or cell.startswith("a"):
                color = "#87CEEB"
            cells.append(
                ft.DataCell(
                    ft.Text(
                        cell,
                        color=color,
                        size=9
                    )
                )
            )
        data_rows.append(ft.DataRow(cells=cells))
    
    tabla_widget = ft.Column([
        ft.Text(titulo, color="#90EE90", weight=ft.FontWeight.BOLD),
        ft.Container(
            content=ft.DataTable(
                columns=data_columns,
                rows=data_rows,
                border=ft.border.all(1, "#FFFFFF"),
                border_radius=5,
                horizontal_margin=5,
                vertical_lines=ft.border.BorderSide(1, "#FFFFFF"),
                horizontal_lines=ft.border.BorderSide(1, "#FFFFFF"),
            ),
            padding=10,
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.2, "#000000"),
        )
    ])
    
    return tabla_widget

def main_simplex_minimizacion(page: ft.Page):
    # Configuración del fondo
    fondo = ft.Image(
        src="fondo6.jpg",
        fit=ft.ImageFit.COVER,
        width=page.width,
        height=page.height,
    )

    title = ft.Container(
        content=ft.Text(
            "Método Simplex - Dos Fases (Minimización)",
            size=24,
            weight=ft.FontWeight.BOLD,
            color="#FFFFFF"
        ),
        alignment=ft.alignment.center,
        padding=10
    )

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

    info = ft.Text(
        "Método de dos fases para problemas de minimización con restricciones de igualdad y ≥",
        color="#FFFFFF",
        size=12
    )
    
    func_obj_field = ft.TextField(
        label="Función Objetivo (Minimizar)", 
        value="min=2x1+x2+3x3",
        **field_style
    )
    
    restricciones_field = ft.TextField(
        label="Restricciones (una por línea)", 
        value="5x1+2x2+7x3=420\n3x1+2x2+5x3>=280\nx1+x3<=100",
        width=500,
        height=120,
        text_align=ft.TextAlign.LEFT,
        color="#FFFFFF",
        bgcolor="#80333333",
        border_color="#FFFFFF",
        border_radius=10,
        multiline=True,
        min_lines=3,
        max_lines=5
    )

    # Área de resultados con scroll
    salida = ft.Container(
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
        ),
        height=500,
        padding=10,
        border=ft.border.all(1, "#FFFFFF"),
        border_radius=10,
        bgcolor=ft.Colors.with_opacity(0.1, "#000000"),
    )

    error_text = ft.Text(color="red", visible=False)

    def resolver_minimizacion(e):
        # Limpiar resultados anteriores
        salida.content.controls.clear()
        error_text.visible = False
        
        try:
            func_obj_str = func_obj_field.value.strip()
            restr_str = restricciones_field.value.strip()

            if not func_obj_str or not restr_str:
                raise ValueError("Por favor complete todos los campos")

            variables = detect_variables(func_obj_str, restr_str)
            if not variables:
                raise ValueError("No se detectaron variables x1, x2, ...")

            c = parse_function_objective(func_obj_str, variables)

            restr_lines = [line for line in restr_str.split("\n") if line.strip()]
            A = []
            b = []
            sentidos = []
            
            salida.content.controls.append(ft.Text("✓ Problema cargado correctamente", color="#90EE90"))
            salida.content.controls.append(ft.Text(f"Función objetivo: {func_obj_str}", color="#FFFFFF"))
            salida.content.controls.append(ft.Text("Restricciones:", color="#FFFFFF"))
            
            for line in restr_lines:
                coefs, val, sentido = parse_restriction(line, variables)
                A.append(coefs)
                b.append(val)
                sentidos.append(sentido)
                salida.content.controls.append(ft.Text(f"  {line} (tipo: {sentido})", color="#FFFFFF"))

            # Resolver con método de dos fases
            salida.content.controls.append(ft.Text(
                "\n🔄 Aplicando método de dos fases...", 
                color="#87CEEB", weight=ft.FontWeight.BOLD
            ))
            
            tablas = simplex_dos_fases(c, np.array(A), np.array(b), sentidos)
            
            # Mostrar todas las tablas
            for titulo, tabla_data, nombres_vars in tablas:
                tabla_widget = crear_tabla_visual(tabla_data, nombres_vars, titulo)
                salida.content.controls.append(tabla_widget)
            
            # Mostrar solución final
            ultima_tabla = tablas[-1][1]
            salida.content.controls.append(ft.Text(
                "\n🎯 SOLUCIÓN ÓPTIMA ENCONTRADA:", 
                weight=ft.FontWeight.BOLD, color="#32CD32", size=16
            ))
            
            # Extraer valores de las variables originales
            valores_finales = {}
            for i, var in enumerate(variables):
                valor = 0.0
                # Buscar si la variable es básica
                for j in range(1, ultima_tabla.shape[0]):
                    if abs(ultima_tabla[j, i] - 1) < 0.001:
                        # Verificar si es variable básica
                        col_data = ultima_tabla[:, i]
                        ones_count = sum(1 for val in col_data if abs(val - 1) < 0.001)
                        zeros_count = sum(1 for val in col_data if abs(val) < 0.001)
                        
                        if ones_count == 1 and zeros_count == len(col_data) - 1:
                            valor = ultima_tabla[j, -1]
                            break
                
                valores_finales[var] = valor
                salida.content.controls.append(ft.Text(f"{var} = {valor:.3f}", color="#FFFFFF", size=14))
            
            z_val = ultima_tabla[0, -1]
            salida.content.controls.append(ft.Text(
                f"Valor mínimo de Z = {z_val:.3f}", 
                weight=ft.FontWeight.BOLD, color="#FFD700", size=18
            ))
            
            # Verificación de restricciones
            salida.content.controls.append(ft.Text("\n✅ Verificación de restricciones:", color="#90EE90"))
            for i, (coefs, val, sentido) in enumerate(zip(A, b, sentidos)):
                resultado = sum(coefs[j] * valores_finales[variables[j]] for j in range(len(variables)))
                if sentido == "=":
                    status = "✓" if abs(resultado - val) < 0.001 else "✗"
                    salida.content.controls.append(ft.Text(f"R{i+1}: {resultado:.3f} = {val} {status}", color="#FFFFFF"))
                elif sentido == "<=":
                    status = "✓" if resultado <= val + 0.001 else "✗"
                    salida.content.controls.append(ft.Text(f"R{i+1}: {resultado:.3f} <= {val} {status}", color="#FFFFFF"))
                elif sentido == ">=":
                    status = "✓" if resultado >= val - 0.001 else "✗"
                    salida.content.controls.append(ft.Text(f"R{i+1}: {resultado:.3f} >= {val} {status}", color="#FFFFFF"))

        except Exception as ex:
            error_text.value = f"Error: {str(ex)}"
            error_text.visible = True

        salida.content.update()
        page.update()

    resolver_btn = ft.ElevatedButton(
        text="Resolver con Dos Fases",
        on_click=resolver_minimizacion,
        style=ft.ButtonStyle(
            bgcolor="#4CAF50",
            color="white",
            padding=20,
        ),
        width=250
    )

    # Información adicional
    info_adicional = ft.Container(
        content=ft.Column([
            ft.Text("Método de Dos Fases:", color="#87CEEB", weight=ft.FontWeight.BOLD),
            ft.Text("• Fase 1: Minimizar suma de variables artificiales", color="#FFFFFF", size=12),
            ft.Text("• Fase 2: Optimizar función objetivo original", color="#FFFFFF", size=12),
            ft.Text("• Maneja restricciones =, >=, <=", color="#FFFFFF", size=12),
        ]),
        padding=10,
        margin=10,
        bgcolor=ft.Colors.with_opacity(0.3, "#000000"),
        border_radius=10
    )

    # Contenedor principal con scroll
    main_content = ft.Container(
        content=ft.Column(
            [
                title,
                info,
                func_obj_field,
                restricciones_field,
                info_adicional,
                ft.Container(resolver_btn, alignment=ft.alignment.center),
                ft.Container(error_text, alignment=ft.alignment.center),
                ft.Text("Proceso y Resultados:", color="#FFFFFF", weight=ft.FontWeight.BOLD, size=16),
                salida,
                ft.Container(height=20),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=20,
        expand=True,
    )

    # Layout principal
    return ft.Stack(
        [
            fondo,
            ft.Container(
                content=main_content,
                expand=True,
            )
        ],
        expand=True,
    )