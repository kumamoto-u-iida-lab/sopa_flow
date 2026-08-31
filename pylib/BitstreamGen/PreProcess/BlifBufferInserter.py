from __future__ import annotations

import copy
import logging
from typing import List
from abc import ABCMeta, abstractmethod

from blifparser import blifparser

# Constant Parameters to parse dff subckt
DFF_NAME_WORD = "DFF_PN0"
DFF_INPUT_WORD = "D="
DFF_OUTPUT_WORD = "Q="
DFF_CLK_WORD = "C="
DFF_RESET_WORD = "R="

# 任意の回路の入出力を解釈する場合は、このクラスをインタフェースとして継承する。
# buffer inserterでのみ利用する。
class ISubCircuit(metaclass=ABCMeta):
    @property
    @abstractmethod
    def inputs(self)->List[str]:
        # because this is an interface
        pass # pragma: no cover

class SubCircuitDFF(ISubCircuit):
    def __init__(self, subckt:blifparser.keywords.subfiles.Subckt):
        # region Guard
        if not isinstance(subckt, blifparser.keywords.subfiles.Subckt):
            raise TypeError("SubCircuitDFF input subckt shall be Subckt type.")
        
        if not DFF_NAME_WORD in subckt.modelname:
            raise ValueError("SubCircuitDFF input subckt shall be kind of DFF.")
        # endregion

        self.__inputs = []

        for param in subckt.params:
            if DFF_INPUT_WORD in param:
                dffInput = param.replace(DFF_INPUT_WORD, "")
                self.__inputs.append(dffInput)

    @property
    def inputs(self)->List[str]:
        return self.__inputs

class SubCircuits:
    def __init__(self, circuits:List[ISubCircuit]=None):

        # region Guard
        if circuits is None:
            circuits = []

        if not isinstance(circuits, List):
            raise TypeError("circuits shall be List type.")

        if not circuits:
            pass
        elif not all(isinstance(elm, ISubCircuit) for elm in circuits):
            raise TypeError("circuits shall be List[ISubCircuit] type.")
        # endregion

        self.__subCircuits = circuits

    def AddSubCircuit(self, circuit:ISubCircuit)->SubCircuits:
        # Guard
        if not isinstance(circuit, ISubCircuit):
            raise TypeError("circuit shall be ISubCircuit type.")
        addedList = self.__subCircuits + [circuit]
        return self.__class__(addedList)
    
    @property
    def inputsEachSubCircuit(self)->List[List[str]]:
        retList = []

        for subCircuit in self.__subCircuits:
            retList.append(subCircuit.inputs)

        return retList


class BlifBufferInserter:
    BUF = [['1','1']]
    def __init__(self, inBlif:blifparser.keywords.generic.Blif):
        # Guard
        if not isinstance(inBlif, blifparser.keywords.generic.Blif):
            raise TypeError("inBlif shall be Blif type")
        
        self.__nInsertedBuffer = 0

        subCircuits = self.__GetSubCircuitsInputs(inBlif)
        newBlif = self.__InsertDummyBuffer(inBlif, subCircuits)

        self.__blif = newBlif
        self.Log()

    @staticmethod
    def __GetSubCircuitsInputs(inBlif:blifparser.keywords.generic.Blif)\
        ->SubCircuits:
        subCircuits = SubCircuits()
        for subckt in inBlif.subcircuits:
            # subcktへの入力は、種類によらず抽出する必要がある。
            if DFF_NAME_WORD in subckt.modelname:
                parsedSubckt:ISubCircuit = SubCircuitDFF(subckt)
            # Exclude subckt DFF has not implemented
            # DFF以外のサブサーキットはスルーされます。
            
                subCircuits = subCircuits.AddSubCircuit(parsedSubckt)

        return subCircuits
    
    def __InsertDummyBuffer(self, inBlif:blifparser.keywords.generic.Blif,
                            subCircuits:SubCircuits)\
        ->blifparser.keywords.generic.Blif:
        modBlif = copy.deepcopy(inBlif)

        for circuit in subCircuits.inputsEachSubCircuit:
            for fanin in circuit:
                # blifにバッファを追加
                bufClause = f"{fanin} DummyBuf{self.__nInsertedBuffer}"
                newBuf = blifparser.keywords.generic.Names(bufClause, False)
                # 真理値表をbufferに
                newBuf.truthtable = BlifBufferInserter.BUF
                modBlif.booleanfunctions.append(newBuf)
                self.__nInsertedBuffer += 1

        return modBlif

    @property
    def blif(self)->blifparser.keywords.generic.Blif:
        return self.__blif
    
    def Log(self):
        logging.info(f"Inserted {self.__nInsertedBuffer} buffers.")