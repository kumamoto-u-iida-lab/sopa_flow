"""
    ファイル名 : main.py

    description:


"""





########################################################################################################################
#                                                                                                                      #
#      import                                                                                                          #
#                                                                                                                      #
########################################################################################################################

import sys
import argparse
import xml.etree.ElementTree as ET
import networkx as nx
import re
import datetime
import time



########################################################################################################################
#                                                                                                                      #
#      クラスの定義                                                                                                     #
#          SubejectGraph : サブジェクトグラフの情報(name, inpput_list, out_put_list,‥‥)を表す                          #
#          PatternGraph  : パターングラフの情報(name, input_list, output_ist,‥‥)を表す                                 #
#          Cell          : 論理セルの名前・入出力情報(name, input_list, output_list)を表す                               #
#          Node          : グラフのノード情報(id, type, iput_list, output,‥‥)を表す                                    #
#          Subckt        : サブジェクトグラフのサブサーキットの情報を表す                                                 #
#          Latch         : サブジェクトグラフのラッチの情報を表す                                                        #
#          Buffer        : サブジェクトグラフのバッファ情報を表す                                                        #
#                                                                                                                      #
#                                                                                                                      #
#       クラスの階層構造                                                                                                #
#          ・SubjectGraph                                                                                              #
#                 |------Node                                                                                          #
#                 |------Subckt                                                                                        #
#                 |------Latch                                                                                         #
#                  ------Buffer                                                                                        #
#          ・PatternGraph                                                                                              #
#                  ------Node                                                                                          #
#          ・Cell                                                                                                      #
#                                                                                                                      #
########################################################################################################################





class SubjectGraph():




    def __init__(self, subjectgraph_element):
        """
        関数名 : __init__

        description:
            SubjectGraphクラスのコンストラクタ。

        Arguments:
            subjectgraph_element(xml.etree.ElementTree.Element)

        Variables:
            self.subjectgraph_element(xml.etree.ElementTree.Element)
        
        Functions:
            self.name()
            self.input_list()
            self.output_list()
            self.node_list()
            self.subckt_list()
            self.latch_list()
            self.edge_list()
            self.node_dict()

        
        Returns:

        """

        self.subjectgraph_element = subjectgraph_element
        self.name()
        self.input_list()
        self.output_list()
        self.node_list()
        self.subckt_list()
        self.latch_list()
        self.buffer_list()

        #　以下はself.node_list()の後に実行されなければならない
        self.edge_list()    
        self.node_dict()
        self.node_id_list()





    def name(self):
        """
        関数名 : name

        description:
            サブジェクトグラフの名前をname属性へ格納する関数。

        Arguments:

        Variables:
            self.name(string)
        
        Functions
        
        Returns:

        """

        #　subjectgraph要素の子要素の中からname要素を見つけ、テキストデータを取得し、格納する
        self.name = self.subjectgraph_element.find("name").text
    




    def input_list(self):
        """
        関数名 : input_list

        description:
            サブジェクトグラフのすべての入力をinput_list属性に格納する関数。
            (例： input_list = ["入力１", "入力２", "入力３", ‥‥])

        Arguments:

        Variables:
            self.input_list(list[string])
        
        Functions
            generate_list(subjectgraph_element, "input_list") : subjectgraph要素と文字列"input_list"を渡すことで、subjectgraph要素の子要素であるinput_list要素の子要素のテキストデータをリスト形式に変換して返す関数
        
        Returns:

        """

        self.input_list = generate_list(self.subjectgraph_element, "input_list")
    




    def output_list(self):
        """
        関数名 : output_list

        description:
            サブジェクトグラフのすべての出力をoutput_list属性に格納する関数。
            (例： output_list = ["出力１", "出力２", "出力３", ‥‥])

        Arguments:

        Variables:
            self.output_list(list[string])
        
        Functions
            generate_list(subjectgraph_element, "output_list") : subjectgraph要素と文字列"output_list"を渡すことで、subjectgraph要素の子要素であるoutput_list要素の子要素のテキストデータをリスト形式に変換して返す関数
        
        Returns:

        """

        self.output_list = generate_list(self.subjectgraph_element, "output_list")





    def node_list(self):
        """
        関数名 : node_list

        description:
            サブジェクトグラフのすべてのノード情報をnode_list属性に格納する関数。
            (例： node_list = [Node_1, Node_2, Node_3, ‥‥])

        Arguments:

        Variables:
            self.node_list(list[Node])                              
            node_element_list(list[xml.etree.ElementTree.Element])        : subjectgraph要素の子要素であるnode要素のすべてがリスト形式で格納されている変数
            node_element(xml.etree.ElementTree.Element)                   : node_element_listに格納された各ノード要素を表す変数
            tmp(Node)                                                     : Nodeクラスを構築する際に一時的にデータを保存しておく変数
        
        Functions
        
        Returns:

        """

        #　初期化
        self.node_list = []

        #　findallは同じ名前のすべての子要素を見つける
        #　subjectgraph要素内のすべてのnode要素を見つけリスト化し、node_element_listに格納
        node_element_list = self.subjectgraph_element.findall("node")

        #　node要素の数だけループする
        for node_element in node_element_list:

            #　Nodeクラスのインスタンス化
            tmp = Node(node_element)

            #　Nodeクラスのサブジェクトグラフ用の初期化メソッドを実行
            tmp.initialize_subjectgraph_node()

            #　node_listに追加
            self.node_list.append(tmp)





    def subckt_list(self):
        """
        関数名 : subckt_list

        description:
            サブジェクトグラフのすべてのサブサーキット情報をsubckt_list属性に格納する関数。
            (例： subckt_list = [Subckt_1, Subckt_2, Subckt_3, ‥‥])

        Arguments:

        Variables:
            self.subckt_list(list[Subckt])                              
            subckt_element_list(list[xml.etree.ElementTree.Element])        : subjectgraph要素の子要素であるsubckt要素のすべてがリスト形式で格納されている変数
            subckt_element(xml.etree.ElementTree.Element)                   : subckt_element_listに格納された各ノード要素を表す変数
            tmp(Subckt)                                                     : Subcktクラスを構築する際に一時的にデータを保存しておく変数
        
        Functions
        
        Returns:

        """

        # 初期化
        self.subckt_list = []

        #　findallは同じ名前のすべての子要素を見つける
        #　subjectgraph要素のすべてのsubckt要素を見つけリスト化し、subckt_element_listに格納
        subckt_element_list = self.subjectgraph_element.findall("subckt")

        #　subckt要素の数だけループする
        for subckt_element in subckt_element_list:
            
            # Subcktクラスのインスタンス化
            tmp = Subckt(subckt_element)

            # subckt_listに追加
            self.subckt_list.append(tmp)





    def latch_list(self):
        """
        関数名 : latch_list

        description:
            サブジェクトグラフのすべてのラッチ情報をlatch_list属性に格納する関数。
            (例： latch_list = [Latch_1, Latch_2, Latch_3, ‥‥])

        Arguments:

        Variables:
            self.latch_list(list[Latch])                              
            latch_element_list(list[xml.etree.ElementTree.Element])        : subjectgraph要素の子要素であるlatch要素のすべてがリスト形式で格納されている変数
            latch_element(xml.etree.ElementTree.Element)                   : latch_element_listに格納された各ノード要素を表す変数
            tmp(Latch)                                                     : Latchクラスを構築する際に一時的にデータを保存しておく変数
        
        Functions
        
        Returns:

        """

        # 初期化
        self.latch_list = []

        #　findallは同じ名前のすべての子要素を見つける
        #　subjectgraph要素のすべてのlatch要素を見つけリスト化し、latch_element_listに格納
        latch_element_list = self.subjectgraph_element.findall("latch")

        #　latch要素の数だけループする
        for latch_element in latch_element_list:

            # Latchクラスのインスタンス化
            tmp = Latch(latch_element)

            # latch_listに追加
            self.latch_list.append(tmp)





    def buffer_list(self):
        """
        関数名 : buffer_list

        description:
            サブジェクトグラフのすべてのバッファ情報をbuffer_list属性に格納する関数。
            (例： buffer_list = [Buffer_1, Buffer_2, Buffer_3, ‥‥])

        Arguments:

        Variables:
            self.buffer_list(list[Buffer])                              
            buffer_element_list(list[xml.etree.ElementTree.Element])        : subjectgraph要素の子要素であるBuffer要素のすべてがリスト形式で格納されている変数
            buffer_element(xml.etree.ElementTree.Element)                   : buffer_element_listに格納された各ノード要素を表す変数
            tmp(Buffer)                                                     : Bufferクラスを構築する際に一時的にデータを保存しておく変数
        
        Functions
        
        Returns:

        """

        # 初期化
        self.buffer_list = []

        #　findallは同じ名前のすべての子要素を見つける
        #　subjectgraph要素のすべてのbuffer要素を見つけリスト化し、buffer_element_listに格納
        buffer_element_list = self.subjectgraph_element.findall("buffer")

        #　buffer要素の数だけループする
        for buffer_element in buffer_element_list:

            # Bufferクラスのインスタンス化
            tmp = Buffer(buffer_element)

            # buffer_listに追加
            self.buffer_list.append(tmp)
        
    



    def edge_list(self):
        """
        関数名 : edge_list

        description:
            サブジェクトグラフのすべてのエッジをnode_listを用いて作成し、edge_list属性に格納する関数。
            (例： edge_list = [(1,2), (2,3), (1,3), ‥‥])

        Arguments:

        Variables:
            self.edge_list(list[tuple(int, int)])   :                              
            node_obj(Node)                          : サブジェクトグラフのノード1つを表す変数。エッジの始点を表すノードに対応している。
            other_node_obj(Node)                    : サブジェクトグラフのノード1つを表す変数。エッジの終点を表すノードに対応している。
            edge_tuple(tuple(int, int))             : エッジ1つを表す変数。サブジェクトグラフのエッジには向きが存在するため、(エッジの始点, エッジの終点)のように表されている。

        Functions
        
        Returns:

        Constraints:
            エッジの生成にはnode_listを用いているため、self.node_listの後に実行されなければならない

        """

        # 初期化
        self.edge_list = []

        ### 以下でエッジを生成する ###

        # node_objの出力とother_node_objの入力が一致した場合、そのエッジは存在するため、edge_listに追加する
        for node_obj in self.node_list:

            #ノードの出力がグラフ全体の出力である場合、そのノードが始点のエッジは存在しないため、実行しない
            if node_obj.output in self.output_list:

                continue

            for other_node_obj in self.node_list:

                # other_node_objの入力リストにnode_objの出力が含まれる場合に実行
                if node_obj.output in other_node_obj.input_list:

                    #1つのエッジをタプルで作成　(始点のノード番号、終点のノード番号)
                    edge_tuple = (node_obj.id, other_node_obj.id)

                    # edge_listに追加
                    self.edge_list.append(edge_tuple)
    




    def node_dict(self):
        """
        関数名 : node_dict

        description:
            サブジェクトグラフの一部のノード情報をnode_listを用いて作成し、node_dict属性に格納する関数。
            (例： node_dict = [1:{"type":"AND", "fanin_num":2, "fanout_num":1}, 2:{"type":"INV", "fanin_num":1, "fanout_num":int_max} ‥‥])

        Arguments:

        Variables:
            self.node_dict(dict)   :                              
            node_obj(Node)         : サブジェクトグラフのノード1つを表す変数。

        Functions
        
        Returns:

        Constraints:
            辞書形式のノード情報の生成にはnode_listを用いているため、self.node_listの後に実行されなければならない

        """

        # 初期化
        self.node_dict = {}

        ### 以下で辞書形式のノード情報を生成する ###

        # すべてのノード数だけループする
        for node_obj in self.node_list:
            
            # node_dictに格納される形式 ( ノード番号(int): {"type": ノードのタイプ(string), "fanin_num: ファンインの数(int), "fanout_num":, ファンアウトの数(int)} )
            # setdefaultで辞書に格納される
            self.node_dict.setdefault(node_obj.id, {"type":node_obj.type, "fanin_num":node_obj.fanin_num, "fanout_num":node_obj.fanout_num, "input_list":node_obj.input_list, "output":node_obj.output})

    



    def node_id_list(self):
        """
        関数名 : node_id_list

        description:
            サブジェクトグラフのすべてのノードのID情報をnode_listを用いて作成し、node_id_list属性に格納する関数。
            (例： node_id_list = [1, 2, 3, 4 ‥‥])

        Arguments:

        Variables:
            self.node_id_list(list[int])    :                              
            node_obj(Node)                  : サブジェクトグラフのノード1つを表す変数。

        Functions
        
        Returns:

        Constraints:
            ノードのID情報の生成にはnode_listを用いているため、self.node_listの後に実行されなければならない

        """

        # 初期化
        self.node_id_list = []

        # すべてのノード数だけループする
        for node_obj in self.node_list:

            # node_id_listに格納される形式
            self.node_id_list.append(node_obj.id)
            





