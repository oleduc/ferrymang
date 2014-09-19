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
            print('Downloading repository...', url)
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

        # Create root directory if configured
        if self.config['root']:
            if FileSystem.createDirectory(self.config['root']):
                print('Created root directory as configured.')

        if self.config['actions']:
            for actions in self.config['actions']:
                if actions['type'] == 'move':
                    to_path = FileSystem.join(self.config['root'], actions['to'])
                    to_path = FileSystem.resolve(to_path)
                    if actions['to'][-1:] == '/' and not FileSystem.dirExists(to_path):
                        FileSystem.createDirectory(to_path)

                    from_path = FileSystem.join(self.tmpRepoDir, actions['from'])
                    from_path = FileSystem.resolve(from_path)
                    print('MOVE', from_path, to_path)
                    FileSystem.move(from_path, to_path)
                    print('Done...')

        self.runScripts('start')

        # Delete TMP folder
        if FileSystem.delete(self.tmpRepoDir):
            print('Successfully deleted temporary repository directory.')

        return True

    def clean(self):

        self.runScripts('stop')
        self.deleteApplicationsRoots()

        FileSystem.delete(FileSystem.join(self.tmpCacheDir, self.configFileName))

        return

    def deleteApplicationsRoots(self):
        if self.config['applications']:
            for key in self.config['applications']:
                app_path = self.rootAndResolve(self.config['applications'][key]['path'])
                if FileSystem.exists(app_path) and FileSystem.delete(app_path):
                    print('Deleted applications root', app_path)

    def runScripts(self, script_name):
        if self.config['applications']:
            for key in self.config['applications']:
                application_path = self.rootAndResolve(self.config['applications'][key]['path'])
                script = self.config['applications'][key][script_name]
                if script.get('path') is not None:
                    script_path = FileSystem.join(self.config['applications'][key]['path'], script['path'])
                    script_path = self.rootAndResolve(script_path)

                    if FileSystem.fileExists(script_path):
                        print('Running script', script_path)
                        if subprocess.call('cd '+application_path+' && '+script_path+' '+script['parameters'], shell=True):
                            print('Ran script successfully', script_path)
                        else:
                            print('Ran script but unsuccessfully', script_path)
                    else:
                        print('Failed to run a script; unavailable script', script_path)
                elif script.get('commands') is not None:
                    for command in script['commands']:
                        command = command.replace('{path}', application_path)
                        print('Running command "'+command+'"')
                        if subprocess.call('cd '+application_path+' && '+command, shell=True):
                            print('Ran command successfully', command)
                        else:
                            print('Ran command but unsuccessfully', command)

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
        results = self.replaceConfigVariables(parsed_content)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(results)
        return results

    def rootAndResolve(self, path):
        path = FileSystem.join(self.config['root'], path)
        return FileSystem.resolve(path)

    def replaceConfigVariables(self, config):
        # Todo: Leverage generators

        for top_key in config:
            key_type = type(config[top_key])
            print('Iterating', top_key)
            config[top_key] = self.configVarIterator(config[top_key])

        return config

    def configVarIterator(self, var):
        key_type = type(var)
        if key_type == str:
            print('BREFORE REPLACE', var)
            var = var.replace('{branch}', self.branch)
            print('AFTER REPLACE', var)
            return var
        if key_type == dict:
            for dic_key in var:
                var[dic_key] = self.configVarIterator(var[dic_key])
        if key_type == list:
            for key, item in enumerate(var):
                var[key] = self.configVarIterator(item)
        return var