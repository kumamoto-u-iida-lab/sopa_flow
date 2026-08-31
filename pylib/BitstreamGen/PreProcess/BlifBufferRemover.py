import copy
import logging

from blifparser import blifparser

class BlifBufferRemover:
    CONST = ["$false", "$true", "$undef"]
    BUF = [['1','1']]
    
    def __init__(self, inBlif:blifparser.keywords.generic.Blif):
        # Guard
        if not isinstance(inBlif, blifparser.keywords.generic.Blif):
            raise TypeError("inBlif shall be Blif type")
        
        self.__nRemovedBuffer = 0
        self.__blif = self.__SearchAndRemoveBuffer(inBlif)
        self.Log()

    def __SearchAndRemoveBuffer(self, inBlif:blifparser.keywords.generic.Blif)\
        ->blifparser.keywords.generic.Blif:
        modBlif = copy.deepcopy(inBlif)
        
        outputs = modBlif.outputs.outputs if modBlif.outputs else []

        # bufferを探索して、削除対象なら削除する
        for node in inBlif.booleanfunctions:
            # バッファでない場合は次へ
            if node.truthtable != BlifBufferRemover.BUF:
                continue

            fanin = node.inputs[0]
            fanout = node.output

            # バッファのfanoutがPOに含まれていない場合
            if fanout not in outputs:
                # fanout→faninに置き換え
                self.__replaceSignal(modBlif, fanout, fanin)
                self.__nRemovedBuffer += 1

            # バッファのfanoutがPOに含まれており、かつファンインが定数の場合、何もしない
            elif fanin in BlifBufferRemover.CONST:
                pass

            # バッファのfanoutがPOに含まれており、ファンインが定数でない場合
            else:
                # fanin→fanoutに置き換え
                self.__replaceSignal(modBlif, fanin, fanout)
                self.__nRemovedBuffer += 1

        # 同名の入出力を持つバッファを削除 (.names X X + 1 1)
        modBlif.booleanfunctions = [
            func for func in modBlif.booleanfunctions
            if not (func.truthtable == BlifBufferRemover.BUF and 
                    func.inputs[0] == func.output)
        ]

        return modBlif

    def __replaceSignal(self, blif, oldSignal, newSignal):
        """すべての.names, .latch, .subcktでoldSignalをnewSignalに置き換える"""
        
        # .names (booleanfunctions) - 入力も出力もすべて置き換え
        for func in blif.booleanfunctions:
            for j, inp in enumerate(func.inputs):
                if inp == oldSignal:
                    func.inputs[j] = newSignal
            if func.output == oldSignal:
                func.output = newSignal

        # .latch (latches)
        if blif.latches:
            for latch in blif.latches:
                if latch.input == oldSignal:
                    latch.input = newSignal
                if latch.output == oldSignal:
                    latch.output = newSignal

        # .subckt (subcircuits)
        if blif.subcircuits:
            for subckt in blif.subcircuits:
                for j, param in enumerate(subckt.params):
                    paramDescription = param.split('=')
                    if len(paramDescription) == 2 and paramDescription[1] == oldSignal:
                        subckt.params[j] = paramDescription[0] + '=' + newSignal

    @property
    def blif(self)->blifparser.keywords.generic.Blif:
        return self.__blif

    def Log(self):
        logging.info(f"Removed {self.__nRemovedBuffer} buffers.")


# import copy
# import logging

# from blifparser import blifparser

# class BlifBufferRemover:
#     CONST = ["$false", "$true", "$undef"]
#     BUF = [['1','1']]
#     def __init__(self, inBlif:blifparser.keywords.generic.Blif):
#         # Guard
#         if not isinstance(inBlif, blifparser.keywords.generic.Blif):
#             raise TypeError("inBlif shall be Blif type")
        
#         self.__nRemovedBuffer = 0

#         tmpBlif = self.__SearchAndRemoveBuffer(inBlif)

#         # 1次的な短絡だけでは消え切らないバッファがあるので2回実施。
#         # 理想的にはバッファの数が変わらなくなるまで実行した方が良い。
#         newBlif = self.__SearchAndRemoveBuffer(tmpBlif)

#         self.__blif = newBlif
#         self.Log()

#     def __SearchAndRemoveBuffer(self, inBlif:blifparser.keywords.generic.Blif)\
#         ->blifparser.keywords.generic.Blif:
#         modBlif = copy.deepcopy(inBlif)

#         shortedWire = []

