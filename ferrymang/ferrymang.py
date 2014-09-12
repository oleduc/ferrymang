import os, urllib, json, sys, hmac

from http.server import HTTPServer, BaseHTTPRequestHandler

#from time import sleep
#from daemonize import Daemonize


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes("Hola, I'm your friend the ferry mang! :D", 'UTF-8'))

    def do_POST(self):
        parsed_request = self.parse()
        if self.verifySignature(parsed_request):
            print('Got a valid signature, proceed')
            event_type = self.headers.get('X-Github-Event')

            if event_type == 'push':
                print('Got push event, instantiate repository event')
                repository_event = RepositoryEvent('push', parsed_request['branch'], parsed_request['data']['repository']['git_url'])
                self.respond(200)
            else:
                print('Unsupported event')
                self.respond(400)
        else:
            print('Got an invalid signature, abort')
            self.respond(401)

    def verifySignature(self, parsed_request):
        github_signature = self.headers.get('X-Hub-Signature')
        if len(github_signature) > 0:

            hmac_obj = hmac.new(str.encode(sys.argv[1]), parsed_request['raw'], 'sha1')
            secret_key = 'sha1='+hmac_obj.hexdigest()

            return secret_key == github_signature
        else:
            print('No signature')
            return False

    def parse(self):
        length = int(self.headers.get('content-length'))
        body = self.rfile.read(length)
        data = json.loads(body.decode('utf-8'))

        reference = data['ref'].split('/')

        return {
            'branch': reference[2],
            'data': data,
            'raw': body
        }

    def respond(self, code):
        self.send_response(code)
        self.send_header('content-type', 'text/html')
        self.end_headers()


class RepositoryEvent():
    def __init__(self, type_of_event, branch, url):
        self.type = type_of_event
        self.branch = branch
        self.url = url

    def clone(self):
        return

    def deploy(self):
        return


def main():
    print('======================= Ferrymang =======================')
    if len(sys.argv) > 1:
        print('Ferrymang is now listening on port 5454...')
        httpd = HTTPServer(('127.0.0.1', 5454), RequestHandler)
        httpd.serve_forever()
    else:
        print('Must specify Github token.')
        print('Ex: python ferrymang.py "nbuyev56uyyku89HGRG%?jyn9"')


main()

#daemon = Daemonize(app="Ferrymang", pid="/tmp/ferrymang.pid", action=main)
#daemon.start()