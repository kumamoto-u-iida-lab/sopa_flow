import os
import re
from pathlib import Path

"""procedure example
read -sv test.v
synth -flatten -top TOP
abc -g AND -dff
write_blif test.blif
"""

class TopModuleExtractor:
    def __init__(self, verilogFileName:str):
        pattern = r'\bmodule\s+(\w+)'

        with open(verilogFileName, mode="r") as f:
            txt = f.read()

        moduleNames = re.findall(pattern, txt)

        if not moduleNames:
            raise ValueError(f"top module was not found in {verilogFileName}")

        self.__topName = moduleNames[0]

    @property
    def name(self)->str:
        return self.__topName

class YosysScript:
    """
    and, not, dffのみを使ったネットリストを
    Yosysで生成するためのスクリプトを生成する。
    """
    # スクリプトのひな形。{}になっている場所はバリエーションで、
    # 入る要素の名前がコメントで書かれている。
    TEXT_READ = 'read -sv {}' # verilog file name
    TEXT_SYNTH = 'synth -flatten -top {}' # top module name
    TEXT_DFF_MAP = 'dfflibmap -liberty {}' # 任意のディレクトリで動かす場合注意
    TEXT_ABC = 'abc -g AND'
    TEXT_WRITE_BLIF = 'write_blif {}' # output blif name

    def __init__(self, verilogFileName:str, cellsFilePath:Path,
                 outputBlifName:str):
        # region Guard
        if not isinstance(verilogFileName, str):
            raise TypeError(f"verilogFileName shall be str")

        if not os.path.isfile(verilogFileName):
            raise FileNotFoundError(f"{verilogFileName} does not exist")

        if not isinstance(outputBlifName, str):
            raise TypeError(f"outputBlifName shall be str")

        # endregion

        topModuleName = TopModuleExtractor(verilogFileName).name

        # Store Yosys Script to here
        self.__texts = []

        textRead = YosysScript.TEXT_READ.format(verilogFileName)
        textSynth = YosysScript.TEXT_SYNTH.format(topModuleName)
        textDffMap = YosysScript.TEXT_DFF_MAP.format(cellsFilePath)
        textAbc = YosysScript.TEXT_ABC
        textWriteBlif = YosysScript.TEXT_WRITE_BLIF.format(outputBlifName)

        self.__texts.append(textRead)
        self.__texts.append(textSynth)
        self.__texts.append(textDffMap)
        self.__texts.append(textAbc)
        self.__texts.append(textWriteBlif)

    def __str__(self)->str:
        retText = ""
        for t in self.__texts:
            retText += t
            retText += '\n'

        return retText