#         # bufferを探索して、削除対象なら削除する
#         for node in inBlif.booleanfunctions:
#             # バッファでない場合は次へ
#             if node.truthtable != BlifBufferRemover.BUF:
#                 continue

#             # こののちの3パターンは削除不可なバッファのため何もせずにcontinueしている。

#             # バッファのfaninがモジュールのinputに含まれる、かつ
#             # fanoutがモジュールのoutputに含まれる場合何もしない 
#             if node.inputs[0] in inBlif.inputs.inputs and\
#                 node.output in inBlif.outputs.outputs:
#                 # ここにたどり着いたとき、nodeがバッファであることが確定しているので、
#                 # inputs[0] がinputとみなせる。
#                 continue

#             # バッファのfanoutがモジュールのoutputに含まれている かつ
#             # バッファのfaninが定数値の場合、何もしない
#             if node.inputs[0] in BlifBufferRemover.CONST and\
#                 node.output in inBlif.outputs.outputs:
#                 continue

#             # POの短絡により、削除済みのインプットを持つ場合何もしない
#             if node.inputs[0] in shortedWire:
#                 continue

#             # ここまでたどり着いた場合、そのnodeは削除(短絡)の対象。
#             # バッファのfanoutがPOの場合と、そうでない場合で処理が異なる。

#             # region change fanin signal to fanout signal
#             # バッファのfanoutがPOの場合、そのバッファのfaninの信号をすべて
#             # fanoutに置き換える(短絡させる)
#             if node.output in modBlif.outputs.outputs:

#                 # latchの場合
#                 if modBlif.latches:
#                     raise ValueError("eFPGA does not accept latch.")

#                 # boolean functionの場合
#                 for i, func in enumerate(modBlif.booleanfunctions):
#                     # 自分自身ならスルー
#                     if str(node) == str(func):
#                         continue

#                     for j, fanin in enumerate(func.inputs):
#                         if fanin == node.inputs[0]:
#                             modBlif.booleanfunctions[i].inputs[j] = node.output
#                             #shortedWire.append(fanin)

#                     if func.output == node.inputs[0]:
#                         modBlif.booleanfunctions[i].output = node.output
#                         shortedWire.append(fanin)
#                         #print(shortedWire)

#                 # subcktの場合
#                 for i, subckt in enumerate(modBlif.subcircuits):
#                     for j, param in enumerate(subckt.params):
#                         paramDescription = param.split('=')
#                         if paramDescription[1] == node.inputs[0]:
#                             newDescription = paramDescription[0] + '=' + node.output
#                             modBlif.subcircuits[i].params[j] = newDescription
#                             shortedWire.append(paramDescription[1])

#                 # バッファの記述を削除
#                 newBoolFunc = [i for i in modBlif.booleanfunctions if str(i) != str(node)]

#                 modBlif.booleanfunctions = newBoolFunc
#                 self.__nRemovedBuffer += 1
#                 continue

#             # endregion

#             # region change fanout signal to fanin signal
#             # バッファのfanoutがPOではない場合、そのバッファのfanoutの信号をすべて
#             # faninに置き換える(短絡させる)
#             # latchの場合
#             if modBlif.latches:
#                 raise ValueError("eFPGA does not accept latch.")

#             # boolean functionの場合
#             for i, func in enumerate(modBlif.booleanfunctions):
#                 # 自分自身ならスルー
#                 if str(node) == str(func):
#                     continue

#                 for j, fanin in enumerate(func.inputs):
#                     if fanin == node.output:
#                         modBlif.booleanfunctions[i].inputs[j] = node.inputs[0]

#             # subcktの場合
#             for i, subckt in enumerate(modBlif.subcircuits):
#                 for j, param in enumerate(subckt.params):
#                     paramDescription = param.split('=')
#                     if paramDescription in shortedWire:
#                         continue

#                     if paramDescription[1] == node.output:
#                         newDiscription = paramDescription[0] + '=' + node.inputs[0]
#                         modBlif.subcircuits[i].params[j] = newDiscription

#             # バッファの記述を削除
#             newBoolFunc = [i for i in modBlif.booleanfunctions if str(i) != str(node)]
            
#             modBlif.booleanfunctions = newBoolFunc
#             self.__nRemovedBuffer += 1
#         # endregion

#         return modBlif

#     @property
#     def blif(self)->blifparser.keywords.generic.Blif:
#         return self.__blif

#     def Log(self):
#         logging.info(f"Removed {self.__nRemovedBuffer} buffers.")