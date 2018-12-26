#!/usr/bin/python
#coding=utf-8
#在文件中写注释，注明coding=utf-8
from py2neo import Graph,Node,Relationship,NodeSelector
#先启动neo4j console；接着运行fcg
graph = Graph("http://localhost:7474", username="neo4j", password="123456")
#图置为空
graph.delete_all()
import os
import re
import sys
#定义全局变量
global oldclist
global func_setfun,func_setun,n,node_1_call_node2,list_node,list_attr_one,list_attr_last
list_attr_last={}
list_attr_one={}
list_node={}
#选择器
selector=NodeSelector(graph)
func_setfun=[]
func_setun=[]

#只处理自定义函数的调用图，不处理库函数；自定义函数的属性为库函数；

class callGraph():
    def __init__(self):
        self.node_neighbors ={}
        self.node_in={}
        self.temp=0
        self.ini_n=Node()

    #得到函数【自定义／库】集合
    def getFlist(self):
        oldclist=""

		#想自定义文件位置，使用sys.argv[1] sys.argv[2]
		#/Users/Zd/Desktop/ass2.c.cdepn /Users/Zd/Desktop/ass2.c.cdepn2
        #print(sys.argv[1])
        #print(sys.argv[2])


		#1.codeviz+gcc编译.c文件生成.c.cdepn
        input_file = open(os.getcwd()+"/data/"+"ass2.c.cdepn", "r+")

		#可以不用提前建cdepn2文件，直接指明就可以
		#2.python处理.c.cdepn文件，只留下函数名，包括自定义和库文件的
        output_file = open(os.getcwd()+"/data/"+"ass2.c.cdepn2", 'w').write(re.sub(r'\w+\.\w\:\w+|{|}', '', input_file.read()))

        f = open(os.getcwd()+"/data/"+"ass2.c.cdepn2")
        lines = f.readlines()
        for fline in lines:
			#F：函数
            if fline.startswith('F'):
				#截取 函数名
                flist = fline.split(' ')[1]
                oldclist = oldclist + " " + flist
        for i in oldclist.split(' ')[1:]:
			#自定义的函数放入 func_setfun
            func_setfun.append(i)
        for cline in lines:
			# C：调用
            if cline.startswith('C'):
                clist1 = cline.split('  ')[1].strip()
                if clist1 not in func_setfun:
					#在call中得到的函数，不在自定义的函数中即库函数的放入 func_setun
                    func_setun.append(clist1)
        #print(func_setfun)


    #给节点添加属性，属性就是库函数
    def add_node_in_value(self,node):
        #node =（节点名和属性）
        key,value=node
        #print(key)
        # key拼接value【属性】
        self.node_in.setdefault(key,[]).append(value)
        #判断是否有该节点
        if selector.select(key).first() is None:
            for i in range(len(list_node)):
                #判断节点中是否有key
                if key in list_node.get(i).labels():
                    #获取到位置
                    self.temp = i
            #没有该节点，则graph中创建
            graph.create(list_node[self.temp])
            #节点的名称name
            list_node[self.temp]['name'] = key
            #修改节点的值
            graph.push(list_node[self.temp])

            #节点属性集合中拼接上value【属性】
            list_attr_one[self.temp].append(self.node_in[key])
            #节点的属性attr=函数的参数
            list_node[self.temp]['attr']=list_attr_one[self.temp]
            # 修改节点的值
            graph.push(list_node[self.temp])
        else:
            # 同样获取到位置
            for i in range(len(list_node)):
                if key in list_node.get(i).labels():
                    self.temp = i
            #已经有该节点，属性集合中拼接上value【属性】
            list_attr_one[self.temp].append(self.node_in[key])
            j=len(list_attr_one[self.temp])-1
            #节点的属性attr【即刚才拼接的value【传过来的库函数】】
            list_node[self.temp]['attr'] = list_attr_one[self.temp][j - 1]
            #修改节点的值
            graph.push(list_node[self.temp])
        print(list_node[self.temp])

    # 添加边【自定义函数之间】
    def add_edge(self, edge):
        u,v=edge
        #同样设置key、value
        self.node_neighbors.setdefault(u, []).append(v)
        #查找u对应的节点的num
        #类似于给节点添加属性
        #先判断是否存在两个点，不存在就创建
        if selector.select(u).first() is None:
            for i in range(len(list_node)):
                if u in list_node.get(i).labels():
                    self.temp = i
            graph.create(list_node[self.temp])
            list_node[self.temp]['name'] = u
            graph.push(list_node[self.temp])
        if selector.select(v).first() is None:
            for i in range(len(list_node)):
                if v in list_node.get(i).labels():
                    self.temp = i
                    print(self.temp)
            graph.create(list_node[self.temp])
            list_node[self.temp]['name'] = v
            graph.push(list_node[self.temp])
        print(list_node[self.temp])
        #判断是否有该属性 match_one()。
        if not graph.match_one(start_node=selector.select(u).first(),end_node=selector.select(v).first(),bidirectional=False):
            #不存在匹配关系，就添加call
            node_1_call_node2=Relationship(selector.select(u).first(), 'call', selector.select(v).first())
            #创建关系
            graph.create(node_1_call_node2)
            print(node_1_call_node2)
        print(self.node_neighbors)


    #初始化节点
    def initial(self):
        #自定义函数，每个函数为一个节点
        l = list(func_setfun)
        for i in range(len(func_setfun)):
            #每个节点的属性和之前属性为空
            list_attr_one[i] = []
            list_attr_last[i] = []
            #为每个节点添加标签【自定义函数名】
            self.ini_n.add_label(l[i])
            #自定义函数组成的集合中，依次放入一个Node
            list_node[i] = self.ini_n
            #再次调用时，需再次置为Node类型【每个函数为一个Node】
            self.ini_n = Node()
        # 自定义函数组成的集合
        print(list_node)

    #得到函数调用图【会调用节点添加属性、添加关系的方法】
    def getFcg(self):
        f = open(os.getcwd()+"/data/"+"ass2.c.cdepn2")
        lines = f.readlines()
        for cline in lines:
            if cline.startswith('C'):
                #遍历每行，得到两个函数名
                clist1 = cline.split(' ')[1]
                clist2 = cline.split('  ')[1].strip()
                #如果一个函数在自定义，另一个函数为库函数，则将库函数作为自定义函数的属性
                if (clist1 in func_setfun) and (clist2 in func_setun):
                    cg.add_node_in_value((clist1, clist2))
                # 如果两个函数都为自定义，则生成调用关系【添加边】
                if (clist1 in func_setfun) and (clist2 in func_setfun):
                    cg.add_edge((clist1, clist2))

if __name__ == '__main__':
    cg=callGraph()
    #调用生成函数集合的方法
    cg.getFlist()
    #调用初始化节点集合的方法
    cg.initial()
    #调用生成函数调用图的方法
    cg.getFcg()


