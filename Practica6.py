from collections import deque

class Jugador:
    """Clase que representa a un jugador en la arena"""
    def __init__(self, nombre, hp, ataque, defensa, x, y):
        self.nombre = nombre
        self.hp = hp
        self.ataque = ataque
        self.defensa = defensa
        self.x = x
        self.y = y
        self.vivo = True

    def recibir_dano(self, dano):
        """Aplica daño al jugador considerando su defensa"""
        dano_real = max(1, dano - self.defensa)  # Mínimo 1 de daño
        self.hp -= dano_real
        if self.hp <= 0:
            self.hp = 0
            self.vivo = False
        return dano_real

    def mover(self, nuevo_x, nuevo_y):
        """Cambia la posición del jugador"""
        self.x = nuevo_x
        self.y = nuevo_y

    def __str__(self):
        return f"{self.nombre} (HP: {self.hp}, ATK: {self.ataque}, DEF: {self.defensa}) en ({self.x},{self.y})"

class Arena:
    """Clase principal que maneja la arena de combate"""
    def __init__(self, tamaño=5):
        self.tamaño = tamaño
        self.matriz = [[None for _ in range(tamaño)] for _ in range(tamaño)]
        self.jugadores = []
        self.cola_turnos = deque()  # Cola FIFO para turnos
        self.pila_historial = []    # Pila para historial de acciones
        self.numero_turno = 0

    def agregar_jugador(self, jugador):
        """Agrega un jugador a la arena y a la cola de turnos"""
        if self._es_posicion_valida(jugador.x, jugador.y) and self.matriz[jugador.y][jugador.x] is None:
            self.matriz[jugador.y][jugador.x] = jugador
            self.jugadores.append(jugador)
            self.cola_turnos.append(jugador)
            return True
        return False

    def _es_posicion_valida(self, x, y):
        """Verifica si una posición está dentro de los límites"""
        return 0 <= x < self.tamaño and 0 <= y < self.tamaño

    def _obtener_jugadores_adyacentes(self, jugador):
        """Obtiene jugadores adyacentes (arriba, abajo, izquierda, derecha)"""
        adyacentes = []
        direcciones = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # arriba, abajo, derecha, izquierda

        for dx, dy in direcciones:
            nuevo_x = jugador.x + dx
            nuevo_y = jugador.y + dy

            if self._es_posicion_valida(nuevo_x, nuevo_y):
                objetivo = self.matriz[nuevo_y][nuevo_x]
                if objetivo and objetivo.vivo:
                    adyacentes.append(objetivo)

        return adyacentes

    def mover_jugador(self, jugador, direccion):
        """Mueve un jugador en la dirección especificada"""
        movimientos = {
            'arriba': (0, -1),
            'abajo': (0, 1),
            'izquierda': (-1, 0),
            'derecha': (1, 0)
        }

        if direccion not in movimientos:
            return False

        dx, dy = movimientos[direccion]
        nuevo_x = jugador.x + dx
        nuevo_y = jugador.y + dy

        # Verificar límites y si la celda está vacía
        if not self._es_posicion_valida(nuevo_x, nuevo_y) or self.matriz[nuevo_y][nuevo_x] is not None:
            return False

        # Guardar posición anterior
        pos_anterior = (jugador.x, jugador.y)

        # Realizar movimiento
        self.matriz[jugador.y][jugador.x] = None
        jugador.mover(nuevo_x, nuevo_y)
        self.matriz[nuevo_y][nuevo_x] = jugador

        # MEJORA: Mensaje inmediato de movimiento
        print(f"🚶 {jugador.nombre} se movió de ({pos_anterior[0]},{pos_anterior[1]}) → ({nuevo_x},{nuevo_y})")

        # MEJORA: Mostrar tablero actualizado después del movimiento
        self._mostrar_tablero_compacto()

        # Registrar en historial (pila)
        accion = f"Turno {self.numero_turno}: {jugador.nombre} se movió {direccion} de ({pos_anterior[0]},{pos_anterior[1]}) a ({nuevo_x}, {nuevo_y})"
        self.pila_historial.append(accion)

        return True

    def atacar(self, atacante, objetivo):
        """Realiza un ataque entre dos jugadores"""
        if not objetivo.vivo:
            return False

        dano_causado = objetivo.recibir_dano(atacante.ataque)

        # MEJORA: Mensaje inmediato de ataque
        print(f"⚔️  {atacante.nombre} atacó a {objetivo.nombre} y causó {dano_causado} de daño!")

        # Registrar en historial (pila)
        accion = f"Turno {self.numero_turno}: {atacante.nombre} atacó a {objetivo.nombre} causando {dano_causado} de daño"

        if not objetivo.vivo:
            print(f"💀 {objetivo.nombre} ha sido eliminado!")
            accion += f" - {objetivo.nombre} ha sido eliminado!"
            # Remover del tablero
            self.matriz[objetivo.y][objetivo.x] = None
            # MEJORA: Mostrar tablero actualizado después de eliminación
            self._mostrar_tablero_compacto()
        else:
            print(f"❤️  {objetivo.nombre} tiene {objetivo.hp} HP restante")

        self.pila_historial.append(accion)
        return True

    def obtener_jugadores_vivos(self):
        """Retorna lista de jugadores que siguen vivos"""
        return [j for j in self.jugadores if j.vivo]

    def mostrar_arena(self):
        """Muestra el estado actual de la arena"""
        print(f"\n{'='*50}")
        print(f"ARENA {self.tamaño}x{self.tamaño} - TURNO {self.numero_turno}")
        print(f"{'='*50}")

        # Mostrar matriz
        for y in range(self.tamaño):
            fila = ""
            for x in range(self.tamaño):
                if self.matriz[y][x] is None:
                    fila += "[ . ]"
                else:
                    # Mostrar primera letra del nombre
                    fila += f"[{self.matriz[y][x].nombre[0].upper()}]"
            print(f"{y}: {fila}")

        # Mostrar estado de jugadores
        print(f"\nJugadores vivos:")
        for jugador in self.obtener_jugadores_vivos():
            print(f"  {jugador}")

    def _mostrar_tablero_compacto(self):
        """Muestra solo el tablero de forma compacta para actualizar posiciones"""
        print(f"\n🎲 Tablero actualizado:")
        for y in range(self.tamaño):
            fila = ""
            for x in range(self.tamaño):
                if self.matriz[y][x] is None:
                    fila += "[ . ]"
                else:
                    # Mostrar primera letra del nombre
                    fila += f"[{self.matriz[y][x].nombre[0].upper()}]"
            print(f"{y}: {fila}")

    def ejecutar_turno(self, jugador):
        """Ejecuta el turno de un jugador"""
        if not jugador.vivo:
            return

        print(f"\n--- Turno de {jugador.nombre} ---")
        print(f"🎯 Posición actual: ({jugador.x}, {jugador.y})")

        adyacentes = self._obtener_jugadores_adyacentes(jugador)

        print("Acciones disponibles:")
        print("1. Moverse")
        if adyacentes:
            print("2. Atacar")

        try:
            opcion = input("Selecciona acción (1 o 2): ").strip()

            if opcion == "1":
                # Movimiento
                print("Direcciones: arriba, abajo, izquierda, derecha")
                direccion = input("¿Hacia dónde moverte? ").strip().lower()

                if self.mover_jugador(jugador, direccion):
                    print(f"✅ Movimiento completado")
                    # Mostrar movimientos posibles restantes
                    self._mostrar_movimientos_posibles(jugador)
                else:
                    print("❌ Movimiento inválido (fuera de límites o celda ocupada)")
                    print("Puedes moverte hacia: arriba, abajo, izquierda, derecha")

            elif opcion == "2" and adyacentes:
                # Ataque
                print("Objetivos adyacentes:")
                for i, objetivo in enumerate(adyacentes):
                    print(f"{i+1}. {objetivo}")

                try:
                    seleccion = int(input("Selecciona objetivo: ")) - 1
                    if 0 <= seleccion < len(adyacentes):
                        objetivo = adyacentes[seleccion]
                        self.atacar(jugador, objetivo)
                        print(f"✅ Ataque completado")
                    else:
                        print("❌ Selección inválida")
                except ValueError:
                    print("❌ Entrada no válida")

            else:
                print("❌ Acción no válida")

        except KeyboardInterrupt:
            print("\n¡Juego interrumpido!")
            return False

        return True

    def _mostrar_movimientos_posibles(self, jugador):
        """Muestra las direcciones donde el jugador puede moverse"""
        movimientos = {
            'arriba': (0, -1),
            'abajo': (0, 1),
            'izquierda': (-1, 0),
            'derecha': (1, 0)
        }

        posibles = []
        for direccion, (dx, dy) in movimientos.items():
            nuevo_x = jugador.x + dx
            nuevo_y = jugador.y + dy

            if (self._es_posicion_valida(nuevo_x, nuevo_y) and
                    self.matriz[nuevo_y][nuevo_x] is None):
                posibles.append(f"{direccion} → ({nuevo_x},{nuevo_y})")

        if posibles:
            print(f"🧭 Próximos movimientos posibles: {', '.join(posibles)}")
        else:
            print("🚫 No hay movimientos disponibles")

    def iniciar_juego(self):
        """Bucle principal del juego"""
        print("🏟️  ¡BIENVENIDO A LA ARENA DE COMBATE! 🏟️")
        self.mostrar_arena()

        # Bucle principal hasta que quede un solo jugador
        while len(self.obtener_jugadores_vivos()) > 1:
            # Repoblar cola si está vacía
            if not self.cola_turnos:
                jugadores_vivos = self.obtener_jugadores_vivos()
                self.cola_turnos.extend(jugadores_vivos)

            if not self.cola_turnos:
                break

            # Obtener siguiente jugador de la cola (FIFO)
            jugador_actual = self.cola_turnos.popleft()

            # Solo ejecutar turno si el jugador sigue vivo
            if jugador_actual.vivo:
                self.numero_turno += 1
                self.mostrar_arena()

                if not self.ejecutar_turno(jugador_actual):
                    break  # Juego interrumpido

                # MEJORA: Pequeña pausa para mejor legibilidad
                print("\n" + "="*30)
                input("Presiona Enter para continuar al siguiente turno...")

        # Mostrar resultados finales
        self._mostrar_resultados_finales()

    def _mostrar_resultados_finales(self):
        """Muestra el ganador y el historial de acciones"""
        jugadores_vivos = self.obtener_jugadores_vivos()

        print(f"\n{'='*50}")
        print("🏆 ¡JUEGO TERMINADO! 🏆")
        print(f"{'='*50}")

        # Mostrar ganador
        if jugadores_vivos:
            ganador = jugadores_vivos[0]
            print(f"🥇 GANADOR: {ganador.nombre}")
            print(f"   HP restante: {ganador.hp}")
            print(f"   Posición final: ({ganador.x}, {ganador.y})")
        else:
            print("🤝 ¡EMPATE! No quedaron jugadores vivos.")

        print(f"\nEstadísticas del juego:")
        print(f"📊 Total de turnos: {self.numero_turno}")
        print(f"📊 Total de acciones: {len(self.pila_historial)}")

        # Mostrar historial de acciones (pila - LIFO)
        print(f"\n📜 HISTORIAL DE ACCIONES (del más reciente al más antiguo):")
        print("-" * 60)

        if self.pila_historial:
            # Mostrar pila en orden inverso (último en entrar, primero en salir)
            for i, accion in enumerate(reversed(self.pila_historial)):
                print(f"{i+1}. {accion}")
        else:
            print("No se registraron acciones.")

        # MEJORA: Resumen de movimientos por jugador
        print(f"\n📈 RESUMEN DE MOVIMIENTOS:")
        print("-" * 40)
        self._mostrar_resumen_movimientos()

    def _mostrar_resumen_movimientos(self):
        """Muestra un resumen de los movimientos de cada jugador"""
        movimientos_por_jugador = {}
        ataques_por_jugador = {}

        for accion in self.pila_historial:
            if "se movió" in accion:
                # Extraer nombre del jugador
                nombre = accion.split(" se movió")[0].split(": ")[1]
                movimientos_por_jugador[nombre] = movimientos_por_jugador.get(nombre, 0) + 1
            elif "atacó" in accion:
                # Extraer nombre del atacante
                nombre = accion.split(" atacó")[0].split(": ")[1]
                ataques_por_jugador[nombre] = ataques_por_jugador.get(nombre, 0) + 1

        for jugador in self.jugadores:
            nombre = jugador.nombre
            movimientos = movimientos_por_jugador.get(nombre, 0)
            ataques = ataques_por_jugador.get(nombre, 0)
            estado = "💀" if not jugador.vivo else "💚"
            print(f"{estado} {nombre}: {movimientos} movimientos, {ataques} ataques")