class PatternGraph():



    def __init__(self, patterngraph_element, cell_obj): 
        """
        関数名 : __init__

        description:
            PatternGraphクラスのコンストラクタ。

        Arguments:
            patterngraph_element(xml.etree.ElementTree.Element) : 
            cell_obj(Cell)                                      : 

        Variables:
            self.patterngraph_element(xml.etree.ElementTree.Element)    : 
        
        Functions:
            self.name()
            self.input_list(cell_obj)
            self.output_list(cell_obj)
            self.node_list()
            self.edge_list()
            self.node_dict()

        
        Returns:

        """
        self.patterngraph_element = patterngraph_element
        self.name()
        self.configuration_memory()
        self.input_list(cell_obj)
        self.output_list(cell_obj)
        self.node_list()
        self.edge_list()

        #　以下はself.node_list()の後に実行されなければならない
        self.node_dict()
        self.node_id_list()
    




    def name(self):
        """
        関数名 : name

        description:
            パターングラフの名前をname属性へ格納する関数。

        Arguments:

        Variables:
            self.name(string)
        
        Functions
        
        Returns:

        """

        #　patterngraph要素の子要素の中からname要素を見つけ、テキストデータを取得し、格納する
        self.name = self.patterngraph_element.find("name").text





    def configuration_memory(self):
        

        self.configuration_memory = self.patterngraph_element.find("configuration_memory").text
    



    
    def input_list(self, cell_obj):
        """
        関数名 : input_list

        description:
            パターングラフのすべての入力をinput_list属性に格納する関数。
            input_listには、セルの入力リストと属性(cell_input)が一致した順番に入れられる。
            (例： cell.input_list = ["入力A", "入力B", "入力C", ‥‥] のとき
                        input_list = ["cell_input属性が入力Aの入力", "cell_input属性が入力Bの入力", "cell_input属性が入力Cの入力", ‥‥])

        Arguments:
            cell_obj(Cell) : Cellクラスのオブジェクト。入力の順番を同期させるために引数に指定している。

        Variables:
            self.input_list(list[string])
        
        Functions
            generate_list_cell_order(self.patterngraph_element, "input_list", "input", cell_obj.input_list, "cell_input") : 
                patterngraph要素とセルオブジェクト、3つの指定可能な文字列を渡すことで、patterngraph要素の子要素であるinput_list要素の子要素のテキストデータを、セルオブジェクトの入力順にリスト形式に変換して返す関数
        
        Returns:

        """

        self.input_list = generate_list_cell_order(self.patterngraph_element, "input_list", "input", cell_obj.input_list, "cell_input")


    


    def output_list(self, cell_obj):
        """
        関数名 : output_list

        description:
            パターングラフのすべての出力をoutput_list属性に格納する関数。コンストラクタ内で呼び出される。
            output_listには、セルの入力リストと属性(cell_input)が一致した順番に入れられる。
            (例： cell.output_list = ["出力A", "出力B", "出力C", ‥‥] のとき
                        output_list = ["cell_output属性が出力Aの出力", "cell_output属性が出力Bの出力", "cell_output属性が出力Cの出力"])

        Arguments:
            cell_obj(Cell) : Cellクラスのオブジェクト。出力の順番を同期させるために引数に指定している。

        Variables:
            self.output_list(list[string])
        
        Functions
            generate_list_cell_order(self.patterngraph_element, "output_list", "output", cell_obj.output_list, "cell_output") : 
                patterngraph要素とセルオブジェクト、3つの指定可能な文字列を渡すことで、patterngraph要素の子要素であるoutput_list要素の子要素のテキストデータを、セルオブジェクトの出力順にリスト形式に変換して返す関数
        
        Returns:

        """

        self.output_list = generate_list_cell_order(self.patterngraph_element, "output_list", "output", cell_obj.output_list, "cell_output")

    



    def node_list(self):
        """
        関数名 : node_list

        description:
            パターングラフのすべてのノード情報をnode_list属性に格納する関数。
            (例： node_list = [Node_1, Node_2, Node_3, ‥‥])

        Arguments:

        Variables:
            self.node_list(list[Node])                              
            node_element_list(list[xml.etree.ElementTree.Element])        : patterngraph要素の子要素であるnode要素のすべてがリスト形式で格納されている変数
            node_element(xml.etree.ElementTree.Element)                   : node_element_listに格納された各ノード要素を表す変数
            tmp(Node)                                                     : Nodeクラスを構築する際に一時的にデータを保存しておく変数
        
        Functions
        
        Returns:

        """

        #　初期化
        self.node_list = []

        #　patterngraph要素内のnode_list要素を見つけ、node_list_elementに格納
        node_list_element = self.patterngraph_element.find("node_list")

        #　findallは同じ名前のすべての子要素を見つける
        #　node_list要素内のすべてのnode要素を見つけリスト化し、node_element_listに格納
        node_element_list = node_list_element.findall("node")

        #　node要素の数だけループする
        for node_element in node_element_list:

            #　Nodeクラスのインスタンス化
            tmp = Node(node_element)

            #　Nodeクラスのパターングラフ用の初期化メソッドを実行
            tmp.initialize_patterngraph_node()

            #　node_listに追加
            self.node_list.append(tmp)
        




    def edge_list(self):
        """
        関数名 : edge_list

        description:
            パターングラフのすべてのエッジをedge_list属性に格納する関数。
            (例： edge_list = [(1,2), (2,3), (1,3), ‥‥])

        Arguments:

        Variables:
            self.edge_list(list[tuple(int, int)])                       :                              
            edge_list_element(xml.etree.ElementTree.Element)            : patterngraph要素の子要素であるedge_list要素が格納されている変数
            edge_element_list(list[xml.etree.ElementTree.Element])      : edge_list要素の子要素であるedge要素のすべてがリスト形式で格納されている変数
            edge_element(xml.etree.ElementTree.Element)                 : edge_element_listに格納されたedge要素を表す変数
            start(int)                                                  : エッジの始点であるノードのIDを表す変数
            stop(int)                                                   : エッジの終点であるノードのIDを表す変数
            edge_tuple(tuple(int, int))                                 : エッジ1つを表す変数。サブジェクトグラフのエッジには向きが存在するため、(エッジの始点, エッジの終点)のように表されている。

        Functions
        
        Returns:

        """

        #　初期化
        self.edge_list = []

        #　patterngraph要素内からedge_list要素を検索し、edge_list_elementに格納
        edge_list_element = self.patterngraph_element.find("edge_list")


        ### 例外処理 ###
        try:

            #　edge_list要素内からedge要素をすべて検索し、edge_element_listに格納
            edge_element_list = edge_list_element.findall("edge")
        
        except AttributeError:
            # edge_list_elementが空の場合(エッジがない場合)に発生
            # エッジがない場合は何もしない
            pass


        else:

            #　edge要素の数だけループする
            for edge_element in edge_element_list:

                #　edge要素内のstart(stop)要素を検索し、文字列形式の数字をint型にして格納
                #　start(stop)要素のテキストは、文字列形式の自然数(0を含まない)のみ
                start = int(edge_element.find("start").text)
                stop = int(edge_element.find("stop").text)

                #　エッジの生成
                edge_tuple = (start, stop)

                self.edge_list.append(edge_tuple)
        




    def node_dict(self):
        """
        関数名 : node_dict

        description:
            パターングラフの一部のノード情報をself.node_listを用いて作成し、node_dict属性に格納する関数
            (例： node_dict = [1:{"type":"AND", "fanin_num":2, "fanout_num":1}, 2:{"type":"INV", "fanin_num":1, "fanout_num":int_max} ‥‥])

        Arguments:

        Variables:
            self.node_dict(dict)   :                             
            node_obj(Node)         : サブジェクトグラフのノード1つを表す変数

        Functions:
        
        Returns:

        Constraints:
            辞書形式のノード情報の生成にはnode_listを用いているため、self.node_listの後に実行されなければならない

        """

        self.node_dict = {}

        for node in self.node_list:

            self.node_dict.setdefault(node.id, {"type":node.type, "fanin_num":node.fanin_num, "fanout_num":node.fanout_num})

    



    def node_id_list(self):
        """
        関数名 : node_id_list

        description:
            パターングラフのすべてのノードのID情報をnode_listを用いて作成し、node_id_list属性に格納する関数。
            (例： node_id_list = [1, 2, 3, 4 ‥‥])

        Arguments:

        Variables:
            self.node_id_list(list[int])    :                              
            node_obj(Node)                  : サブジェクトグラフのノード1つを表す変数。

        Functions
        
        Returns:

        Constraints:
            ノードのID情報の生成にはnode_listを用いているため、self.node_listの後に実行されなければならない

        """

        self.node_id_list = []

        for node_obj in self.node_list:

            self.node_id_list.append(node_obj.id)
    




    def get_input_num(self):

        input_num = 0

        for input in self.input_list:

            if input != "N" and input != "T" and input != "F":

                input_num += 1
        
        return input_num
    




    def get_node_num(self):

        return len(self.node_list)





