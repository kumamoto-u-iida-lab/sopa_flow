import os
import subprocess
import logging
from BitstreamGen.PreProcess.YosysScript import YosysScript

# verilogFile名とTOPモジュール名が一致していることを入力条件とする。
# ガードでチェックすると、任意の大きさのverilogファイルをパース・解析する必要があるため
# 
class BlifGenerator:
    YS_FILE_NAME = "PreTechMapSynth.ys"
    def __init__(self, verilogFile:str, cellsFile:str, outputDir:str):
        # region Guard
        if not isinstance(verilogFile, str):
            raise TypeError("verilogFile shall be str")
        
        if not os.path.isfile(verilogFile):
            raise FileNotFoundError(f"{verilogFile} is not found")
        
        if not isinstance(outputDir, str):
            raise TypeError("outputDir shall be str")
        
        if not os.path.isdir(outputDir):
            raise NotADirectoryError(f"{outputDir} is not a directory")

        # endregion

        # YosysScriptクラスへの入力を準備
        baseName = os.path.basename(verilogFile)
        filename = os.path.splitext(baseName)[0]
        blifName = filename + '.blif'
        self.__blifFile = os.path.join(outputDir, blifName)

        # YosysScriptを生成
        ys = YosysScript(verilogFile, cellsFile, self.__blifFile)

        # ファイルとして保存
        with open(BlifGenerator.YS_FILE_NAME, mode='w+', encoding='utf-8') as f:
            f.write(str(ys))

        # Yosysを起動してysを実行
        # subprocess
        rsltYosys = subprocess.run(['yosys', BlifGenerator.YS_FILE_NAME])
        if rsltYosys.returncode != 0:
            raise RuntimeError("Yosys error by any cause")

        self.Log()

    @property
    def blifFile(self)->str:
        return self.__blifFile
    
    @property
    def ysFile(self)->str:
        return BlifGenerator.YS_FILE_NAME
    
    def Log(self):
        logging.info(f"synthesized as {self.__blifFile}")