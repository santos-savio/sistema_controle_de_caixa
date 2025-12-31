from app import create_app
import argparse
import threading
import time
import webbrowser

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5001)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()

    app = create_app()

    if not args.no_browser:
        def open_browser():
            time.sleep(1.5)
            webbrowser.open(f'http://{args.host}:{args.port}')
        threading.Thread(target=open_browser, daemon=True).start()

    app.run(
        debug=args.debug,
        host=args.host,
        port=args.port,
        use_reloader=False
    )
