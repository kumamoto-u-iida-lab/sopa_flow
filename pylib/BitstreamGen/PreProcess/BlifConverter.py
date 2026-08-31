import xml.etree.ElementTree as ET
import os
import re
import logging
from xml.dom import minidom
from abc import ABCMeta, abstractmethod
from typing import Dict

from blifparser import blifparser

#xmlフォーマット用
def prettify(elem):
    roughString = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(roughString)
    pretty = re.sub(r"[\t ]+\n", "", reparsed.toprettyxml(indent="\t"))
    pretty = pretty.replace(">\n\n\t<",">\n\t<")
    return pretty

# NodeIDを持っているクラス。
# valueにアクセスするとカウントアップするので、
# 呼び出し側で気を付ける必要がある。
class NodeID:
    def __init__(self):
        self.__nodeID = 1

    @property
    def value(self)->int:
        retID = self.__nodeID
        self.__nodeID += 1
        return retID

class IBool2XML(metaclass=ABCMeta):
    @abstractmethod
    def Convert(self, node:blifparser.keywords.generic.Names,
                blif:blifparser.keywords.generic.Blif)->ET.Element:
        pass

class BUF2XML(IBool2XML):
    def Convert(self, node:blifparser.keywords.generic.Names,
                blif:blifparser.keywords.generic.Blif)->ET.Element:
        e_node = ET.Element("buffer")

        # input
        e_input = ET.Element("input")
        e_input.text = node.inputs[0]
        e_node.append(e_input)

        # output
        e_output = ET.Element("output")
        e_output.text = node.output
        e_node.append(e_output)

        return e_node

class NOT2XML(IBool2XML):
    def __init__(self, nodeServer:NodeID):
        if not isinstance(nodeServer, NodeID):
            raise TypeError("nodeServer shall be NodeID type")

        self.__nodeServer = nodeServer

    def Convert(self, node:blifparser.keywords.generic.Names,
                blif:blifparser.keywords.generic.Blif)->ET.Element:
        e_node = ET.Element("node")

        # input
        e_inputList = ET.Element("input_list")
        for inputSignal in node.inputs:
            e_input = ET.Element("input")
            e_input.text = inputSignal
            e_inputList.append(e_input)
        e_node.append(e_inputList)

        # output
        e_output = ET.Element("output")
        e_output.text = node.output
        e_node.append(e_output)

        # id
        e_ID = ET.Element("id")
        e_ID.text = str(self.__nodeServer.value)
        e_node.append(e_ID)

        # type(FIX)
        e_type = ET.Element("type")
        e_type.text = "INV"
        e_node.append(e_type)

        # fanin(FIX)
        e_fanin = ET.Element("fanin_num")
        e_fanin.text = '1'
        e_node.append(e_fanin)

        # fanout
        e_fanout = ET.Element("fanout_num")
        strBlif = str(blif)
        listBlif = re.split('[\n ]', strBlif) # 改行とスペースで区切る
        nFanout = str(listBlif.count(node.output) - 1) # 1つは自分
        e_fanout.text = nFanout
        e_node.append(e_fanout)

        return e_node

class AND2XML(IBool2XML):
    def __init__(self, nodeServer:NodeID):
        if not isinstance(nodeServer, NodeID):
            raise TypeError("nodeServer shall be NodeID type")

        self.__nodeServer = nodeServer

    def Convert(self, node:blifparser.keywords.generic.Names,
                blif:blifparser.keywords.generic.Blif)->ET.Element:
        e_node = ET.Element("node")

        # input
        e_inputList = ET.Element("input_list")
        for inputSignal in node.inputs:
            e_input = ET.Element("input")
            e_input.text = inputSignal
            e_inputList.append(e_input)
        e_node.append(e_inputList)

        # output
        e_output = ET.Element("output")
        e_output.text = node.output
        e_node.append(e_output)

        # id
        e_ID = ET.Element("id")
        e_ID.text = str(self.__nodeServer.value)
        e_node.append(e_ID)

        # type(FIX)
        e_type = ET.Element("type")
        e_type.text = "AND"
        e_node.append(e_type)

        # fanin(FIX)
        e_fanin = ET.Element("fanin_num")
        e_fanin.text = '2'
        e_node.append(e_fanin)

        # fanout
        e_fanout = ET.Element("fanout_num")
        strBlif = str(blif)
        listBlif = re.split('[\n ]', strBlif) # 改行とスペースで区切る
        nFanout = str(listBlif.count(node.output) - 1) # 1つは自分
        e_fanout.text = nFanout
        e_node.append(e_fanout)

        return e_node

