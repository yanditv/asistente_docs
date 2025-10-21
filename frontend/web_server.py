import http.server
import socketserver
import webbrowser
import threading
import time
from pathlib import Path

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)

def start_web_server():
    """Iniciar servidor web simple para servir el HTML"""
    PORT = 3000
    
    try:
        with socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler) as httpd:
            print(f"🌐 Servidor web iniciado en http://localhost:{PORT}")
            print(f"📱 Interfaz web disponible en: http://localhost:{PORT}/web_client.html")
            print("🔗 API ejecutándose en: http://localhost:8000")
            print("\n🎯 Para usar la interfaz web:")
            print("   1. Ve a http://localhost:3000/web_client.html")
            print("   2. O espera a que se abra automáticamente...")
            
            # Abrir navegador automáticamente después de 2 segundos
            def open_browser():
                time.sleep(2)
                webbrowser.open(f"http://localhost:{PORT}/web_client.html")
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n🛑 Servidor web detenido")
                
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"⚠️ Puerto {PORT} ya está en uso. Intenta con otro puerto.")
            print(f"💡 O abre directamente: http://localhost:{PORT}/web_client.html")
        else:
            print(f"❌ Error iniciando servidor web: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando servidor web para la interfaz...")
    start_web_server()
