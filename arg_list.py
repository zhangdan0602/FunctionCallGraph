#!/usr/bin/python
#coding=utf-8
from py2neo import Graph,Node,Relationship,NodeSelector
graph = Graph("http://localhost:7474", username="neo4j", password="123456")
graph.delete_all()
import  re
import sys
global oldclist
global func_setfun,func_setun,n,node_1_call_node2,list_node,list_attr_one,list_attr_last
list_attr_last={}
list_attr_one={}
list_node={}
selector=NodeSelector(graph)
func_setfun=[]
func_setun=[]
class callGraph():
    def __init__(self):
        self.node_neighbors ={}
        self.node_in={}
        self.temp=0
        self.ini_n=Node()
    def getFlist(self):
        oldclist=""
        print(sys.argv[1])
        print(sys.argv[2])
        f = open(sys.argv[1], "r+")
        open(sys.argv[2], 'w').write(re.sub(r'\w+\.\w\:\w+|{|}', '', f.read()))
        f = open(sys.argv[2])
        lines = f.readlines()
        for fline in lines:
            if fline.startswith('F'):
                flist = fline.split(' ')[1]
                oldclist = oldclist + " " + flist
        for i in oldclist.split(' ')[1:]:
            func_setfun.append(i)
        for cline in lines:
            if cline.startswith('C'):
                clist1 = cline.split('  ')[1].strip()
                if clist1 not in func_setfun:
                    func_setun.append(clist1)
        print(func_setfun)
    def add_node_in_value(self,node):
        key,value=node
        #print(key)
        self.node_in.setdefault(key,[]).append(value)
        #节点中有key
        if selector.select(key).first() is None:
            for i in range(len(list_node)):
                if key in list_node.get(i).labels():
                    self.temp = i
            graph.create(list_node[self.temp])
            list_node[self.temp]['name'] = key
            graph.push(list_node[self.temp])
            list_attr_one[self.temp].append(self.node_in[key])
            list_node[self.temp]['attr']=list_attr_one[self.temp]
            graph.push(list_node[self.temp])
        else:
            for i in range(len(list_node)):
                if key in list_node.get(i).labels():
                    self.temp = i
            list_attr_one[self.temp].append(self.node_in[key])
            j=len(list_attr_one[self.temp])-1
            list_node[self.temp]['attr'] = list_attr_one[self.temp][j - 1]
            graph.push(list_node[self.temp])
        print(list_node[self.temp])

    def add_edge(self, edge):
        u,v=edge
        self.node_neighbors.setdefault(u, []).append(v)
        #查找u对应的节点的num
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

        if not graph.match_one(start_node=selector.select(u).first(),end_node=selector.select(v).first(),bidirectional=False):
            node_1_call_node2=Relationship(selector.select(u).first(), 'call', selector.select(v).first())
            graph.create(node_1_call_node2)
            print(node_1_call_node2)
        print(self.node_neighbors)

    def initial(self):
        l = list(func_setfun)
        for i in range(len(func_setfun)):
            list_attr_one[i] = []
            list_attr_last[i] = []
            self.ini_n.add_label(l[i])
            list_node[i] = self.ini_n
            self.ini_n = Node()
        print(list_node)
    def getFcg(self):
        f = open(sys.argv[2])
        lines = f.readlines()
        for cline in lines:
            if cline.startswith('C'):
                clist1 = cline.split(' ')[1]
                clist2 = cline.split('  ')[1].strip()
                if (clist1 in func_setfun) and (clist2 in func_setun):
                    cg.add_node_in_value((clist1, clist2))
                if (clist1 in func_setfun) and (clist2 in func_setfun):
                    cg.add_edge((clist1, clist2))

if __name__ == '__main__':
    cg=callGraph()
    cg.getFlist()
    cg.initial()
    cg.getFcg()