class Cell():
     
    """
    class名 : Cell

    description:
        このクラスはターゲットFPGAの論理セルの簡単な情報(name, input, ‥‥)を表す

    Attributes:
        name(str)               : 
        input_list(list[str])   : 
        output_list(list[str])  : 
        io_list(list[str])      : 


    Methods:
        __init__(self, cell_element)    :
        name(self)                      :
        input(self)                     :
        output(self)                    :
        ioput(self)                     :

    Usages:
        #クラスのインスタンス化
        cell = Cell(cell_element)

    """
    
    def __init__(self, cell_element):
        """
        関数名 : __init__

        description:
            Cellクラスのコンストラクタ。

        Arguments:
            cell_element(xml.etree.ElementTree.Element) : 

        Variables:
            self.cell_element(xml.etree.ElementTree.Element)    : 
        
        Functions:
            self.name()         : 
            self.input_list()   : 
            self.output_list()  : 
            self.io_list()      : 

        
        Returns:

        """
        self.cell_element = cell_element
        self.name()
        self.input_list()
        self.output_list()

        #　以下はself.input_list(),self.output_list()の後に実行されなければならない
        self.io_list()
    




    def name(self):
        """
        関数名 : name

        description:
            セルの名前をname属性へ格納する関数。

        Arguments:

        Variables:
            self.name(string)
        
        Functions
        
        Returns:

        """

        self.name = self.cell_element.find("name").text
    




    def input_list(self):
        """
        関数名 : input_list

        description:
            セルのすべての入力をinput_list属性に格納する関数。
            (例： input_list = ["入力１", "入力２", "入力３", ‥‥])

        Arguments:

        Variables:
            self.input_list(list[string])
        
        Functions
            generate_list(cel_element, "input_list") : cell要素と文字列"input_list"を渡すことで、cell要素の子要素であるinput_list要素の子要素のテキストデータをリスト形式に変換して返す関数
        
        Returns:

        """

        self.input_list = generate_list(self.cell_element, "input_list")
    




    def output_list(self):
        """
        関数名 : output_list

        description:
            セルのすべての出力をoutput_list属性に格納する関数。
            (例： output_list = ["出力１", "出力２", "出力３", ‥‥])

        Arguments:

        Variables:
            self.output_list(list[string])
        
        Functions
            generate_list(cel_element, "output_list") : cell要素と文字列"output_list"を渡すことで、cell要素の子要素であるoutput_list要素の子要素のテキストデータをリスト形式に変換して返す関数
        
        Returns:

        """

        self.output_list = generate_list(self.cell_element, "output_list")
    




    def io_list(self):
        """
        関数名 : io_list

        description:
            セルのすべての入出力をio_list属性に格納する関数。
            (例： io_list = ["入力１", "入力２", ‥‥, "出力１", "出力２", ‥‥])

        Arguments:

        Variables:
            self.io_list(list[string])  :
            input(str)                  :
            output(str)                 :
        
        Functions
        
        Returns:

        Constraints:
            io_listの生成にはself.input_list,self.output_listを用いているため、その後に実行されなければならない

        """

        #　初期化
        self.io_list = []

        #　入力情報をio_listに格納
        for input in self.input_list:

            self.io_list.append(input)
        
        #　出力情報をio_listに格納
        for output in self.output_list:

            self.io_list.append(output)





class Node():

    """
    class名 : Node

    
    description:
        このクラスはグラフのノード情報(id, type, input, ‥‥)を表す

        
    Attributes:
        id(str)             :
        type(str)           :
        input_list(list)    :
        output(str)         :
        fanin_num(str)      :
        fanout_num(str)     :


    Methods:
        __init__(self, node_element)        :
        id(self)                            :
        type(self)                          :
        input_list(self)                    :
        output(self)                        :
        fanin_num(self)                     :
        fanout_num(self)                    :
        initialize_subjectgraph_node(self)  :
        initialize_patterngraph_node(self)  :


    Usages:
        #クラスのインスタンス化
        node = Node(node_element)

        #ノード情報の初期化(サブジェクトグラフの場合)
        node.initialize_subjectgraph_node()

        #ノード情報の初期化(パターングラフの場合)
        node.initialize_patterngraph_node()

    """





    def __init__(self, node_element):
        """
        関数名 : __init__

        description:
            Nodeクラスのコンストラクタ。

        Arguments:
            node_element(xml.etree.ElementTree.Element) :

        Variables:
            self.node_element(xml.etree.ElementTree.Element)    :
        
        Functions:
        
        Returns:

        """
        self.node_element = node_element
    




    def id(self):
        """
        関数名 : id

        description:
            ノードのIDをid属性へ格納する関数。

        Arguments:

        Variables:
            self.id(int)    :
        
        Functions:
        
        Returns:

        """

        self.id = int(self.node_element.find("id").text)
    




    def type(self):
        """
        関数名 : type

        description:
            ノードのタイプをtype属性へ格納する関数。

        Arguments:

        Variables:
            self.type(int)    :
        
        Functions:
        
        Returns:

        """

        self.type = self.node_element.find("type").text
    




    def input_list(self):
        """
        関数名 : input_list

        description:
            ノードのすべての入力をinput_list属性に格納する関数。
            (例： input_list = ["入力１", "入力２", "入力３", ‥‥])

        Arguments:

        Variables:
            self.input_list(list[string])
        
        Functions
            generate_list(node_element, "input_list") : node要素と文字列"input_list"を渡すことで、node要素の子要素であるinput_list要素の子要素のテキストデータをリスト形式に変換して返す関数
        
        Returns:

        """

        self.input_list = generate_list(self.node_element, "input_list")





    def output(self):
        """
        関数名 : output

        description:
            ノードの出力をoutput属性へ格納する関数。

        Arguments:

        Variables:
            self.output(str)    :
        
        Functions:
        
        Returns:

        """

        self.output = self.node_element.find("output").text
    




    def fanin_num(self):
        """
        関数名 : fanin_num

        description:
            ノードのファンインの数をfanin_num属性へ格納する関数。
            fanin_num要素のテキストは、文字列形式の自然数(0は含まない)と"x"(小文字のエックス)があり、
            "x"はファンインの数が任意であることを表す。

        Arguments:

        Variables:
            self.fanin_num(int)    :
        
        Functions:
        
        Returns:

        """

        #　ファンインの数が任意の場合
        if self.node_element.find("fanin_num").text == "x":

            #　sys.maxsize : 整数の最大値(32bit環境では2^(32)-1, 64bit環境では2^(64)-1)
            self.fanin_num = sys.maxsize

        else:

            self.fanin_num = int(self.node_element.find("fanin_num").text)
    




    def fanout_num(self):
        """
        関数名 : fanout_num

        description:
            ノードのファンアウトの数をfanout_num属性へ格納する関数。
            fanout_num要素のテキストは、文字列形式の自然数(0は含まない)と"x"(小文字のエックス)があり、
            "x"はファンインの数が任意であることを表す。

        Arguments:

        Variables:
            self.fanout_num(int)    :
        
        Functions:
        
        Returns:

        """

        #　ファンインの数が任意の場合
        if self.node_element.find("fanout_num").text == "x":

            #　sys.maxsize : 整数の最大値(32bit環境では2^(32)-1, 64bit環境では2^(64)-1)
            self.fanout_num = sys.maxsize

        else:

            self.fanout_num = int(self.node_element.find("fanout_num").text)
    




    def initialize_subjectgraph_node(self):
        """
        関数名 : initialize_subjectgraph_node

        description:
            サブジェクトグラフのノードに関する初期化を実行する関数。

        Arguments:

        Variables:
        
        Functions:
            id(self)            :
            type(self)          :
            input_list(self)    :
            output(self)        :
            fanin_num(self)     :
            fanout_num(self)    :
        
        Returns:

        """
        self.id()
        self.type()
        self.input_list()
        self.output()
        self.fanin_num()
        self.fanout_num()





    def initialize_patterngraph_node(self):
        """
        関数名 : initialize_patterngraph_node

        description:
            パターングラフのノードに関する初期化を実行する関数。

        Arguments:

        Variables:
        
        Functions:
            id(self)            :
            type(self)          :
            fanin_num(self)     :
            fanout_num(self)    :
        
        Returns:

        """
        self.id()
        self.type()
        self.fanin_num()
        self.fanout_num()






