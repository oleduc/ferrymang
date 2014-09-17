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
            print('Downloading repository...')
            repository = clone_repository(url, self.tmpRepoDir, credentials=self.Keypair, checkout_branch=self.branch)
            print('Done.')
            return not repository.is_empty
        return False

    def deploy(self):
        self.clean()
        if not self.config['init']:
            self.clone(self.url)

        # Read current version's config
        self.config = self.parseConfig(FileSystem.join(self.tmpRepoDir, self.configFileName))

        # Copy current config to config cache
        if FileSystem.delete(self.tmpCacheDir) and FileSystem.createDirectory(self.tmpCacheDir):
            if FileSystem.copy(FileSystem.join(self.tmpRepoDir, self.configFileName), self.tmpCacheDir):
                print('Cached configuration file.')

        if self.config['actions']:
            for actions in self.config['actions']:
                if actions['type'] == 'move':
                    print('Executing move action')
                    to_path = FileSystem.join(self.config['root'], actions['to'])
                    to_path = FileSystem.resolve(to_path)
                    if actions['to'][-1:] == '/' and not FileSystem.dirExists(to_path):
                        FileSystem.createDirectory(to_path)

                    from_path = FileSystem.join(self.tmpRepoDir, actions['from'])
                    from_path = FileSystem.resolve(from_path)
                    print('MOVE', from_path, to_path)
                    FileSystem.move(from_path, to_path)
                    print('Done...')

        self.runScripts(self.config['start'])

        # Delete TMP folder
        if FileSystem.delete(self.tmpRepoDir):
            print('Successfully deleted temporary repository directory.')

        return True

    def clean(self):

        self.runScripts(self.config['stop'])
        self.deleteApplicationsRoots()

        FileSystem.delete(FileSystem.join(self.tmpCacheDir, self.configFileName))

        return

    def deleteApplicationsRoots(self):
        if self.config['applications']:
            for key in self.config['applications']:
                if FileSystem.exists(self.config['applications'][key]['path']):
                    print('Delete applications root', self.config['applications'][key]['path'])
                    FileSystem.delete(FileSystem.resolve(self.config['applications'][key]['path']))

    def runScripts(self, name):
        if self.config['applications']:
            for key in self.config['applications']:
                script_path = FileSystem.join(self.config['applications'][key]['path'], name)
                script_path = FileSystem.resolve(script_path)
                if FileSystem.fileExists(script_path):
                    print('Running script', script_path)
                    if subprocess.call(script_path, shell=True):
                        print('Ran script successfully', script_path)
                        FileSystem.delete(FileSystem.resolve(self.config['applications'][key]['path']))
                    else:
                        print('Ran script but unsuccessfully', script_path)
                else:
                    print('Failed to run a script; unavailable script', script_path)

    def loadCachedConfig(self):
        config_obj = {}
        cached_config_path = FileSystem.join(self.tmpCacheDir, self.configFileName)
        if FileSystem.fileExists(cached_config_path):
            print('File exists load config.')
            config_obj = self.parseConfig(cached_config_path)
            config_obj['init'] = False
        elif self.gitInitUrl:
            print('No cached configuration, download from github')
            if self.clone(self.gitInitUrl):
                config_obj = self.parseConfig(FileSystem.join(self.tmpRepoDir, self.configFileName))
            config_obj['init'] = True
        return config_obj

    def parseConfig(self, path):
        raw_content = FileSystem.readFile(path)
        parsed_content = json.loads(raw_content)
        results = self.replacePathsVariables(parsed_content)
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(results)
        return results

    def replacePathsVariables(self, config):
        for key in config['applications']:
            application_config = config['applications'][key]
            config['applications'][key]['path'] = application_config['path'].replace('{branch}', self.branch)
        for action in config['actions']:
            action['to'] = action['to'].replace('{branch}', self.branch)

        return config