from typing import List

import os

class TargetFile:
    def __init__(self, inputPath:str, acceptableExtentions:List[str]=['.v']):
        dummy, extention = os.path.splitext(inputPath)
        if not extention in acceptableExtentions:
            raise ValueError(f"The file extention {extention} is not acceptable.")

        self.__name = inputPath

    @property
    def name(self)->str:
        return self.__name

class TargetFiles:
    def __init__(self, inputPath:str, acceptableExtentions:List[str]=['.v']):
        # init
        self.__targets:List[TargetFile] = []

        if os.path.isfile(inputPath):
            self.__targets = [TargetFile(inputPath, acceptableExtentions)]

        elif os.path.isdir(inputPath):
            for path, _, files in os.walk(inputPath):
                for file in sorted(files):
                    # ファイルのパス
                    filepath = os.path.join(path, file)
                    try:
                        self.__targets.append(TargetFile(filepath, acceptableExtentions))
                    except ValueError:
                        print(f"{filepath} is not acceptable. skipped it")
                        # TargetFileの入力規則違反ならパス(ターゲットファイルに追加しない)
                    except:
                        raise RuntimeError

        else:
            raise FileNotFoundError(f"No such file of Directory: {inputPath}")

        if not self.__targets:
            raise FileNotFoundError(f"No any files in the specified Directory: {inputPath}")

        self.__inputPath = inputPath

    @property
    def targets(self)->List[str]:
        retTargets:List[str] = [e.name for e in self.__targets]
        return retTargets

    @property
    def absTargets(self)->List[str]:
        retTargets:List[str] = [os.path.abspath(e.name) for e in self.__targets]
        return retTargets

    @property
    def resultDirs(self)->List[str]:
        currentPath = os.getcwd()
        retDirs = []
        for targetFile in self.__targets:
            relPath = os.path.relpath(targetFile.name, currentPath)
            dirName, dummy = os.path.splitext(relPath)
            retDirs.append(dirName)

        return retDirs

    @property
    def logDir(self)->str:
        currentPath = os.getcwd()
        relPath = os.path.relpath(self.__inputPath, currentPath)

        # 拡張子があれば排除
        dirName, dummy = os.path.splitext(relPath)
        return dirName