class Subckt():
    """
    class名 : Subckt

    
    description:
        このクラスはサブジェクトグラフのサブサーキット情報(name, ioput_dict)を表す

        
    Attributes:
        name(str)                       :
        ioput_dict(dict{str:str})       :


    Methods:
        __init__(self, subckt_element)      :
        name(self)                          :
        ioput_dict(self)                    :


    Usages:
        #クラスのインスタンス化
        subckt = Subckt(subckt_element)

    """




    def __init__(self, subckt_element):
        """
        関数名 : __init__

        description:
            Subcktクラスのコンストラクタ。

        Arguments:
            subckt_element(xml.etree.ElementTree.Element) :

        Variables:
            self.subckt_element(xml.etree.ElementTree.Element)    :
        
        Functions:
            self.name()         :
            self.ioput_dict()   :
        
        Returns:

        """
        self.subckt_element = subckt_element
        self.name()
        self.ioput_dict()





    def name(self):
        """
        関数名 : name

        description:
            サブサーキットの名前をname属性へ格納する関数。

        Arguments:

        Variables:
            self.name(string)
        
        Functions
        
        Returns:

        """

        self.name = self.subckt_element.find("name").text
    




    def ioput_dict(self):
        """
        関数名 : ioput_dict

        description:
            サブサーキットの入出力をioput_dict属性へ格納する関数。

        Arguments:

        Variables:
            self.ioput_dict(dict{str:str})                          :
            ioput_list_element(xml.etree.ElementTree.Element)       :
            ioput_element_list(list[xml.etree.ElementTree.Element]) :
            ioput_element(xml.etree.ElementTree.Element)            :
        
        Functions
        
        Returns:

        """

        #　初期化
        self.ioput_dict = dict()

        #　subckt要素内からioput_list要素を検索し、ioput_list_elementに格納
        ioput_list_element = self.subckt_element.find("ioput_list")


        ### 例外処理 ###
        try:
            
            #　ioput_list要素内からioput要素をすべて検索し、ioput_element_listに格納
            ioput_element_list = ioput_list_element.findall("ioput")
        

        except AttributeError:
            #　ioput_list_elementが空の場合(サブサーキットの入出力情報がない場合)に発生
            print("AttributeError, {}\n".format(self.name))
            print("サブジェクトグラフ内のサブサーキットに入出力情報がありません\n")

        else:

            #　ioput要素の数だけループする
            for ioput_element in ioput_element_list:

                #　ioput要素の属性「subckt_ioput」はmoduleの入出力名、ioput要素のテキストはmoduleをインスタンス化した際の入出力名である
                self.ioput_dict.setdefault(ioput_element.attrib["subckt_ioput"], ioput_element.text)





class Latch():
    """
    class名 : Latch

    
    description:
        このクラスはサブジェクトグラフのラッチ情報(input, output, ‥‥)を表す

        
    Attributes:
        input(str)          :
        output(str)         :
        type(str)           :
        clock(str)          :
        initial_state(str)  :


    Methods:
        __init__(self, latch_element)       :
        input(self)                         :
        output(self)                        :
        type(self)                          :
        clock(self)                         :
        initial_state(self)                 :


    Usages:
        #クラスのインスタンス化
        latch = Latch(latch_element)

    """

    def __init__(self, latch_element):
        """
        関数名 : __init__

        description:
            Latchクラスのコンストラクタ。

        Arguments:
            latch_element(xml.etree.ElementTree.Element) :

        Variables:
            self.latch_element(xml.etree.ElementTree.Element)    :
        
        Functions:
            self.input()            :
            self.output()           :
            self.type()             :
            self.clock()            :
            self.initial_state()    :
        
        Returns:

        """
        self.latch_element = latch_element
        self.input()
        self.output()
        self.type()
        self.clock()
        self.initial_state()
    




    def input(self):
        """
        関数名 : input

        description:
            ラッチの入力をinput属性へ格納する関数。

        Arguments:

        Variables:
            self.input(string)
        
        Functions
        
        Returns:

        """

        self.input = self.latch_element.find("input").text
    




    def output(self):
        """
        関数名 : output

        description:
            ラッチの出力をoutput属性へ格納する関数。

        Arguments:

        Variables:
            self.output(string)
        
        Functions
        
        Returns:

        """

        self.output = self.latch_element.find("output").text
    




    def type(self):
        """
        関数名 : type

        description:
            ラッチのタイプをtype属性へ格納する関数。
            タイプには{fe, re, ah, al, as}の5種類あり、それぞれ{"falling edge", "rising edge", "active high", "active low", "asynchronous"}を表している


        Arguments:

        Variables:
            self.type(string)
        
        Functions
        
        Returns:

        """

        ### 例外処理 ###
        try:

            self.type = self.latch_element.find("type").text
        
        except AttributeError:
            # latch要素内にtype要素が存在しない場合に発生
            # タイプが存在しない場合、空の文字列を代入
            self.type = ""
    




    def clock(self):
        """
        関数名 : clock

        description:
            ラッチのクロックをclock属性へ格納する関数。


        Arguments:

        Variables:
            self.clock(string)
        
        Functions
        
        Returns:

        """

        ### 例外処理 ###
        try:

            self.clock = self.latch_element.find("clock").text
        
        except AttributeError:
            # latch要素内にclock要素が存在しない場合に発生
            # クロックが存在しない場合、空の文字列を代入
            self.clock = ""
    




    def initial_state(self):
        """
        関数名 : initial_state

        description:
            ラッチの初期状態をinitial_state属性へ格納する関数。


        Arguments:

        Variables:
            self.initial_state(string) :
        
        Functions:
        
        Returns:

        """

        self.initial_state = self.latch_element.find("initial_state").text





class Buffer():
    """
    class名 : Buffer

    
    description:
        このクラスはサブジェクトグラフのバッファ情報(input, output)を表す

        
    Attributes:
        input(str)  :
        output(str) :


    Methods:
        __init__(self, buffer_element)  :
        input(self)                     :
        output(self)                    :


    Usages:
        #クラスのインスタンス化
        buffer = Buffer(buffer_element)

    """





    def __init__(self, buffer_element):
        """
        関数名 : __init__

        description:
            Bufferクラスのコンストラクタ。

        Arguments:
            buffer_element(xml.etree.ElementTree.Element) :

        Variables:
            self.buffer_element(xml.etree.ElementTree.Element)    :
        
        Functions:
            self.input()    :
            self.output()   :
        
        Returns:

        """

        self.buffer_element = buffer_element
        self.input()
        self.output()
    




    def input(self):
        """
        関数名 : input

        description:
            バッファの入力をinput属性へ格納する関数。

        Arguments:

        Variables:
            self.input(str)
        
        Functions
        
        Returns:

        """

        self.input = self.buffer_element.find("input").text
    




    def output(self):
        """
        関数名 : output

        description:
            バッファの出力をoutput属性へ格納する関数。

        Arguments:

        Variables:
            self.output(str)
        
        Functions
        
        Returns:

        """

        self.output = self.buffer_element.find("output").text










