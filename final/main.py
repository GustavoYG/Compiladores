# main.py
import sys
from cssx.server.editor import run_server

if __name__ == '__main__':
    # You can customize the port from the command line, e.g., python main.py 8080
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    run_server(port=port)