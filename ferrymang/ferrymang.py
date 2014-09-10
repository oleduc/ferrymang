import os, urllib

from http.server import HTTPServer, BaseHTTPRequestHandler

#from time import sleep
#from daemonize import Daemonize


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("Got a GET request")
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes("Your soup is ready my friend :D", 'UTF-8'))

    def do_POST(self):
        length = int(self.headers.get('content-length'))
        body = self.rfile.read(length)
        post_data = urllib.parse.parse_qs(body)
        print(post_data)
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()


class Repository():
    def __init__(self):
        return

    def clone(self):
        return

    def deploy(self):
        return


def main():
    httpd = HTTPServer(('127.0.0.1', 5454), RequestHandler)
    httpd.serve_forever()

main()

#daemon = Daemonize(app="Ferrymang", pid="/tmp/ferrymang.pid", action=main)
#daemon.start()