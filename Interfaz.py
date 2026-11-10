import customtkinter as ctk
import importlib.util
import contextlib
import io
import json
import os
from datetime import datetime
from tkinter import messagebox

# =========================================
# CARGAR PRODUCTOS
# =========================================

especificacion = importlib.util.spec_from_file_location(
    "trabajo",
    "Trabajo-practico.py"
)

trabajo = importlib.util.module_from_spec(especificacion)

# Evitamos que se impriman los 30 productos en la terminal
with contextlib.redirect_stdout(io.StringIO()):
    especificacion.loader.exec_module(trabajo)

productos = trabajo.productos

# =========================================
# GUARDAR Y CARGAR PRODUCTOS
# =========================================

ARCHIVO_DATOS = "productos.json"


def guardar_datos():

    datos = {}

    for codigo, producto in productos.items():

        datos[codigo] = {
            "codigo": producto.codigo,
            "descripcion": producto.descripcion,
            "marca": producto.marca,
            "precio": producto.precio,
            "impuestos": producto.impuestos,
            "oferta": producto.oferta,
            "descuento": producto.descuento,
            "stock": producto.stock,
            "stock_minimo": producto.stock_minimo,
            "vencimiento": producto.vencimiento,
            "categoria": producto.categoria
        }

    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)


def cargar_datos():

    if os.path.exists(ARCHIVO_DATOS):

        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        # Eliminar los productos que fueron borrados
        for codigo in list(productos.keys()):
            if codigo not in datos:
                del productos[codigo]

        # Recuperar los productos guardados
        for codigo, valores in datos.items():

            if codigo in productos:

                producto = productos[codigo]

                producto.precio = valores.get("precio", producto.precio)
                producto.stock = valores.get("stock", producto.stock)
                producto.oferta = valores.get("oferta", producto.oferta)
                producto.descuento = valores.get("descuento", producto.descuento)

            elif "descripcion" in valores:

                productos[codigo] = trabajo.Producto(
                    int(valores.get("codigo", codigo)),
                    valores["descripcion"],
                    valores["marca"],
                    float(valores["precio"]),
                    float(valores["impuestos"]),
                    bool(valores["oferta"]),
                    float(valores["descuento"]),
                    int(valores["stock"]),
                    int(valores["stock_minimo"]),
                    valores["vencimiento"],
                    valores["categoria"]
                )


cargar_datos()

# =========================================
# CONFIGURACION
# =========================================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

ventana = ctk.CTk()
ventana.title("Sistema de Gestion de Stock")
ventana.geometry("1250x750")
ventana.minsize(1050, 650)


# =========================================
# FUNCIONES
# =========================================

def actualizar_resumen():

    total = len(productos)
    stock_bajo = 0
    proximos_vencer = 0

    for producto in productos.values():

        if producto.stock_bajo():
            stock_bajo += 1

        if producto.vence_en_tres_meses() and not producto.esta_vencido():
            proximos_vencer += 1

    tarjeta_total.configure(text=str(total))
    tarjeta_stock.configure(text=str(stock_bajo))
    tarjeta_vencimientos.configure(text=str(proximos_vencer))


