from http.server import SimpleHTTPRequestHandler, HTTPServer

address = ('', 8000)
httpd = HTTPServer(address, SimpleHTTPRequestHandler)
print("Serving on port 8000...")
httpd.serve_forever()
