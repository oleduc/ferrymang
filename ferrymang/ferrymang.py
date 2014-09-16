import os, argparse, urllib, json, sys, hmac

from http.server import HTTPServer, BaseHTTPRequestHandler
from subprocess import call
from pygit2 import clone_repository, Keypair

# from time import sleep
# from daemonize import Daemonize

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

parser = argparse.ArgumentParser(description='Github webhook event listener.')
parser.add_argument('--pubkpath', required=True, help='Path to the SSH public key.')
parser.add_argument('--prvkpath', required=True, help='Path to the SSH private key.')
parser.add_argument('--pkpasswd', required=True,
                    help='Keypair password')
parser.add_argument('--pkusername', required=True, help='Keypair username')
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
                repository_event = RepositoryEvent('push', parsed_request['branch'],
                                                   parsed_request['data']['repository']['git_url'])
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


class RepositoryEvent():
    gitInitUrl = arguments.giturl or ''

    def __init__(self, type_of_event, branch, url):
        self.type = type_of_event
        self.branch = branch
        self.url = url
        self.tmpDir = '/tmp/ferrymang'
        self.tmpRepoDir = FileSystem.join(self.tmpDir, 'repository')
        self.tmpCacheDir = FileSystem.join(self.tmpDir, 'cache')
        self.keypair = Keypair('ferrymang', arguments.pubkpath, arguments.prvkpath,'')

        FileSystem.createDirectory(self.tmpDir)

        self.config = self.loadConfig()

        #self.dispatch()

    def dispatch(self):
        if self.type == 'push':
            self.deploy()

    def clone(self, url):
        if FileSystem.createDirectory(self.tmpRepoDir):
            print('Cloning')
            repository = clone_repository(url, self.tmpRepoDir, credentials=self.keypair)
            print(repository)
            return True

        return False

    def deploy(self):
        self.clean()

        if FileSystem.createDirectory(self.tmpDir):
            "self.clone('')"
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
        # Run stop scripts

        # For each applications
        # Delete content of root
        return

    def loadConfig(self):
        config_obj = {}
        cached_config_path = FileSystem.join(self.tmpCacheDir, 'config.json')
        if FileSystem.fileExists(cached_config_path):
            print('File exists load config.')
            config_obj = self.parseConfig(cached_config_path)
        elif len(sys.argv) > 2:
            print('Get repository from command line.')
            if self.clone(RepositoryEvent.gitInitUrl):
                if FileSystem.createDirectory('/tmp/ferrymang/cache'):
                    FileSystem.move(FileSystem.join(self.tmpRepoDir, 'config.json'), cached_config_path)
                    config_obj = self.parseConfig(cached_config_path)
        return config_obj

    def parseConfig(self, path):
        return {}


class FileSystem():
    @staticmethod
    def join(path, path2):
        return os.path.join(path, path2)

    @staticmethod
    def dirExists(path):
        return os.path.isdir(path)

    @staticmethod
    def fileExists(path):
        return os.path.isfile(path)

    @staticmethod
    def createDirectory(path):
        if FileSystem.dirExists(path):
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