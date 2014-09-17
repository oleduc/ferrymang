import argparse
import json
import sys
import hmac

from http.server import HTTPServer, BaseHTTPRequestHandler
from modules.RepositoryEvent.RepositoryEvent import RepositoryEvent

# from time import sleep
# from daemonize import Daemonize

config = {
    'port': 5454
}

parser = argparse.ArgumentParser(description='Github webhook event listener.')
parser.add_argument('--pubkpath', required=True, help='Path to the SSH public key.')
parser.add_argument('--prvkpath', required=True, help='Path to the SSH private key.')
parser.add_argument('--pkpasswd', required=True,
                    help='Keypair password')
parser.add_argument('--signature', required=True, help='Signature token as configured in your repository\'s settings.')
parser.add_argument('--giturl', help='Repository url used if no config file is cached.')
arguments = parser.parse_args()


class RequestHandler(BaseHTTPRequestHandler):
    signature = arguments.signature

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
                keypair = {"pubkpath": arguments.pubkpath, "prvkpath": arguments.prvkpath, "pkpasswd": arguments.pkpasswd}

                repository_event = RepositoryEvent('push', parsed_request['branch'],
                                                   parsed_request['data']['repository']['git_url'],
                                                   keypair,
                                                   git_init_url=arguments.giturl)
                self.respond(200)
            else:
                print('Unsupported event')
                self.respond(400)
        else:
            print('Got an invalid signature, abort')
            self.respond(401)

    def verifySignature(self, parsed_request):
        github_signature = self.headers.get('X-Hub-Signature')
        if len(self.signature) > 0:
            hmac_obj = hmac.new(str.encode(self.signature), parsed_request['raw'], 'sha1')
            secret_key = 'sha1=' + hmac_obj.hexdigest()

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


def main():
    print('======================= Ferrymang =======================')
    if len(sys.argv) > 1:
        print('Ferrymang is now listening on port ' + str(config['port']) + '...')
        httpd = HTTPServer(('127.0.0.1', config['port']), RequestHandler)
        httpd.serve_forever()
    else:
        print('Must specify Github token.')
        print('Ex: python ferrymang.py "nbuyev56uyyku89HGRG%?jyn9"')


main()

#daemon = Daemonize(app="Ferrymang", pid="/tmp/ferrymang.pid", action=main)
#daemon.start()