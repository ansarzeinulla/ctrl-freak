import http.server
import socketserver
import json
import logging
from pathlib import Path
from retrieve import retrieve_results_by_vacancy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PORT = 5001
TEMPLATES_DIR = Path(__file__).parent / "templates"

class MyHttpRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handles GET requests. Serves the index.html page."""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(TEMPLATES_DIR / 'index.html', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        """Handles POST requests to /retrieve."""
        if self.path == '/retrieve':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)

                if 'vacancy_id' not in data:
                    self._send_json_response({'error': 'vacancy_id is required'}, status_code=400)
                    return

                vacancy_id = int(data['vacancy_id'])
                results = retrieve_results_by_vacancy(vacancy_id)
                # The retrieve function now returns a list of dicts, which is perfect for a JSON response.
                # The results are already sorted by score.
                logging.info(f"Retrieved {len(results)} results for vacancy_id {vacancy_id}. Sending to client.")
                logging.debug(f"Data: {results}") # More detailed log for debugging
                self._send_json_response(results)

            except ValueError:
                self._send_json_response({'error': 'Invalid vacancy_id provided. It must be a number.'}, status_code=400)
            except Exception as e:
                logging.error(f"An unexpected error occurred in /retrieve: {e}")
                self._send_json_response({'error': 'An internal server error occurred.'}, status_code=500)
        else:
            self.send_error(404, "File Not Found")

    def _send_json_response(self, data, status_code=200):
        """Helper to send a JSON response."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

if __name__ == '__main__':
    # We need to change the directory so the server can find the templates folder
    # This is a simple way to handle it for this specific project structure.
    import os
    os.chdir(Path(__file__).parent)

    with socketserver.TCPServer(("", PORT), MyHttpRequestHandler) as httpd:
        logging.info(f"Serving at port {PORT}")
        logging.info(f"Open http://localhost:{PORT} in your browser.")
        httpd.serve_forever()