########################################################################################################################
#                                                                                                                      #
#      関数の定義                                                                                                       #
#                                                                                                                      #
#                                                                                                                      #
#       階層構造                                                                                                        #
#          ・main                                                                                                      #
#              |-----get_args                                                                                          #
#              |-----check_xml_files                                                                                   #
#              |-----build_graph_obj                                                                                   #
#              |             |-----subjectgraph_list                                                                   #
#              |             |-----separate_into_cell_and_patterngraph                                                 #
#              |              -----patterngraph_list                                                                   #
#              |                                                                                                       #
#              |-----set_pattern_priority                                                                              #
#              |                                                                                                       #
#              |-----graph_matching                                                                                    #
#              |              -----one_to_one_graph_matching                                                           #
#              |                                |-----node_id_list                                                     #
#              |                                 -----node_match                                                       #
#              |                                                                                                       #
#              |-----graph_select                                                                                      #
#              |                                                                                                       #
#               -----write_blif                                                                                        #
#          ・generate_list                                                                                             #
#          ・generate_list_cell_order                                                                                  # 
#                                                                                                                      #
########################################################################################################################







def main(argv):

    """
    関数名 : main

    description:
        main.pyのメイン関数

    Arguments:
        argv() : コマンドライン引数

    Variables:
        args():
        subjectgraph_dict():
        cell():
        patterngraph():
        match_result():
        pattern_priority():
        select_result():
        cell_netlist():
        log_file():

    Returns:
        
    """
    
    
    ### 1.コマンドライン引数の取得 ###

    # コマンドライン引数の0番の要素は「python」なので、1番以降の引数をgetArgs関数に渡す
    args = get_args(argv[1:])
    # file_name = get_file_name(args.subjectgraph_file)
    print("1")



    ### 2.グラフオブジェクトの構築 ###

    subjectgraph_dict, cell, patterngraph_dict = build_graph_obj(args.subjectgraph_file, args.patterngraph_file)
    print("2")
    #print(subjectgraph_dict)
    #print(patterngraph_dict)
    


    ### 3.グラフマッチング ###
    time_s = time.time()
    match_result = graph_matching(subjectgraph_dict, patterngraph_dict)
    if 'top' in match_result:
        subjectgraph_name = 'top'
    else:
        subjectgraph_name = next(iter(match_result))
    match_result_2 = match_result[subjectgraph_name]
    print("3")

    file_name = 'match_result_name.json'
    save_to_json(match_result_2, file_name)
    time_e = time.time()
    time_result = time_e - time_s
    print(time_result)
    
    
import json
def save_to_json(data, filename):
    # 辞書データをJSON形式でファイルに保存
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)



#####################################################################################################
#                                                                                                   #
#                              1.コマンドライン引数の取得                                             #
#                                                                                                   #
#####################################################################################################

def get_args(argv):
    parser = argparse.ArgumentParser(description="=========")
    parser.add_argument("subjectgraph_file",  help="-------")
    parser.add_argument("patterngraph_file",  help="-------")
    # parser.add_argument("-s", "--sat", action="store_true", help="-------")
    # parser.add_argument("-i", "--innerwire", type=int, choices=[0,1], default=0, help="-------")
    # parser.add_argument("-ps", "--print_stats", action="store_true", help="--------")
    return parser.parse_args(argv)





#####################################################################################################
#                                                                                                   #
#                              2.グラフオブジェクトの構築                                             #
#                                                                                                   #
#####################################################################################################

def build_graph_obj(xml_file_sg, xml_file_pg):
    """
    関数名 : build_graph_obj

    description:
        それぞれのオブジェクトの構築を行う関数。

    Arguments:
        xml_file_sg():
        xml_file_pg():

    Variables:
        xml_file_sg_ET()            :
        subjectgraph_dict()         :
        xml_file_pg_ET()            :
        cell_element()              :
        patterngraph_element_list() :
        cell()                      :
        patterngraph_dict()         :

    Returns:
        subjectgraph_dict() :
        cell()              :
        patterngraph_dict() :
        
    """
    
    ### サブジェクトグラフファイルの処理 ###
    xml_file_sg_ET = ET.parse(xml_file_sg)
    subjectgraph_dict = generate_subjectgraph_dict(xml_file_sg_ET)


    ### パターングラフファイルの処理 ###
    xml_file_pg_ET = ET.parse(xml_file_pg)
    cell_element, patterngraph_element_list = separate_into_cell_and_patterngraph(xml_file_pg_ET)
    cell = Cell(cell_element)
    patterngraph_dict = generate_patterngraph_dict(patterngraph_element_list, cell)

    return subjectgraph_dict, cell, patterngraph_dict
    




def generate_subjectgraph_dict(xml_file_sg):
    """
    関数名 : generate_subjectgraph_dict

    description:
        サブジェクトグラフの構築を行う関数。

    Arguments:
        xml_file_sg():

    Variables:
        subjectgraph_dict()     :
        root_element()          :
        child_element()         :
        tmp()                   :


    Returns:
        subjectgraph_dict() :
        
    """

    subjectgraph_dict = dict()

    root_element = xml_file_sg.getroot()

    for child_element in root_element:

        tmp = SubjectGraph(child_element)

        subjectgraph_dict[tmp.name] = tmp
    #print(subjectgraph_dict)
    return subjectgraph_dict





def separate_into_cell_and_patterngraph(xml_file_pg):
    """
    関数名 : separate_into_cell_and_patterngraph

    description:
        パターングラフファイルから論理セルとパターングラフを分ける関数。

    Arguments:
        xml_file_pg():

    Variables:
        root_element()              :
        cell_element()              :
        patterngraph_element_list() :

    Returns:
        cell_element() :
        patterngraph_element_list():
        
    """

    root_element = xml_file_pg.getroot()

    cell_element = root_element.find("cell")

    patterngraph_element_list = root_element.findall("patterngraph")

    return cell_element, patterngraph_element_list





def generate_patterngraph_dict(patterngraph_element_list, cell):
    """
    関数名 : generate_patterngraph_dict

    description:
        パターングラフファイルの構築を行う関数。

    Arguments:
        patterngraph_element_list():
        cell():

    Variables:
        patterngraph_dict():
        patterngraph_element():
        tmp():


    Returns:
        patterngraph_dict():
        
    """

    patterngraph_dict = dict()

    for patterngraph_element in patterngraph_element_list:

        tmp = PatternGraph(patterngraph_element, cell)

        patterngraph_dict[tmp.name] = tmp
    
    #print(patterngraph_dict)
    return patterngraph_dict





#####################################################################################################
#                                                                                                   #
#                              3.グラフマッチング                                                    #
#                                                                                                   #
#####################################################################################################

def graph_matching(subjectgraph_dict, patterngraph_dict):
    """
    関数名 : graph_matching

    description:
        サブジェクトグラフN個とパターングラフM個のグラフマッチングを行う関数。

    Arguments:
        subjectgraph_dict():
        patterngraph_dict():

    Variables:
        match_result():
        subjectgraph_obj():
        patterngraph_obj():

    Returns:
        match_result():
        
    """

    match_result = dict()

    for subjectgraph_obj in subjectgraph_dict.values():

        match_result[subjectgraph_obj.name] = dict()

        for patterngraph_obj in patterngraph_dict.values():

            match_result[subjectgraph_obj.name][patterngraph_obj.name] = one_to_one_graph_matching(subjectgraph_obj, patterngraph_obj)
    
    return match_result





def one_to_one_graph_matching(subjectgraph_obj, patterngraph_obj):
    """
    関数名 : one_to_one_graph_matching

    description:
        サブジェクトグラフ1個とパターングラフ1個のグラフマッチングを行う関数。

    Arguments:
        subjectgraph_obj():
        patterngraph_obj():

    Variables:
        one_to_one_match_result():
        subjectgraph():
        patterngraph():
        attr():
        default():
        op():
        local_node_match():
        digraph_matching():
        result_dict():
        sorted_result_list():
        tmp_list():
        left():
        right():


    Returns:
        one_to_one_match_result():
        
    """

    one_to_one_match_result = []

    subjectgraph = nx.DiGraph()
    subjectgraph.add_nodes_from(subjectgraph_obj.node_id_list)
    subjectgraph.add_edges_from(subjectgraph_obj.edge_list)
    nx.set_node_attributes(subjectgraph, subjectgraph_obj.node_dict)


    patterngraph = nx.DiGraph()
    patterngraph.add_nodes_from(patterngraph_obj.node_id_list)
    patterngraph.add_edges_from(patterngraph_obj.edge_list)
    nx.set_node_attributes(patterngraph, patterngraph_obj.node_dict)


    attr = ["type", "fanin_num", "fanout_num"]
    default = ["", 0, 0]
    op = [match_type, match_fanin_num, match_fanout_num]
    local_node_match = nx.algorithms.isomorphism.generic_node_match(attr, default, op)

    digraph_matching = nx.algorithms.isomorphism.DiGraphMatcher(subjectgraph, patterngraph, node_match=local_node_match)

    for result_dict in digraph_matching.subgraph_isomorphisms_iter():

        sorted_result_list = sorted(result_dict.items(), key = lambda k: k[1])

        tmp_list = []

        for left, right in sorted_result_list:

            tmp_list.append(left)

        one_to_one_match_result.append(tmp_list)
    
    return one_to_one_match_result





def match_type(data1, data2):
    """
    関数名 : match_type

    description:
        サブジェクトグラフの部分グラフのノードのタイプと、パターングラフのノードのタイプを比較する関数。
        return 0: ノードのタイプがマッチしていない場合
        return 1: 

    Arguments:
        data1():
        data2():

    Variables:

    Returns:
        data1==data2(bool):
        
    """
    return data1 == data2





def match_fanin_num(data1, data2):
    """
    関数名 : match_fanin_num

    description:
        サブジェクトグラフの部分グラフのノードのファンイン数と、パターングラフのノードのファンイン数を比較する関数。

    Arguments:
        data1():
        data2():

    Variables:

    Returns:
        data1==data2(bool):
        
    """
    return data1 == data2





