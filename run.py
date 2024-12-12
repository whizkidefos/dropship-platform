from app import create_app
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import webbrowser
import time
import os
from livereload import Server

app = create_app()

class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py') or event.src_path.endswith('.html') or event.src_path.endswith('.css') or event.src_path.endswith('.js'):
            print(f"Changes detected in {event.src_path}")

def watch_files():
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='app', recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    if app.debug:
        port = 5500
        # Start the livereload server
        server = Server(app.wsgi_app)
        # Watch the app directory for changes
        server.watch('app', ignore=lambda x: '__pycache__' in x)
        server.serve(
            host='127.0.0.1',
            port=port,
            debug=True,
            open_url=False
        )
    else:
        app.run(host='localhost', port=5500)