def actualizar_tabla(*args):

    # Limpiar la tabla anterior
    for elemento in tabla.winfo_children():
        elemento.destroy()

    busqueda = buscador.get().lower().strip()
    filtro = selector_filtro.get()

    encabezados = [
        "Codigo",
        "Descripcion",
        "Marca",
        "Categoria",
        "Precio sin impuestos",
        "% Impuestos",
        "Oferta",
        "Descuento",
        "Precio de venta",
        "Stock",
        "Stock minimo",
        "Vencimiento",
        "Estado"
        ]
    
    # Distribuir el espacio entre las columnas
    for columna in range(len(encabezados)):
        tabla.grid_columnconfigure(columna, weight=1)

    # Crear encabezados
    for columna, texto in enumerate(encabezados):

        etiqueta = ctk.CTkLabel(
            tabla,
            text=texto,
            font=("Arial", 13, "bold"))

        etiqueta.grid(
            row=0,
            column=columna,
            padx=10,
            pady=12,
            sticky="ew")

    fila = 1

    # Recorrer todos los productos
    for codigo, producto in productos.items():

        nombre = producto.descripcion.lower()

        codigo_texto = str(codigo)

        codigo_buscado = busqueda.zfill(3)

        if busqueda not in nombre and codigo_buscado != codigo_texto:
            continue

        # Aplicar filtros
        if filtro == "Stock bajo":
            if not producto.stock_bajo():
                continue

        elif filtro == "Proximos a vencer":
            if not producto.vence_en_tres_meses() or producto.esta_vencido():
                continue

        elif filtro == "Vencidos":
            if not producto.esta_vencido():
                continue

        # Obtener datos
        oferta = "Si" if producto.oferta else "No"

        descuento = str(producto.descuento) + "%" if producto.oferta else "0%"

        # Determinar el estado del producto
        if producto.esta_vencido():
            estado = "VENCIDO"
            color = "#F8D7DA"

        elif producto.stock_bajo():
            estado = "STOCK BAJO"
            color = "#FFF0C2"

        elif producto.vence_en_tres_meses():
            estado = "POR VENCER"
            color = "#FFE5CC"

        else:
            estado = "NORMAL"
            color = "#D9F2E6"

        datos = [
            codigo,
            producto.descripcion,
            producto.marca,
            producto.categoria,
            "$ " + str(round(producto.precio, 2)),
            str(producto.impuestos) + "%",
            oferta,
            descuento,
            "$ " + str(round(producto.obtener_precio_venta(), 2)),
            producto.stock,
            producto.stock_minimo,
            producto.vencimiento,
            estado
        ]

        # Mostrar datos en la tabla
        for columna, dato in enumerate(datos):

            etiqueta = ctk.CTkLabel(
                tabla,
                text=str(dato),
                font=("Arial", 12),
                fg_color=color,
                corner_radius=5
            )

            etiqueta.grid(
                row=fila,
                column=columna,
                padx=10,
                pady=10,
                sticky="ew"
            )

        fila += 1


    # Si no hay resultados
    if fila == 1:

        mensaje = ctk.CTkLabel(
            tabla,
            text="No se encontraron productos.",
            font=("Arial", 14))

        mensaje.grid(row=1, column=0, padx=15, pady=20)

    actualizar_resumen()


# =========================================
# REGISTRAR INGRESO O SALIDA
# =========================================


def modificar_precio_oferta():

    ventana_edicion = ctk.CTkToplevel(ventana)
    ventana_edicion.title("Modificar precio y oferta")
    ventana_edicion.geometry("430x480")
    ventana_edicion.transient(ventana)
    ventana_edicion.grab_set()

    titulo = ctk.CTkLabel(
        ventana_edicion,
        text="Modificar producto",
        font=("Arial", 22, "bold")
    )
    titulo.pack(pady=20)

    opciones = [
        str(codigo) + " - " + producto.descripcion
        for codigo, producto in productos.items()
    ]

    selector = ctk.CTkOptionMenu(
        ventana_edicion,
        values=opciones,
        width=320
    )
    selector.pack(pady=12)

    entrada_precio = ctk.CTkEntry(
        ventana_edicion,
        placeholder_text="Nuevo precio sin impuestos",
        width=320
    )
    entrada_precio.pack(pady=12)

    oferta_var = ctk.StringVar(value="No")

    selector_oferta = ctk.CTkOptionMenu(
        ventana_edicion,
        values=["No", "Si"],
        variable=oferta_var,
        width=320
    )
    selector_oferta.pack(pady=12)

    entrada_descuento = ctk.CTkEntry(
        ventana_edicion,
        placeholder_text="Descuento en porcentaje",
        width=320
    )
    entrada_descuento.pack(pady=12)

    mensaje = ctk.CTkLabel(
        ventana_edicion,
        text=""
    )
    mensaje.pack(pady=8)

    def cargar_producto(eleccion):

        codigo = eleccion.split(" - ")[0]
        producto = productos[codigo]

        entrada_precio.delete(0, "end")
        entrada_precio.insert(0, str(producto.precio))

        oferta_var.set("Si" if producto.oferta else "No")

        entrada_descuento.delete(0, "end")
        entrada_descuento.insert(0, str(producto.descuento))

    def guardar_cambios():

        try:
            codigo = selector.get().split(" - ")[0]
            producto = productos[codigo]

            precio = float(entrada_precio.get().replace(",", "."))
            descuento = float(entrada_descuento.get().replace(",", "."))

            if precio < 0:
                mensaje.configure(
                    text="El precio no puede ser negativo.",
                    text_color="red"
                )
                return

            if descuento < 0 or descuento > 100:
                mensaje.configure(
                    text="El descuento debe estar entre 0 y 100.",
                    text_color="red"
                )
                return

            if oferta_var.get() == "No" and descuento > 0:
                mensaje.configure(
                    text="Activá la oferta para aplicar un descuento.",
                    text_color="red"
                )
                return

            producto.actualizar_precio(precio)
            producto.oferta = (oferta_var.get() == "Si")
            producto.descuento = descuento

            guardar_datos()
            actualizar_tabla()

            ventana_edicion.destroy()

        except ValueError:
            mensaje.configure(
                text="Ingresá valores numéricos válidos.",
                text_color="red"
            )

    selector.configure(command=cargar_producto)

    cargar_producto(selector.get())

    boton_guardar = ctk.CTkButton(
        ventana_edicion,
        text="Guardar cambios",
        command=guardar_cambios
    )
    boton_guardar.pack(pady=15)