def match_fanout_num(data1, data2):
    """
    関数名 : match_fanout_num

    description:
        サブジェクトグラフの部分グラフのノードのファンアウト数と、パターングラフのノードのファンアウト数を比較する関数。

    Arguments:
        data1():
        data2():

    Variables:

    Returns:
        data1<=data2(bool):
        
    """
    #print(data1)
    #print(data2)
    return data1 <= data2



#####################################################################################################
#                                                                                                   #
#                              4.グラフ選択                                                          #
#                                                                                                   #
#####################################################################################################


def set_pattern_priority(patterngraph_dict):

    pattern_priority = []
    
    tmp_dict = dict()

    for patterngraph_name in patterngraph_dict.keys():

        input_num = patterngraph_dict[patterngraph_name].get_input_num()

        node_num = patterngraph_dict[patterngraph_name].get_node_num()

        tmp_dict.setdefault(patterngraph_name, {"input_num":input_num, "node_num": node_num})
    
    tmp_list = sorted(tmp_dict.items(), key = lambda x: (x[1]["input_num"], x[1]["node_num"]) , reverse = True)


    for graph in tmp_list:

        pattern_priority.append(graph[0])

    return pattern_priority





def graph_select(subjectgraph_dict, matching_result, pattern_priority):
    
    select_result = dict()

    for subjectgraph_name in subjectgraph_dict.keys():

        select_result[subjectgraph_name] = dict()

        for patterngraph_name in pattern_priority:

            select_result[subjectgraph_name][patterngraph_name] = []

            one_to_one_graph_select(subjectgraph_dict[subjectgraph_name], matching_result[subjectgraph_name][patterngraph_name], select_result[subjectgraph_name][patterngraph_name])
    
    check_graph_select(subjectgraph_dict)
    
    return select_result





def one_to_one_graph_select(subjectgraph_obj, one_match_result, one_select_result):

    for candidate in one_match_result:

        flag_unused_node = check_unused_node(subjectgraph_obj, candidate)

        if flag_unused_node == False:

            continue

        one_select_result.append(candidate)

        remove_used_node(subjectgraph_obj, candidate)





def check_unused_node(subjectgraph_obj, candidate):

    flag_unused_node = True

    for candidate_node in candidate:

        if candidate_node not in subjectgraph_obj.node_id_list:

            flag_unused_node = False
        
    return flag_unused_node





def remove_used_node(subjectgraph_obj, candidate):

    for candidate_node in candidate:

        subjectgraph_obj.node_id_list.remove(candidate_node)





def check_graph_select(subjectgraph_dict):

    for subjectgraph_obj in subjectgraph_dict.values():

        if len(subjectgraph_obj.node_id_list) != 0:

            print("正しくグラフを選択できていません")
            print(subjectgraph_obj.node_id_list)
            exit()





#####################################################################################################
#                                                                                                   #
#                              5.セルベースのネットリストに変換                                       #
#                                                                                                   #
#####################################################################################################

def convert_cell_base_netlist(select_result, subjectgraph_dict, patterngraph_dict):

    cell_netlist = dict()

    for subjectgraph_name in subjectgraph_dict.keys():

        cell_netlist[subjectgraph_name] = dict()

        for patterngraph_name in patterngraph_dict.keys():

            cell_netlist[subjectgraph_name][patterngraph_name] = []

            convert_graph_to_cell(select_result[subjectgraph_name][patterngraph_name], cell_netlist[subjectgraph_name][patterngraph_name], subjectgraph_dict[subjectgraph_name], patterngraph_dict[patterngraph_name])
    
    return cell_netlist





def convert_graph_to_cell(partial_select_result, partial_cell_netlist, subjectgraph_obj, patterngraph_obj):

    for graph in partial_select_result:
        
        input_nodes_list = extract_input_nodes(graph, patterngraph_obj)

        output_nodes_list = extract_output_nodes(graph, patterngraph_obj)

        inner_edges = extra_inner_egdes(graph, subjectgraph_obj, patterngraph_obj)

        partial_cell_netlist.append(generate_io_cell(input_nodes_list, output_nodes_list, inner_edges, subjectgraph_obj))
    




def extract_input_nodes(graph, patterngraph_obj):
    
    retval_list = []

    for input_node in patterngraph_obj.input_list:

        if input_node != "N" and input_node != "T" and input_node != "F":

            input_node_id = int(input_node)

            index = 0

            for node_obj in patterngraph_obj.node_list:

                if node_obj.id == input_node_id:

                    break
                    
                index += 1

            retval_list.append(graph[index])
        
        else:

            retval_list.append(input_node)

    
    return retval_list





def extract_output_nodes(graph, patterngraph_obj):
    
    retval_list = []

    for output_node in patterngraph_obj.output_list:

        if output_node != "N" and output_node != "T" and output_node != "F":

            output_node_id = int(output_node)

            index = 0

            for node_obj in patterngraph_obj.node_list:

                if node_obj.id == output_node_id:

                    break
                    
                index += 1

            retval_list.append(graph[index])
        
        else:

            retval_list.append(output_node)
    
    return retval_list





def extra_inner_egdes(graph, subjectgraph_obj, patterngraph_obj):

    retval_list = []

    for start, stop in patterngraph_obj.edge_list:

        node_id = start

        index = 0

        for node_obj in patterngraph_obj.node_list:

            if node_obj.id == node_id:

                break
                    
            index += 1
            
        sg_node_id = graph[index]

        retval_list.append(subjectgraph_obj.node_list[sg_node_id-1].output)
    
    return retval_list





def generate_io_cell(input_nodes_list, output_nodes_list, inner_edges, subjectgraph_obj):


    input_nodes = [""] * len(input_nodes_list)

    twice_node_dict = find_twice_node(input_nodes_list)

    for twice_node in twice_node_dict.keys():

        real_edge_name_list = subjectgraph_obj.node_list[int(twice_node)-1].input_list

        for i in range(2):

            index = twice_node_dict[twice_node][i]

            input_nodes[index] = real_edge_name_list[i]


    index = 0

    for input_node in input_nodes_list:

        if input_nodes[index] != "":

            index += 1
            continue
        
        if input_node == "N":

            input_nodes[index] = "N"

        elif input_node == "T":

            input_nodes[index] = "$true"
        
        elif input_node == "F":

            input_nodes[index] = "$false"

        else:

            real_edge_name_list = subjectgraph_obj.node_list[int(input_node)-1].input_list

            for input_name in real_edge_name_list:

                if (input_name not in inner_edges):

                    input_nodes[index] = input_name
                    break

        index += 1
    

    output_nodes = []

    for output_node in output_nodes_list:

        if output_node == "N":

            output_nodes.append("N")
        
        elif output_node == "T":

            output_nodes.append("$true")
        
        elif output_node == "F":

            output_nodes.append("false")
        
        else:

            output_nodes.append(subjectgraph_obj.node_list[int(output_node)-1].output)

    return input_nodes + output_nodes





def find_twice_node(input_node_list):

    retval_dict = dict()

    for i in range(len(input_node_list)):

        if((input_node_list[i]=="N") or (input_node_list[i]=="T") or (input_node_list[i]=="F")):

            continue

        for j in range(i+1, len(input_node_list)):

            if input_node_list[i] == input_node_list[j]:
                retval_dict[input_node_list[i]] = [i,j]
    
    return retval_dict





#####################################################################################################
#                                                                                                   #
#                              6.extended BLIF形式で出力                                             #
#                                                                                                   #
#####################################################################################################
def write_blif(cell_netlist, subjectgraph_obj, cell_obj, patterngraph_obj):
    
    blif_file_name = "mapped_for_equivalent.blif"

    blif_file = open(blif_file_name, mode="w", encoding='UTF-8')

    
    for subjectgraph_name in subjectgraph_obj.keys():


        blif_file.write(".model {}\n".format(subjectgraph_name))


        blif_file.write(".inputs")
        for input in subjectgraph_obj[subjectgraph_name].input_list:
            blif_file.write(" {}".format(input))
        blif_file.write("\n")


        blif_file.write(".outputs")
        for output in subjectgraph_obj[subjectgraph_name].output_list:
            blif_file.write(" {}".format(output))
        blif_file.write("\n")


        blif_file.write(".names $false\n")
        blif_file.write(".names $true\n")
        blif_file.write("1\n")
        blif_file.write(".names $undef\n")


        for patterngraph_name in cell_netlist[subjectgraph_name].keys():

            for cell in cell_netlist[subjectgraph_name][patterngraph_name]:

                # blif_file.write(".subckt cell_{}".format(patterngraph_name))
                blif_file.write(".subckt PG_{}".format(patterngraph_obj[patterngraph_name].configuration_memory))

                for index in range(len(cell)):

                    if cell[index] == "N":

                        # blif_file.write(" {0}=$false".format(cell_obj.io_list[index]))
                        pass

                    else:

                        blif_file.write(" {0}={1}".format(cell_obj.io_list[index], cell[index]))
                
                blif_file.write("\n")
        

        for subckt_obj in subjectgraph_obj[subjectgraph_name].subckt_list:

            blif_file.write(".subckt {}".format(subckt_obj.name))

            for ioput in subckt_obj.ioput_dict.keys():

                blif_file.write(" {}={}".format(ioput, subckt_obj.ioput_dict[ioput]))
            
            blif_file.write("\n")
        

        for latch_obj in subjectgraph_obj[subjectgraph_name].latch_list:

            if len(latch_obj.clock) == 0:

                blif_file.write(".latch {0} {1} {2}\n".format(latch_obj.output, latch_obj.input, latch_obj.initial_state))
            
            else:

                blif_file.write(".latch {0} {1} {2} {3} {4}\n".format(latch_obj.output, latch_obj.input, latch_obj.type, latch_obj.clock, latch_obj.initial_state))

        for buffer_obj in subjectgraph_obj[subjectgraph_name].buffer_list:

            blif_file.write(".names {0} {1}\n".format(buffer_obj.input, buffer_obj.output))
            blif_file.write("1 1\n")

        blif_file.write(".end\n\n\n")


    
    blif_file.close()


