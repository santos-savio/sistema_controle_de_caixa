from app import create_app
import webbrowser
import time

if __name__ == '__main__':
    app = create_app()
    port = 5001
    
    # Abrir navegador automaticamente após um pequeno delay
    def open_browser():
        time.sleep(1.5)  # Esperar a aplicação iniciar
        webbrowser.open(f'http://127.0.0.1:{port}')
    
    # Iniciar thread para abrir o navegador
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(debug=True, host='127.0.0.1', port=port, use_reloader=False)
