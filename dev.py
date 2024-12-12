import subprocess
import webbrowser
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, flask_process):
        self.flask_process = flask_process
        self.last_modified = time.time()
        
    def on_modified(self, event):
        # Avoid duplicate reloads
        if time.time() - self.last_modified < 1:
            return
            
        if event.src_path.endswith(('.py', '.html', '.css', '.js')):
            print(f"\nChanges detected in {event.src_path}")
            print("Restarting Flask server...")
            
            # Restart Flask process
            self.flask_process.terminate()
            self.flask_process = subprocess.Popen(
                ['python', 'run.py'],
                env=dict(os.environ, FLASK_DEBUG='1')
            )
            self.last_modified = time.time()

def run_dev_server():
    # Start Flask
    flask_process = subprocess.Popen(
        ['python', 'run.py'],
        env=dict(os.environ, FLASK_DEBUG='1')
    )
    
    # Setup file watcher
    event_handler = ChangeHandler(flask_process)
    observer = Observer()
    observer.schedule(event_handler, path='app', recursive=True)
    observer.start()
    
    print("Development server is running...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down development server...")
        observer.stop()
        flask_process.terminate()
    observer.join()

if __name__ == '__main__':
    run_dev_server()