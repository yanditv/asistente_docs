#!/usr/bin/env python3
"""
Asistente de Documentos - Inicio Automático
Inicia tanto la API como la interfaz web de manera secuencial en primer plano
"""

import subprocess
import time
import webbrowser
import signal
import sys
from pathlib import Path

def signal_handler(sig, frame):
    """Manejador para Ctrl+C"""
    print("\nDeteniendo servicios...")
    sys.exit(0)

def start_api_server_foreground():
    """Iniciar el servidor API en primer plano"""
    print("="*60)
    print("INICIANDO SERVIDOR API")
    print("="*60)
    print("Servidor API iniciándose en http://localhost:8000")
    print("Documentación disponible en http://localhost:8000/docs")
    print()
    print("NOTA: Este proceso ejecutará en primer plano.")
    print("Para detener, presiona Ctrl+C")
    print("="*60)
    print()

    try:
        # Cambiar al directorio raíz del proyecto
        project_root = Path(__file__).parent.parent

        # Ejecutar el servidor API en primer plano
        result = subprocess.run([
            sys.executable, "main.py"
        ], cwd=project_root)

        return result.returncode == 0

    except KeyboardInterrupt:
        print("\nServidor API detenido por el usuario")
        return True
    except Exception as e:
        print(f"Error iniciando API: {e}")
        return False

def start_web_server_foreground():
    """Iniciar el servidor web en primer plano"""
    print("="*60)
    print("INICIANDO SERVIDOR WEB")
    print("="*60)
    print("Servidor web iniciándose en http://localhost:3000")
    print("Interfaz web en http://localhost:3000/web_client.html")
    print()
    print("NOTA: Este proceso ejecutará en primer plano.")
    print("Para detener, presiona Ctrl+C")
    print("="*60)
    print()

    # Abrir navegador automáticamente
    try:
        time.sleep(2)  # Dar tiempo para que se inicie
        webbrowser.open("http://localhost:3000/web_client.html")
        print("Navegador abierto automáticamente")
        print()
    except Exception as e:
        print(f"No se pudo abrir el navegador: {e}")
        print("Abre manualmente: http://localhost:3000/web_client.html")
        print()

    try:
        # Cambiar al directorio frontend
        frontend_dir = Path(__file__).parent.parent / "frontend"

        # Ejecutar el servidor web en primer plano
        result = subprocess.run([
            sys.executable, "web_server.py"
        ], cwd=frontend_dir)

        return result.returncode == 0

    except KeyboardInterrupt:
        print("\nServidor web detenido por el usuario")
        return True
    except Exception as e:
        print(f"Error iniciando servidor web: {e}")
        return False

def show_menu():
    """Mostrar menú de opciones"""
    print("="*60)
    print("ASISTENTE DE DOCUMENTOS - INICIO SECUENCIAL")
    print("="*60)
    print("Los servicios se ejecutarán secuencialmente en primer plano")
    print("Cada servicio será visible y controlable directamente")
    print()
    print("SERVICIOS DISPONIBLES:")
    print("1. Servidor API (http://localhost:8000)")
    print("2. Servidor Web (http://localhost:3000)")
    print()
    print("OPCIONES:")
    print("1) Iniciar solo API")
    print("2) Iniciar solo Web Server")
    print("3) Iniciar API, luego Web Server")
    print("4) Salir")
    print("="*60)

def main():
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)

    show_menu()

    while True:
        try:
            choice = input("Selecciona una opción (1-4): ").strip()

            if choice == "1":
                print("\nIniciando solo el servidor API...")
                start_api_server_foreground()
                break

            elif choice == "2":
                print("\nIniciando solo el servidor web...")
                print("ADVERTENCIA: El servidor web necesita que la API esté ejecutándose")
                print("Asegúrate de tener la API corriendo en otro terminal")
                input("Presiona Enter para continuar...")
                start_web_server_foreground()
                break

            elif choice == "3":
                print("\nIniciando secuencialmente...")
                print("PASO 1: Servidor API")
                print("Cuando quieras pasar al servidor web, presiona Ctrl+C")
                print()

                # Iniciar API
                api_success = start_api_server_foreground()

                if api_success:
                    print("\nPASO 2: Servidor Web")
                    print("El servidor API debe seguir ejecutándose en segundo plano")
                    print("o en otra terminal para que funcione correctamente")
                    input("Presiona Enter para continuar al servidor web...")
                    start_web_server_foreground()

                break

            elif choice == "4":
                print("Saliendo...")
                break

            else:
                print("Opción inválida. Por favor selecciona 1-4.")

        except KeyboardInterrupt:
            print("\nSaliendo...")
            break
        except EOFError:
            print("\nSaliendo...")
            break

if __name__ == "__main__":
    main()