class Latch2XML:
    def Convert(self, node:blifparser.keywords.generic.Latch)\
        ->ET.Element:
        e_node = ET.Element("latch")

        e_input = ET.Element("input")
        e_input.text = node.input
        e_node.append(e_input)

        e_output = ET.Element("output")
        e_output.text = node.output
        e_node.append(e_output)

        if node.type is not None:
            e_type = ET.Element("type")
            e_type.text = node.type
            e_node.append(e_type)

        if node.control is not None:
            e_clock = ET.Element("clock")
            e_clock.text = node.control
            e_node.append(e_clock)

        if node.initval is not None:
            e_init = ET.Element("initial_state")
            e_init.text = node.initval
            e_node.append(e_init)

        return e_node

class SubCircuit2XML:
    def Convert(self, node:blifparser.keywords.subfiles.Subckt)\
        ->ET.Element:
        e_node = ET.Element("subckt")

        e_modelname = ET.Element("name")
        e_modelname.text = node.modelname
        e_node.append(e_modelname)

        e_paramList = ET.Element("ioput_list")
        for param in node.params:
            paramSplit = param.split("=")
            if len(paramSplit) != 2:
                raise ValueError(\
                    f"Subckt {node.modelname}\'s params is wrong something. {node.params}"\
                )

            e_param = ET.Element("ioput", {"subckt_ioput":paramSplit[0]})
            e_param.text = paramSplit[1]

            e_paramList.append(e_param)
        e_node.append(e_paramList)

        return e_node

class BlifConverter:
    def __init__(self, inputFilePath:str):
        # region Guard
        filepath = os.path.abspath(inputFilePath)
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"No such file or directory: {filepath}")
        
        # endregion

        # region Init
        parser = blifparser.BlifParser(filepath)
        blif = parser.blif

        nodeID = NodeID()
        convHash:Dict[str, IBool2XML] = {} # 真理値表で変換クラスのインスタンスを引く辞書
        convHash.setdefault(str([['1', '1']]), BUF2XML())
        convHash.setdefault(str([['0', '1']]), NOT2XML(nodeID))
        convHash.setdefault(str([['1', '1', '1']]), AND2XML(nodeID))

        self.__nNodes = 0 # nodeとみなすべきでない記述があるので、数える
        self.__nLatches = len(blif.latches)
        self.__nSubckts = len(blif.subcircuits)

        # endregion

        e_subjectGraph = self.__MakeTreeHeader(blif)

        for boolFunc in blif.booleanfunctions: # names要素
            if not boolFunc.inputs: # $trueなどはinputsが空でパースされる。
                continue
            
            # 真理値表によって使う変換器が変わる
            converter = convHash[str(boolFunc.truthtable)]
            e_node = converter.Convert(boolFunc, blif)

            e_subjectGraph.append(e_node)
            self.__nNodes += 1

        converter = Latch2XML()
        for latch in blif.latches:
            e_node = converter.Convert(latch)
            e_subjectGraph.append(e_node)

        converter = SubCircuit2XML()
        for subckt in blif.subcircuits:
            e_node = converter.Convert(subckt)
            e_subjectGraph.append(e_node)

        root = ET.Element("file")
        root.append(e_subjectGraph)

        self.__root = root
        self.Log()

    def ToXML(self, filename:str):
        with open(filename, "w", encoding='utf-8') as f:
            f.write(prettify(self.__root))

    @staticmethod
    def __MakeTreeHeader(blif:blifparser.keywords.generic.Blif)->ET.Element:
        e_subjectGraph = ET.Element("subjectgraph")

        e_modelName = ET.Element("name")
        e_modelName.text = blif.model.name
        e_subjectGraph.append(e_modelName)

        e_inputList = ET.Element("input_list")
        for inputSignal in blif.inputs.inputs:
            e_input = ET.Element("input")
            e_input.text = inputSignal
            e_inputList.append(e_input)
        e_subjectGraph.append(e_inputList)

        e_outputList = ET.Element("output_list")
        for outputSignal in blif.outputs.outputs:
            e_output = ET.Element("output")
            e_output.text = outputSignal
            e_outputList.append(e_output)
        e_subjectGraph.append(e_outputList)

        return e_subjectGraph
    
    def Log(self):
        logging.info("[PreProcess] convert blif")
        logging.info("The number of elements is following")
        logging.info("Nodes: {}".format(self.__nNodes))
        logging.info("Subckts: {}".format(self.__nSubckts))
        logging.info("Latches: {}".format(self.__nLatches))
