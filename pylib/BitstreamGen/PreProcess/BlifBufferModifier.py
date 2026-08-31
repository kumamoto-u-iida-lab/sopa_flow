from __future__ import annotations

import copy
import logging

from blifparser import blifparser

class BlifBufferModifier:
    BUF = [['1', '1']]
    AND = [['1', '1', '1']]
    NOT = [['0', '1']]
    CONST_SIGNAL = ["$false", "$true", "$undef"]

    def __init__(self, inBlif:blifparser.keywords.generic.Blif):
        # Guard
        if not isinstance(inBlif, blifparser.keywords.generic.Blif):
            raise TypeError("inBlif shall be Blif type")
        
        self.__nModifiedBuffer = 0

        newBlif = self.__ReplaceBuffers(inBlif)

        self.__blif = newBlif
        self.Log()

    def __ReplaceBuffers(self, inBlif:blifparser.keywords.generic.Blif)\
        ->blifparser.keywords.generic.Blif:
        modBlif = copy.deepcopy(inBlif)

        for func in modBlif.booleanfunctions:
            if func.truthtable != BlifBufferModifier.BUF:
                continue

            # 定数値がbufferのinputの場合
            if any(elm in BlifBufferModifier.CONST_SIGNAL for elm in func.inputs):
                inv = self.__Invert(func.inputs[0]) # バッファなので、長さ1が保証される
                func.inputs[0] = inv
                func.truthtable = BlifBufferModifier.NOT
                self.__nModifiedBuffer += 1
                continue

            func.inputs.append("$true")
            func.truthtable = BlifBufferModifier.AND
            self.__nModifiedBuffer += 1

        return modBlif

    @property
    def blif(self)->blifparser.keywords.generic.Blif:
        return self.__blif

    @staticmethod
    def __Invert(inStr:str)->str:
        if inStr == "$false":
            return "$true"
        if inStr == "$true":
            return "$false"

        raise ValueError("myNot input is only true or false")

    def Log(self):
        logging.info(f"Modified {self.__nModifiedBuffer} buffers.")