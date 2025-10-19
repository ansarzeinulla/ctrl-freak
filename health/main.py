from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handles GET requests."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response_data = {"status": "ok"}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

def run_server(server_class=HTTPServer, handler_class=HealthCheckHandler, port=8080, host='0.0.0.0'):
    """Starts the HTTP server."""
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd server on {host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Stopping httpd server.")

if __name__ == '__main__':
    run_server(port=7999)