# =========================================
# AGREGAR PRODUCTO
# =========================================

def siguiente_codigo():

    if not productos:
        return "001"

    mayor = max(int(codigo) for codigo in productos.keys())

    return str(mayor + 1).zfill(3)


def agregar_producto():

    ventana_alta = ctk.CTkToplevel(ventana)
    ventana_alta.title("Agregar producto")
    ventana_alta.geometry("440x720")
    ventana_alta.transient(ventana)
    ventana_alta.grab_set()

    titulo = ctk.CTkLabel(
        ventana_alta,
        text="Nuevo producto",
        font=("Arial", 22, "bold")
    )
    titulo.pack(pady=15)

    codigo_nuevo = siguiente_codigo()

    ctk.CTkLabel(
        ventana_alta,
        text="Código asignado: " + codigo_nuevo
    ).pack(pady=5)

    campos = {}

    datos_campos = [
        ("descripcion", "Descripción"),
        ("marca", "Marca"),
        ("precio", "Precio sin impuestos"),
        ("impuestos", "Porcentaje de impuestos"),
        ("descuento", "Descuento (%)"),
        ("stock", "Stock inicial"),
        ("stock_minimo", "Stock mínimo"),
        ("vencimiento", "Vencimiento (DD/MM/AAAA)"),
        ("categoria", "Categoría")
    ]

    for clave, texto in datos_campos:

        entrada = ctk.CTkEntry(
            ventana_alta,
            placeholder_text=texto,
            width=330
        )

        entrada.pack(pady=6)

        campos[clave] = entrada

    oferta_var = ctk.StringVar(value="No")

    ctk.CTkLabel(
        ventana_alta,
        text="¿Está en oferta?"
    ).pack(pady=5)

    selector_oferta = ctk.CTkOptionMenu(
        ventana_alta,
        values=["No", "Si"],
        variable=oferta_var,
        width=330
    )
    selector_oferta.pack(pady=5)

    mensaje = ctk.CTkLabel(
        ventana_alta,
        text=""
    )
    mensaje.pack(pady=5)

    def confirmar_alta():

        try:

            descripcion = campos["descripcion"].get().strip()
            marca = campos["marca"].get().strip()
            categoria = campos["categoria"].get().strip()

            if not descripcion or not marca or not categoria:
                mensaje.configure(
                    text="Completá descripción, marca y categoría.",
                    text_color="red"
                )
                return

            precio = float(campos["precio"].get().replace(",", "."))
            impuestos = float(campos["impuestos"].get().replace(",", "."))
            descuento = float(campos["descuento"].get().replace(",", "."))

            stock = int(campos["stock"].get())
            stock_minimo = int(campos["stock_minimo"].get())

            vencimiento = campos["vencimiento"].get().strip()

            # Validar fecha
            datetime.strptime(vencimiento, "%d/%m/%Y")

            if precio < 0 or impuestos < 0:
                raise ValueError

            if descuento < 0 or descuento > 100:
                mensaje.configure(
                    text="El descuento debe estar entre 0 y 100.",
                    text_color="red"
                )
                return

            if stock < 0 or stock_minimo < 0:
                mensaje.configure(
                    text="El stock no puede ser negativo.",
                    text_color="red"
                )
                return

            oferta = oferta_var.get() == "Si"

            if not oferta and descuento > 0:
                mensaje.configure(
                    text="Si no está en oferta, el descuento debe ser 0.",
                    text_color="red"
                )
                return

            # Crear el nuevo producto
            nuevo = trabajo.Producto(
                int(codigo_nuevo),
                descripcion,
                marca,
                precio,
                impuestos,
                oferta,
                descuento,
                stock,
                stock_minimo,
                vencimiento,
                categoria
            )

            # Agregarlo al diccionario
            productos[codigo_nuevo] = nuevo

            # Guardar y actualizar
            guardar_datos()
            actualizar_tabla()

            ventana_alta.destroy()

        except ValueError:

            mensaje.configure(
                text="Revisá los números y la fecha.",
                text_color="red"
            )

    boton_guardar = ctk.CTkButton(
        ventana_alta,
        text="Guardar producto",
        command=confirmar_alta,
        width=220
    )
    boton_guardar.pack(pady=15)