def write_eblif(cell_netlist, subjectgraph_obj, cell_obj, patterngraph_obj):
    
    blif_file_name = "mapped.eblif"
    
    blif_file = open(blif_file_name, mode="w", encoding='UTF-8')

    for subjectgraph_name in subjectgraph_obj.keys():


        blif_file.write(".model {}\n".format(subjectgraph_name))


        blif_file.write(".inputs")
        for input in subjectgraph_obj[subjectgraph_name].input_list:
            blif_file.write(" {}".format(input))
        blif_file.write("\n")


        blif_file.write(".outputs")
        for output in subjectgraph_obj[subjectgraph_name].output_list:
            blif_file.write(" {}".format(output))
        blif_file.write("\n")


        blif_file.write(".names $false\n")
        blif_file.write(".names $true\n")
        blif_file.write("1\n")
        blif_file.write(".names $undef\n")


        for patterngraph_name in cell_netlist[subjectgraph_name].keys():

            for cell in cell_netlist[subjectgraph_name][patterngraph_name]:

                # blif_file.write(".subckt cell_{}".format(patterngraph_name))
                blif_file.write(".subckt cell")

                for index in range(len(cell)):

                    if cell[index] == "N":

                        # blif_file.write(" {0}=$false".format(cell_obj.io_list[index]))
                        pass

                    else:

                        blif_file.write(" {0} = {1}".format(cell_obj.io_list[index], cell[index]))
                
                blif_file.write("\n")

                blif_file.write(".param MODE {}\n".format(patterngraph_obj[patterngraph_name].configuration_memory))
        

        for subckt_obj in subjectgraph_obj[subjectgraph_name].subckt_list:

            blif_file.write(".subckt {}".format(subckt_obj.name))

            for ioput in subckt_obj.ioput_dict.keys():

                blif_file.write(" {} = {}".format(ioput, subckt_obj.ioput_dict[ioput]))
            
            blif_file.write("\n")
        

        for latch_obj in subjectgraph_obj[subjectgraph_name].latch_list:

            if len(latch_obj.clock) == 0:

                blif_file.write(".latch {0} {1} {2}\n".format(latch_obj.output, latch_obj.input, latch_obj.initial_state))
            
            else:

                blif_file.write(".latch {0} {1} {2} {3} {4}\n".format(latch_obj.output, latch_obj.input, latch_obj.type, latch_obj.clock, latch_obj.initial_state))

        for buffer_obj in subjectgraph_obj[subjectgraph_name].buffer_list:

            print(buffer_obj.input)

            blif_file.write(".conn {0} {1}\n".format(buffer_obj.input, buffer_obj.output))


        blif_file.write(".end\n\n\n")


    
    blif_file.close()





#####################################################################################################
#                                                                                                   #
#                              6.Verilog形式で出力                                                   #
#                                                                                                   #
#####################################################################################################

# def write_verilog(cell_netlist, subjectgraph_obj, cell_obj):

#     verilog_file = open("mapped.v", "w", encoding="UTF-8")

#     for subjectgraph_name in subjectgraph_obj.keys():

#         verilog_file.write("module {}(\n".format(subjectgraph_name))

#         for input in subjectgraph_obj[subjectgraph_name].input_list:
#             verilog_file.write("\tinput wire {},\n".format(input))
        
#         for output in subjectgraph_obj[subjectgraph_name].output_list:
#             if subjectgraph_obj.output_list[-1] != output:
#                 verilog_file.write("\toutput wire {},\n".format(output))
#             else:
#                 verilog_file.write("\toutput wire {}\n".format(output))
        
#         verilog_file.write(");\n\n")

#         # inner_edgeの作成
#         inner_edges = []
#         for patterbgraph_name in cell_netlist[subjectgraph_name].keys():
#             for cell in cell_netlist[subjectgraph_name][patterbgraph_name]:
#                 for edge_name in cell:
#                     if edge_name != "N" and edge_name not in subjectgraph_obj[subjectgraph_name].input_list and edge_name not in subjectgraph_obj[subjectgraph_name].output_list and edge_name not in inner_edges:
#                         inner_edges.append(edge_name)
#         for subckt_obj in subjectgraph_obj[subjectgraph_name].subckt_list:
#             for ioput in subckt_obj.ioput_dict.keys():
#                 if ioput not in subjectgraph_obj[subjectgraph_name].input_list and ioput not in subjectgraph_obj[subjectgraph_name].output_list and ioput not in inner_edges:
#                     inner_edges.append(ioput)
#         for latch_obj in subckt_obj[subjectgraph_name].latch_list:
#             if latch_obj.input not in subjectgraph_obj[subjectgraph_name].input_list and latch_obj.input not in subjectgraph_obj[subjectgraph_name].output_list and latch_obj.input not in inner_edges:
#                 inner_edges.append(latch_obj.input)
#             if latch_obj.output not in subjectgraph_obj[subjectgraph_name].input_list and latch_obj.output not in subjectgraph_obj[subjectgraph_name].output_list and latch_obj.output not in inner_edges:
#                 inner_edges.append(latch_obj.output)
        
#         # wireの書き込み
#         for inner_edge in inner_edges:
#             verilog_file.write("wire {};\n".format(inner_edge))
        
#         verilog_file.write("\n")

#         # regの書き込み
#         reg_number = 0
#         for latch_obj in subjectgraph_obj[subjectgraph_name].latch_list:
#             if latch_obj.initial_state == "0":
#                 verilog_file.write("reg r{0} = 1'b0;\n".format(reg_number))
#             elif latch_obj.initial_state == "1":
#                 verilog_file.write("reg r{0} = 1'b1;\n".format(reg_number))
#             elif latch_obj.initial_state == "2" or latch_obj.initial_state == "3":
#                 verilog_file.write("reg r{0};\n".format(reg_number))
#             reg_number += 1
        
#         verilog_file.write("\n")

#         cell_number = 0
#         for patterngraph_name in cell_netlist[subjectgraph_name].keys():
#             configuration_bit = patterngraph_name[8:]
#             configuration_bit = configuration_bit.replace("-", "0")
#             for cell in cell_netlist[subjectgraph_name][patterngraph_name]:
#                 verilog_file.write("m_pea #(.MODE(8'b{0})) _{1}_ ()\n".format(configuration_bit, cell_number))
#                 for index in range(len(cell)):
#                     if cell[index] != "N":
#                         if len(cell)-1 != index:
#                             verilog_file.write("\t.{0}({1}),\n".format(cell_obj.io_list[index], cell[index]))
#                         else:
#                             verilog_file.write("\t.{0}({1})\n".format(cell_obj.io_list[index], cell[index]))
#                 verilog_file.write(");\n\n")
#                 cell_number += 1
        
#         subckt_number = 0
#         for subckt_obj in subjectgraph_obj[subjectgraph_name].subckt_list:
#             verilog_file.write("{0} subckt{1} (\n".format(subckt_obj.name, subckt_number))
#             ioput_length = len(subckt_obj.ioput_dict.keys())-1
#             loop_num = 0
#             for ioput in subckt_obj.ioput_dict.keys():
#                 if ioput_length != loop_num:
#                     verilog_file.write("\t.{0}({1}),\n".format(ioput, subckt_obj.ioput_list[ioput]))
#                 else:
#                     verilog_file.write("\t.{0}({1})\n".format(ioput, subckt_obj.ioput_list[ioput]))
#             verilog_file.write(");\n")
#             subckt_number += 1
        
#         verilog_file.write("\n")

#         reg_number = 0
#         for latch_obj in subckt_obj[subjectgraph_name].latch_list:
#             if latch_obj.type == "re":
#                 verilog_file.write("always @(posedge)")

        








#####################################################################################################
#                                                                                                   #
#                                    logファイル関連                                                 #
#                                                                                                   #
#####################################################################################################

def get_file_name(file_path):

    folder_and_file_list = re.split("[/\\]", file_path)

    file_name_with_extension = folder_and_file_list[-1]

    name_and_extension_list = re.split("[.]", file_name_with_extension)

    return name_and_extension_list[0]





