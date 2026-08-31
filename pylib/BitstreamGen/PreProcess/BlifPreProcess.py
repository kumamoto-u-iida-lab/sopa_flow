import os
from typing import List

from blifparser import blifparser

from BitstreamGen.PreProcess.BlifBufferInserter import BlifBufferInserter
from BitstreamGen.PreProcess.BlifBufferModifier import BlifBufferModifier
from BitstreamGen.PreProcess.BlifBufferRemover import BlifBufferRemover

class BlifPreProcess:
    def __init__(self, inputFilePath:str):
        # Guard
        filepath = os.path.abspath(inputFilePath)
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"No such file or directory: {filepath}")
        
        # get the file path and pass it to the parser
        parser = blifparser.BlifParser(filepath)

        # get the object that contains the parsed data
        # from the parser
        self.__blif = parser.blif

        # pre-processed flag
        self.__inserted = False
        self.__removed = False
        self.__modified = False

        self.__outputFiles:List[str] = []
        self.__latestFile = filepath # 一度も前処理されなかった場合、入力ファイルのパスが返る。

    def ToFile(self, outputFilePath:str)->None:
        strBlif = str(self.__blif).replace("\n\n", "\n")
        with open(outputFilePath, mode='w', encoding='utf-8') as f:
            f.write(strBlif)

        self.__outputFiles.append(outputFilePath)
        self.__latestFile = outputFilePath

    # バッファの考慮により、テクノロジマッピングが本来より小さい範囲で行われることを防ぐために
    # バッファを削除する。
    def RemoveBuffer(self)->None:
        if self.__removed:
            print("[Warn]: Buffer removement has been done. Skiped it.")
            return
        
        br = BlifBufferRemover(self.__blif)
        self.__blif = br.blif
        self.__removed = True

    # dffや下位モジュールに接続する回路がPAEセル内にマッピングされることを防ぐために
    # バッファを挿入する。
    def InsertBuffer(self)->None:
        if self.__inserted:
            print("[Warn]: Buffer insertion has been done. Skiped it.")
            return
        
        bi = BlifBufferInserter(self.__blif)
        self.__blif = bi.blif
        self.__inserted = True

    # バッファのみで実現できる論理がある場合、PAEセル外に有効なバッファが形成されてしまう。
    # これを防ぐためにバッファをandゲートやnotゲートに変換する。
    def ModifyBuffer(self)->None:
        if self.__modified:
            print("[Warn]: Buffer modification has been done. Skiped it.")
            return
        
        bm = BlifBufferModifier(self.__blif)
        self.__blif = bm.blif
        self.__modified = True

    @property
    def outputFiles(self)->List[str]:
        # 重複を削除
        outFiles = sorted(set(self.__outputFiles), key=self.__outputFiles.index)
        return outFiles

    @property
    def latestFile(self)->str:
        return self.__latestFile