# =========================================
# ELIMINAR PRODUCTO
# =========================================

def eliminar_producto():

    if not productos:
        messagebox.showinfo(
            "Eliminar producto",
            "No hay productos para eliminar."
        )
        return

    ventana_baja = ctk.CTkToplevel(ventana)
    ventana_baja.title("Eliminar producto")
    ventana_baja.geometry("440x260")
    ventana_baja.transient(ventana)
    ventana_baja.grab_set()

    titulo = ctk.CTkLabel(
        ventana_baja,
        text="Eliminar producto",
        font=("Arial", 22, "bold")
    )
    titulo.pack(pady=20)

    opciones = [
        str(codigo) + " - " + producto.descripcion
        for codigo, producto in productos.items()
    ]

    selector = ctk.CTkOptionMenu(
        ventana_baja,
        values=opciones,
        width=340
    )
    selector.pack(pady=15)

    def confirmar_baja():

        seleccion = selector.get()

        codigo = seleccion.split(" - ")[0]

        producto = productos[codigo]

        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Seguro que querés eliminar " + producto.descripcion + "?"
        )

        if respuesta:

            del productos[codigo]

            guardar_datos()
            actualizar_tabla()

            ventana_baja.destroy()

    boton_eliminar = ctk.CTkButton(
        ventana_baja,
        text="Eliminar producto",
        command=confirmar_baja,
        fg_color="#B83232",
        hover_color="#922B2B",
        width=220
    )
    boton_eliminar.pack(pady=20)

def registrar_movimiento(tipo):

    ventana_movimiento = ctk.CTkToplevel(ventana)
    ventana_movimiento.title("Movimiento de stock")
    ventana_movimiento.geometry("400x350")
    ventana_movimiento.transient(ventana)
    ventana_movimiento.grab_set()

    titulo = ctk.CTkLabel(
        ventana_movimiento,
        text="Registrar " + tipo,
        font=("Arial", 22, "bold"))
    titulo.pack(pady=20)

    opciones = [
        str(codigo) + " - " + producto.descripcion
        for codigo, producto in productos.items()]

    selector_producto = ctk.CTkOptionMenu(
        ventana_movimiento,
        values=opciones,
        width=300)
    selector_producto.pack(pady=15)

    entrada_cantidad = ctk.CTkEntry(
        ventana_movimiento,
        placeholder_text="Cantidad de unidades",
        width=300)
    entrada_cantidad.pack(pady=15)

    mensaje = ctk.CTkLabel(
        ventana_movimiento,
        text="")
    mensaje.pack(pady=5)

    def confirmar():

        try:
            cantidad = int(entrada_cantidad.get())

            if cantidad <= 0:
                mensaje.configure(
                    text="La cantidad debe ser mayor a cero.",
                    text_color="red")
                return

            seleccion = selector_producto.get()
            codigo = seleccion.split(" - ")[0]

            producto = productos[codigo]

            if tipo == "ingreso":

                producto.actualizar_stock(cantidad, "ingreso")

            else:

                if cantidad > producto.stock:
                    mensaje.configure(
                        text="No hay suficiente stock.",
                        text_color="red")
                    return

                producto.actualizar_stock(cantidad, "egreso")

            guardar_datos()
            actualizar_tabla()
            ventana_movimiento.destroy()

        except ValueError:

            mensaje.configure(text="Ingresá una cantidad válida.",text_color="red")

    boton_confirmar = ctk.CTkButton(
        ventana_movimiento,
        text="Confirmar movimiento",
        command=confirmar)
    boton_confirmar.pack(pady=20)