def write_base_info_to_log(log_file, subjectgraph_dict, patterngraph_dict, match_result, select_result, cell_netlist, pattern_priority):

    dt_now = datetime.datetime.now()
    log_file.write("作成時間 : {}".format(dt_now))
    log_file.write("\n\n")


    log_file.write("パターンマッチングを用いたテクノロジーマッピング\n\n")


    log_file.write("・サブジェクトグラフの名前一覧\n")
    
    column = 0
    column_max = 4
    for subjectgraph_name in subjectgraph_dict.keys():
        if column == column_max:
            log_file.write("\t")
            log_file.write(subjectgraph_name)
            log_file.write("\n")
            column = 0
        else:
            log_file.write("\t")
            log_file.write(subjectgraph_name)
            column += 1
    log_file.write("\n")
    
    log_file.write("\n\n")
    log_file.write("・パターングラフの名前一覧\n")
    
    column = 0
    column_max = 4
    for patterngraph_name in patterngraph_dict.keys():
        if column == column_max:
            log_file.write("\t")
            log_file.write(patterngraph_name)
            log_file.write("\n")
            column = 0
        else:
            log_file.write("\t")
            log_file.write(patterngraph_name)
            column += 1
    log_file.write("\n")

    log_file.write("\n\n")
    log_file.write("・パターンマッチング結果\n\n")
    first_flag = False
    for subjectgraph_name in subjectgraph_dict.keys():
        for patterngraph_name in patterngraph_dict.keys():
            if len(match_result[subjectgraph_name][patterngraph_name]) != 0:
                log_file.write("Subject Graph : {} , Pattern Graph : {}\n".format(subjectgraph_name, patterngraph_name))
                for one_to_one_match_result in match_result[subjectgraph_name][patterngraph_name]:
                    log_file.write("[")
                    for node in one_to_one_match_result:
                        if first_flag == False:
                            log_file.write("{}".format(node))
                            first_flag = True
                        else:
                            log_file.write(",{}".format(node))
                    log_file.write("]")
                    log_file.write("\n")
                    first_flag = False
    
    log_file.write("\n\n")
    log_file.write("・グラフ選択結果\n\n")
    first_flag = False
    for subjectgraph_name in subjectgraph_dict.keys():
        for patterngraph_name in patterngraph_dict.keys():
            if len(select_result[subjectgraph_name][patterngraph_name]) != 0:
                log_file.write("Subject Graph : {} , Pattern Graph : {}\n".format(subjectgraph_name, patterngraph_name))
                for one_to_one_select_result in select_result[subjectgraph_name][patterngraph_name]:
                    log_file.write("[")
                    for node in one_to_one_select_result:
                        if first_flag == False:
                            log_file.write("{}".format(node))
                            first_flag = True
                        else:
                            log_file.write(",{}".format(node))
                    log_file.write("]")
                    log_file.write("\n")
                    first_flag = False
    
    log_file.write("\n\n")
    log_file.write("・セルベースのネットリスト\n\n")
    first_flag = False
    for subjectgraph_name in subjectgraph_dict.keys():
        for patterngraph_name in patterngraph_dict.keys():
            if len(cell_netlist[subjectgraph_name][patterngraph_name]) != 0:
                log_file.write("Subject Graph : {} , Pattern Graph : {}\n".format(subjectgraph_name, patterngraph_name))
                for one_to_one_cell_netlist in cell_netlist[subjectgraph_name][patterngraph_name]:
                    log_file.write("[")
                    for node in one_to_one_cell_netlist:
                        if first_flag == False:
                            log_file.write("{}".format(node))
                            first_flag = True
                        else:
                            log_file.write(",{}".format(node))
                    log_file.write("]")
                    log_file.write("\n")
                    first_flag = False
    
    log_file.write("\n\n")
    log_file.write("・パターングラフの優先度\n\n")
    
    for patterngraph_name in pattern_priority:
        log_file.write(patterngraph_name)
        log_file.write("\n")






#####################################################################################################
#                                                                                                   #
#                                         class関連                                                 #
#                                                                                                   #
#####################################################################################################

def generate_list(parent_element, child_element_name):

    """
    関数名 : generate_list

    description:
        

    Arguments:
        parent_element():
        child_element_name(str):

    
    Variables:
        retval_list(list):
        child_element():
        grandchild_elemnt():

        
    Returns:
        retval_list(list):

    """

    retval_list = []

    child_element = parent_element.find(child_element_name)

    for grandchild_element in child_element:

        retval_list.append(grandchild_element.text)
    
    return retval_list





def generate_list_cell_order(parent_element, child_element_name, grandchild_element_name, cell_io_list, cell_io_name):

    retval_list = []

    child_element = parent_element.find(child_element_name)

    grandchild_element_list = child_element.findall(grandchild_element_name)

    for cell_io in cell_io_list:

        for grandchild_element in grandchild_element_list:

            if grandchild_element.attrib[cell_io_name] == cell_io:

                retval_list.append(grandchild_element.text)
    
    return retval_list


########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                        追加した関数                                                                    #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################
#ファイルを読み込み、辞書配列に変換する
def text_to_dict(text):
    # eval関数を使って文字列をPythonのリストや辞書に変換
    result_dict = eval(text)
    return result_dict
#
#　マッチ結果の光学異性体を除去する関数
#
def remove_duplicates(data):
    result = {}
    for key, values in data.items():
        unique_values = []
        for value in values:
            if value not in unique_values:
                
                is_unique = True
                for unique_value in unique_values:
                    if sorted(value) == sorted(unique_value):
                        is_unique = False
                        break
                if is_unique:
                    unique_values.append(value)
        if unique_values:
            result[key] = unique_values
    return result
#
#　ファイルを書き出す関数
#
def write_dict_to_file(result, out_file):
    with open(out_file, 'w') as file:
        for key, values in result.items():
            for value in values:
                file.write(f"{key}:{value}\n")
#
#  ノード数のカウント
#
def find_overall_min_max_value(data):
    min_value = float('inf')  # 最小値を格納する変数を初期化し、正の無限大で設定します。
    max_value = float('-inf')  # 最大値を格納する変数を初期化し、負の無限大で設定します。

    for values_list in data.values():
        for values in values_list:
            if values:  # リストが空でない場合のみ最小値と最大値を更新
                min_in_values = min(values)
                max_in_values = max(values)
                min_value = min(min_value, min_in_values)
                max_value = max(max_value, max_in_values)

    return min_value, max_value
#
# ノードの評価を行う関数
#
def count_occurrences(data, output_file):
    occurrences = {}  # 数字ごとの出現回数を記録する辞書

    # 各キーと値の組み合わせをループで処理
    for key, values_list in data.items():
        for values in values_list:
            for value in values:
                if value in occurrences:
                    occurrences[value] += 1
                else:
                    occurrences[value] = 1

    # 結果をテキストファイルに書き込む
    with open(output_file, 'w') as file:
        for number, count in occurrences.items():
            file.write(f"{number}:{count}\n")

    return occurrences
#
#　マッチ結果の評価を行う関数
#
def restore_values(data, occurrences):
    restored_data = {}
    min_restored_data = {}
    # データの各キーと値をループで処理
    for key, values_list in data.items():
        restored_values_list = []  # 復元された値を格納するリスト
        min_restored_values_list = []
        # データの各リストに含まれる数字を復元してリストに追加
        for values in values_list:
            restored_values = [occurrences[value] for value in values]
            min_restored_values = [min([occurrences[value] for value in values])]
            restored_values_list.append(restored_values)
            min_restored_values_list.append(min_restored_values)
        restored_data[key] = restored_values_list
        min_restored_data[key] = min_restored_values_list
    return restored_data, min_restored_data

#
# マッチ結果の選択
#
def select(data, min_pg_score, n, m):
    all_num = set(range(n, m)) #集めたい数字
    select_num = [] #集めた数字を格納するlist
    select_pg = {} #選択したPG、listの情報を格納
    i = 1
    j = 0 # jで論理セル数のカウント

    for score_key, score_outer_list in min_pg_score.items():
        select_pg[score_key] = []

    while set(select_num) != all_num:
    # i == score_inner_list[0]を満たすものをselect_targetに格納
        select_target = {}
        for score_key , score_outer_list in min_pg_score.items():
            for index , score_inner_list in enumerate(score_outer_list):
                #print(score_inner_list)
                if i == score_inner_list[0] and not set(select_num).intersection(set(data[score_key][index])):
                    if score_key not in select_target:
                        select_target[score_key] = []
                    select_target[score_key].append(data[score_key][index])
            
        #print(select_target)

        # select_targetから条件に従って選んでいく
        while select_target:
            longest_target = None
            longest_length = 0
            longest_pg = None
            longest_index = None

            # ここでlistの長さが最も長いものを探索する
            for target_key , target_outer_list in select_target.items():
                for index, target_inner_list in enumerate(target_outer_list):
                    if len(target_inner_list) > longest_length:
                        longest_target = target_inner_list
                        longest_length = len(target_inner_list)
                        longest_pg = target_key
                        longest_index = index
            
            if longest_target is None:
                break  # 最も長い対象がない場合、ループを抜ける
        
            #print(f"最も長いもの{longest_pg}:{longest_target}")

            # 最も長い物は選べるのかの判定
            if longest_target and not set(select_num).intersection(set(longest_target)):
                select_num.extend(longest_target)
                #print("選ばれたもの",select_num)
                j = j + 1
                if longest_pg not in select_pg:
                    select_pg[longest_pg] = []
                select_pg[longest_pg].append(longest_target)
                select_target[longest_pg].remove(longest_target)
                if not select_target[longest_pg]:
                    del select_target[longest_pg]
                #print(select_pg)
                    
            else:
                del select_target[longest_pg][longest_index]
                #print("not select")
        
        if not select_target:
            i = i + 1

    return select_num, select_pg, j

########################################################################################################################


#####################################################################################################
#                                                                                                   #
#                                if __name__=="__main__"                                            #
#                                                                                                   #
#####################################################################################################

if __name__ == "__main__":
    main(sys.argv)