def crear_jugadores_ejemplo():
    """Crea jugadores de ejemplo para demostración"""
    return [
        Jugador("Guerrero", 100, 25, 5, 0, 0),
        Jugador("Mago", 70, 35, 2, 4, 0),
        Jugador("Arquero", 80, 30, 3, 2, 2),
        Jugador("Tanque", 120, 20, 8, 0, 4)
    ]

def main():
    """Función principal del programa"""
    print("🎮 CONFIGURACIÓN DE LA ARENA DE COMBATE 🎮")
    print("\n" + "="*60)
    print("EXPLICACIÓN DEL SISTEMA:")
    print("• Cola FIFO: Los jugadores se turnan en orden circular")
    print("• Pila (Historial): Las acciones se guardan para revisar después")
    print("• Arena N x N: Matriz donde cada celda puede tener un jugador o estar vacía")
    print("• Movimientos: arriba, abajo, izquierda, derecha (celdas adyacentes)")
    print("• Ataques: Solo a jugadores adyacentes (al lado)")
    print("="*60)

    # Crear arena
    arena = Arena(5)  # Arena 5x5

    # Crear y agregar jugadores
    jugadores = crear_jugadores_ejemplo()

    print(f"\nAgregando jugadores a la arena...")
    for jugador in jugadores:
        if arena.agregar_jugador(jugador):
            print(f"✓ {jugador.nombre} agregado en posición ({jugador.x}, {jugador.y})")
        else:
            print(f"✗ No se pudo agregar a {jugador.nombre}")

    print(f"\n ORDEN DE TURNOS:")
    for i, jugador in enumerate(arena.cola_turnos, 1):
        print(f"  {i}. {jugador.nombre}")

    # Verificar que hay suficientes jugadores
    if len(arena.obtener_jugadores_vivos()) >= 2:
        input("\nPresiona Enter para comenzar el combate...")
        arena.iniciar_juego()
    else:
        print("❌ Se necesitan al menos 2 jugadores para comenzar el combate.")

if __name__ == "__main__":
    main()

