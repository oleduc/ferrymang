import json
import pprint
import subprocess
from modules.FileSystem.FileSystem import FileSystem
from pygit2 import clone_repository, Keypair

class RepositoryEvent():
    configFileName = 'ferrymang.json'

    def __init__(self, type_of_event, branch, url, keypair, git_init_url=None):
        self.type = type_of_event
        self.branch = branch
        self.url = url
        self.tmpDir = '/tmp/ferrymang'
        self.tmpRepoDir = FileSystem.join(self.tmpDir, 'repository')
        self.tmpCacheDir = FileSystem.join(self.tmpDir, 'cache')
        self.gitInitUrl = git_init_url or ''
        self.Keypair = Keypair('git', keypair['pubkpath'], keypair['prvkpath'], keypair['pkpasswd'])

        FileSystem.createDirectory(self.tmpDir)

        self.config = self.loadCachedConfig()

        self.dispatch()

    def dispatch(self):
        if self.type == 'push':
            self.deploy()

    def clone(self, url):
        FileSystem.delete(self.tmpRepoDir)
        if FileSystem.createDirectory(self.tmpRepoDir):
            repository = clone_repository(url, self.tmpRepoDir, credentials=self.Keypair, checkout_branch=self.branch)
            return not repository.is_empty
        return False

    def deploy(self):
        self.clean()

        # Read current version's config
        self.config = self.parseConfig(FileSystem.join(self.tmpRepoDir, self.configFileName))
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.config)
        # Do actions

        if self.config['actions']:
            print(type(self.config['actions']))
            for actions in self.config['actions']:
                if actions['type'] == 'move':
                    print('Executing move action')
                    to_path = FileSystem.join(self.config['root'], actions['to'])
                    # TODO: Move to own method
                    to_path = to_path.replace('{branch}', self.branch)
                    to_path = FileSystem.resolve(to_path)
                    if actions['to'][-1:] == '/' and not FileSystem.dirExists(to_path):
                        FileSystem.createDirectory(to_path)

                    from_path = FileSystem.join(self.tmpRepoDir, actions['from'])
                    from_path = FileSystem.resolve(from_path)
                    print('MOVE', from_path, to_path)
                    FileSystem.move(from_path, to_path)
                    print('Done...')

        # Run start scripts

        # Copy current config to config cache
        # Delete TMP folder

        # Done

        return True

    def clean(self):

        if self.config['applications']:
            for key in self.config['applications']:
                print(self.config['applications'][key]['path'])
                stop_script_path = FileSystem.join(self.config['applications'][key]['path'], self.config['stop'])
                stop_script_path = FileSystem.resolve(stop_script_path)
                if FileSystem.fileExists(stop_script_path):
                    if subprocess.call(stop_script_path, shell=True):
                        FileSystem.delete(FileSystem.resolve(self.config['applications'][key]['path']))

        FileSystem.delete(self.tmpCacheDir)

        return

    def runScripts(self, name):
        if self.config['applications']:
            for key in self.config['applications']:
                print(self.config['applications'][key]['path'])
                script_path = FileSystem.join(self.config['applications'][key]['path'], name)
                script_path = FileSystem.resolve(script_path)
                if FileSystem.fileExists(script_path):
                    if subprocess.call(script_path, shell=True):
                        print('Ran script successfully')
                        FileSystem.delete(FileSystem.resolve(self.config['applications'][key]['path']))
                    else:
                        print('Ran script but unsuccessfully')

    def loadCachedConfig(self):
        config_obj = {}
        cached_config_path = FileSystem.join(self.tmpCacheDir, self.configFileName)
        if FileSystem.fileExists(cached_config_path):
            print('File exists load config.')
            config_obj = self.parseConfig(cached_config_path)
        elif self.gitInitUrl:
            print('Get repository from command line.')
            if self.clone(self.gitInitUrl):
                config_obj = self.parseConfig(FileSystem.join(self.tmpRepoDir, self.configFileName))
        return config_obj

    def parseConfig(self, path):
        raw_content = FileSystem.readFile(path)
        parsed_content = json.loads(raw_content)
        return parsed_content