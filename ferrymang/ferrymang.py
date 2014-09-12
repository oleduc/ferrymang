import os, urllib, json, sys, hmac

from http.server import HTTPServer, BaseHTTPRequestHandler
from subprocess import call

#from time import sleep
#from daemonize import Daemonize

config = {
    'port': 5454,
    'branches': [
        {
            'branch': 'master',
            'path': '/home/api'
        },
        {
            'branch': 'qa',
            'path': '/home/api-qa'
        }
    ]
}


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
        self.config = {}
        self.workingDir = '/tmp/ferrymang'
        self.dispatch()

    def dispatch(self):
        if self.type == 'push':
            self.deploy()

    def clone(self):

        return

    def deploy(self):
        self.clean()

        if FileSystem.createDirectory(self.workingDir):
            self.clone()
            # Read current version's config
            # Do actions
            # Run start script

            # Delete config cache
            # Copy current config to config cache
            # Delete TMP folder

            # Done
        else:
            return False

        return True

    def clean(self):
        # If config cache exists
            # Load old config

            # Run stop scripts

            # For each applications
                # Delete content of root

        # Else
            # Create folders

        # Done
        return

    def parseConfig(self, path):
        # Read
        return


class FileSystem():

    @staticmethod
    def createDirectory(path):
        if os.path.isdir(path):
            return True
        else:
            return os.mkdir(path)

    @staticmethod
    def move(fromPath, toPath):
        return call('mv', fromPath, toPath)


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