# =========================================
# ENCABEZADO
# =========================================

encabezado = ctk.CTkFrame(
    ventana,
    fg_color="transparent")
encabezado.pack(fill="x", padx=25, pady=(20, 5))

titulo = ctk.CTkLabel(
    encabezado,
    text="Sistema de Gestion de Stock",
    font=("Arial", 28, "bold"))
titulo.pack(anchor="w")

subtitulo = ctk.CTkLabel(
    encabezado,
    text="Administracion y control de productos",
    font=("Arial", 14),
    text_color="gray")
subtitulo.pack(anchor="w", pady=5)


# =========================================
# TARJETAS DE RESUMEN
# =========================================

resumen = ctk.CTkFrame(
    ventana,
    fg_color="transparent")
resumen.pack(fill="x", padx=25, pady=15)


def crear_tarjeta(contenedor, titulo_tarjeta):

    tarjeta = ctk.CTkFrame(
        contenedor,
        corner_radius=12)
    tarjeta.pack(
        side="left",
        fill="x",
        expand=True,
        padx=7)

    etiqueta_titulo = ctk.CTkLabel(
        tarjeta,
        text=titulo_tarjeta,
        font=("Arial", 14))
    etiqueta_titulo.pack(pady=(15, 5))

    etiqueta_numero = ctk.CTkLabel(
        tarjeta,
        text="0",
        font=("Arial", 28, "bold"))
    etiqueta_numero.pack(pady=(0, 15))

    return etiqueta_numero


tarjeta_total = crear_tarjeta(
    resumen,
    "Total de productos")

tarjeta_stock = crear_tarjeta(
    resumen,
    "Stock bajo")

tarjeta_vencimientos = crear_tarjeta(
    resumen,
    "Por vencer (3 meses)")


# =========================================
# BUSCADOR Y FILTROS
# =========================================

herramientas = ctk.CTkFrame(
    ventana,
    fg_color="transparent")
herramientas.pack(fill="x", padx=30, pady=10)

buscador = ctk.CTkEntry(
    herramientas,
    placeholder_text="Buscar por nombre o codigo...",
    width=280)
buscador.pack(side="left", padx=(0, 15))

selector_filtro = ctk.CTkOptionMenu(
    herramientas,
    values=[
        "Todos",
        "Stock bajo",
        "Proximos a vencer",
        "Vencidos"
    ],
    command=actualizar_tabla)
selector_filtro.pack(side="left")

boton_ingreso = ctk.CTkButton(
    herramientas,
    text="+ Ingresar stock",
    command=lambda: registrar_movimiento("ingreso"))
boton_ingreso.pack(side="right", padx=5)

boton_salida = ctk.CTkButton(
    herramientas,
    text="- Registrar salida",
    command=lambda: registrar_movimiento("salida"))
boton_salida.pack(side="right", padx=5)

boton_modificar = ctk.CTkButton(
    herramientas,
    text="Modificar precio y oferta",
    command=modificar_precio_oferta
)
boton_modificar.pack(side="right", padx=5)

boton_agregar = ctk.CTkButton(
    herramientas,
    text="+ Nuevo producto",
    command=agregar_producto,
    fg_color="#218838",
    hover_color="#19692C"
)
boton_agregar.pack(side="right", padx=5)


boton_eliminar = ctk.CTkButton(
    herramientas,
    text="Eliminar producto",
    command=eliminar_producto,
    fg_color="#B83232",
    hover_color="#922B2B"
)
boton_eliminar.pack(side="right", padx=5)

# =========================================
# TABLA DE PRODUCTOS
# =========================================

contenedor_tabla = ctk.CTkFrame(
    ventana,
    fg_color="#FFFFFF",
    corner_radius=12)
contenedor_tabla.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=(5, 25))

tabla = ctk.CTkScrollableFrame(
    contenedor_tabla,
    fg_color="#FFFFFF",
    corner_radius=10)
tabla.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10)


# =========================================
# INICIAR SISTEMA
# =========================================

buscador.bind(
    "<KeyRelease>",
    actualizar_tabla)

actualizar_tabla()

ventana.mainloop()
