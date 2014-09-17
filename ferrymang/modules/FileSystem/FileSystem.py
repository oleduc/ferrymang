import os, shutil

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
    def exists(path):
        if FileSystem.fileExists(path):
            return True
        if FileSystem.dirExists(path):
            return True
        return False

    @staticmethod
    def createDirectory(path, rec=False):
        if FileSystem.dirExists(path):
            return True
        else:
            if rec:
                os.makedirs(path)
            else:
                os.mkdir(path)
            return FileSystem.dirExists(path)

    @staticmethod
    def delete(path):
        if os.path.isfile(path):
            os.remove(path)
        if os.path.isdir(path):
            shutil.rmtree(path)
        return not FileSystem.exists(path)

    @staticmethod
    def move(from_path, to_path):
        if from_path[-1:] == '*':
            from_path = from_path[0:len(from_path)-1]
            dir_list = os.listdir(from_path)
            for item in dir_list:
                shutil.move(FileSystem.join(from_path, item), FileSystem.join(to_path, item))
        else:
            shutil.move(from_path, to_path)

        return FileSystem.exists(to_path)

    @staticmethod
    def copy(fromPath, toPath):
        shutil.copy(fromPath, toPath)
        return FileSystem.exists(toPath)

    @staticmethod
    def resolve(path):
        return os.path.abspath(path)

    @staticmethod
    def readFile(path):
        if FileSystem.fileExists(path):
            file = open(path)
            content = file.read(50000000)
            file.close()
            return content
        print('File does not exists: '+path)
        return False