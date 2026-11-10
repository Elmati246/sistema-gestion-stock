
from datetime import datetime, date, timedelta


# ==========================================
# CLASE PRODUCTO
# ==========================================

class Producto:

    def __init__(self, codigo, descripcion, marca, precio,
                 impuestos, oferta, descuento, stock,
                 stock_minimo, vencimiento, categoria):

        self.codigo = codigo
        self.descripcion = descripcion
        self.marca = marca
        self.precio = precio
        self.impuestos = impuestos
        self.oferta = oferta
        self.descuento = descuento
        self.stock = stock
        self.stock_minimo = stock_minimo
        self.vencimiento = vencimiento
        self.categoria = categoria

    # Actualizar el precio sin impuestos
    def actualizar_precio(self, nuevo_precio):
        if nuevo_precio >= 0:
            self.precio = nuevo_precio
        else:
            print("El precio no puede ser negativo.")

    # Calcular el precio de venta
    def obtener_precio_venta(self):

        precio_final = self.precio + (self.precio * self.impuestos / 100)

        if self.oferta:
            precio_final = precio_final - (precio_final * self.descuento / 100)

        return precio_final

    # Actualizar el stock
    def actualizar_stock(self, cantidad, operacion):

        if cantidad <= 0:
            print("La cantidad debe ser mayor a cero.")
            return

        if operacion == "ingreso":
            self.stock = self.stock + cantidad

        elif operacion == "egreso":
            if cantidad <= self.stock:
                self.stock = self.stock - cantidad
            else:
                print("No hay suficiente stock.")

        else:
            print("Operación no válida.")

    # Comprobar si el stock está por debajo del mínimo
    def stock_bajo(self):
        return self.stock < self.stock_minimo

    # Comprobar si el producto está vencido
    def esta_vencido(self):

        fecha_vencimiento = datetime.strptime(
            self.vencimiento, "%d/%m/%Y"
        ).date()

        return fecha_vencimiento < date.today()

    # Comprobar si vence en los próximos tres meses
    def vence_en_tres_meses(self):

        fecha_vencimiento = datetime.strptime(
            self.vencimiento, "%d/%m/%Y"
        ).date()

        hoy = date.today()
        limite = hoy + timedelta(days=90)

        return hoy <= fecha_vencimiento <= limite


# ==========================================
# DICCIONARIO DE PRODUCTOS
# ==========================================

productos = {

    "001": Producto(1, "Leche entera", "La Serenísima", 1500, 21, False, 0, 50, 10, "15/12/2026", "Lácteos"),

    "002": Producto(2, "Leche descremada", "Verónica", 1400, 21, True, 10, 30, 8, "20/12/2026", "Lácteos"),

    "003": Producto(3, "Yogur frutilla", "Ser", 1200, 21, False, 0, 25, 5, "01/11/2026", "Lácteos"),

    "004": Producto(4, "Queso cremoso", "La Paulina", 6500, 21, True, 15, 20, 5, "05/12/2026", "Lácteos"),

    "005": Producto(5, "Manteca", "Sancor", 2300, 21, False, 0, 15, 5, "18/12/2026", "Lácteos"),

    "006": Producto(6, "Arroz", "Gallo", 1800, 10.5, False, 0, 60, 15, "01/08/2027", "Almacén"),

    "007": Producto(7, "Fideos", "Matarazzo", 1300, 10.5, True, 10, 45, 10, "15/07/2027", "Almacén"),

    "008": Producto(8, "Aceite de girasol", "Cocinero", 3200, 21, False, 0, 35, 10, "20/06/2027", "Almacén"),

    "009": Producto(9, "Azúcar", "Ledesma", 1600, 10.5, False, 0, 40, 10, "01/09/2027", "Almacén"),

    "010": Producto(10, "Harina", "Pureza", 1100, 10.5, True, 5, 55, 15, "10/08/2026", "Almacén"),

    "011": Producto(11, "Sal fina", "Celusal", 900, 21, False, 0, 30, 8, "01/10/2027", "Almacén"),

    "012": Producto(12, "Yerba mate", "Playadito", 3500, 21, False, 0, 40, 10, "15/05/2027", "Almacén"),

    "013": Producto(13, "Café", "Cabrales", 5200, 21, True, 10, 20, 5, "20/09/2027", "Almacén"),

    "014": Producto(14, "Mantecol", "Georgalos", 2000, 21, False, 0, 35, 10, "01/04/2027", "Golosinas"),

    "015": Producto(15, "Galletitas saladas", "Criollitas", 1400, 21, True, 10, 28, 8, "10/05/2027", "Galletitas"),

    "016": Producto(16, "Chocolate", "Milka", 2800, 21, False, 0, 22, 5, "15/03/2027", "Golosinas"),

    "017": Producto(17, "Caramelos", "Arcor", 800, 21, False, 0, 70, 20, "01/12/2027", "Golosinas"),

    "018": Producto(18, "Gaseosa cola", "Coca-Cola", 2500, 21, True, 15, 50, 12, "01/06/2027", "Bebidas"),

    "019": Producto(19, "Agua mineral", "Villavicencio", 1300, 21, False, 0, 60, 15, "01/07/2027", "Bebidas"),

    "020": Producto(20, "Jugo de durazno", "Cepita", 1800, 21, False, 0, 25, 8, "20/12/2026", "Bebidas"),

    "021": Producto(21, "Detergente", "Magistral", 2100, 21, False, 0, 30, 8, "01/01/2028", "Limpieza"),

    "022": Producto(22, "Lavandina", "Ayudín", 1600, 21, True, 10, 35, 10, "01/02/2027", "Limpieza"),

    "023": Producto(23, "Jabón en polvo", "Ala", 3900, 21, False, 0, 20, 5, "01/01/2028", "Limpieza"),

    "024": Producto(24, "Suavizante", "Vivere", 2800, 21, False, 0, 18, 5, "01/01/2028", "Limpieza"),

    "025": Producto(25, "Shampoo", "Sedal", 3200, 21, True, 10, 25, 6, "01/01/2028", "Higiene"),

    "026": Producto(26, "Acondicionador", "Pantene", 4500, 21, False, 0, 15, 5, "01/01/2028", "Higiene"),

    "027": Producto(27, "Papel higiénico", "Higienol", 2400, 21, False, 0, 40, 10, "01/01/2028", "Higiene"),

    "028": Producto(28, "Pasta dental", "Colgate", 1900, 21, True, 5, 32, 8, "01/01/2028", "Higiene"),

    "029": Producto(29, "Galletitas de agua", "Express", 1500, 21, False, 0, 25, 8, "01/05/2027", "Galletitas"),

    "030": Producto(30, "Atún en lata", "La Campagnola", 2900, 21, False, 0, 20, 5, "01/10/2027", "Conservas")

}

# Permite utilizar los productos desde otros archivos
if __name__ == "__main__":
    print("Sistema de productos cargado correctamente.")

# ==========================================
# MOSTRAR LOS PRODUCTOS
# ==========================================

print("LISTADO DE PRODUCTOS DEL SUPERMERCADO")
print("--------------------------------------")

for codigo, producto in productos.items():

    print("Código:", codigo)
    print("Producto:", producto.descripcion)
    print("Stock actual:", producto.stock)
    print("Precio de venta: $", round(producto.obtener_precio_venta(), 2))
    print("--------------------------------------")
