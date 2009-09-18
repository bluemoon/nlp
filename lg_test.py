from collections import deque
import os
import sys
import pprint
import inspect
import glob
import time


## pretty graphs
import networkx as nx
import matplotlib.pyplot as plt

import lg_fsm as lgFSM
import linkGrammar

from structures.fsm import FSM
from utils.list import list_functions

#from nltk.sem import logic
START_TIME = time.time()


### RELATIONSHIPS:
###   Wd(left, x) & Ss(y, z) & (x & y) -> subject(z, y)
###   TO(x, y) -> todo(x, y)
###   O(x, y) -> object(x, y)
###   Wi(x, y) -> imperative(x, y)


def debug(obj, prefix=None):
    #pprint(inspect.getmembers(obj))
    #frame = inspect.currentframe()
    #with_caller = '[%s:%s:%d] %s'
    #without_caller = '[%s:%d] %s'

    caller_module = inspect.stack()[1][1]
    caller_method = inspect.stack()[1][3]
    from_line     = inspect.stack()[1][2]
    #if not LastDebugged or LastDebugged != caller_method:
    #    print '--> [func:%s]' % caller_method
    #else:
    #    print '[line:%d] %s' % (caller_method, from_line, repr(obj))
    d_time = time.time() - START_TIME
    if not prefix:
        print '[%f:%s-%d]: ' % (d_time, caller_method, from_line),
        pprint.pprint(obj)
    else:
        print '[%f:%s-%d] %s: ' % (d_time, caller_method, from_line, prefix),
        pprint.pprint(obj)


class grammarFSM:
    def fsm_setup(self):
        self.fsm = FSM('INIT', [])
        self.fsm.set_default_transition(lgFSM.Error, 'INIT')
        self.fsm.add_transition_any('INIT', None, 'INIT')
        self.fsm.add_transition('RW', 'INIT', lgFSM.Root)
        self.fsm.add_transition('Xp', 'INIT', lgFSM.Period)
        self.fsm.add_transition('Wd', 'INIT', lgFSM.Declarative, 'DECL')
        self.fsm.add_transition('Wd', 'DECL', lgFSM.Declarative, 'DECL')
        self.fsm.add_transition('Ss', 'DECL', lgFSM.Subject, 'INIT')
        self.fsm.add_transition('AF', 'DECL', lgFSM.Object, 'INIT')
        
        
    def fsm_run(self, input):
        print input
        return self.fsm.process_list(input)

class Grammar:
    def __init__(self):
        self.g = grammarFSM()
        self.g.fsm_setup()

        ### One tree for sentences
        self.s_Tree = R_Tree()
        #self.s_root = self.s_Tree.addNode(0, 0, 0)
        
        ### One for constituents
        self.c_Tree = R_Tree()
        self.owners = TheOwner()
        #self.c_root = self.c_Tree.addNode(0, 0, 0)

        
        ### and one for graphing
        self.G = nx.Graph()
        
                
    def sentence_to_Tree(self, sentence, cur_node=1):
        if not sentence:
            return
        for x in sentence[2]:
            self.s_Tree.insert_onto_master(cur_node, data=[x[0], x[1]])
            cur_node += 1
            
    def lastOwner(self, nodes):
        f_owners = filter(lambda x: isinstance(x, Owner), t_nodes)
        return f_owners
    
    def const_toTree(self, constituent):        
        t_currentNode = 0
        t_constituent = [(constituent, -1)]
        t_nodes       = deque()
        t_lastnode    = None
        
        while t_constituent:
            ## ->[X,x,x,x,x]
            item, level  = t_constituent.pop()
            if isinstance(item, list):
                for i in reversed(item):
                    t_constituent.append((i, level + 1))
            else:
                #debug(t_nodes)
                #debug(len(t_constituent))
                data = item
                
                if len(t_constituent) >= 2:
                    if t_constituent[-1][1] - t_constituent[-2][1] >= 1:
                        node = self.owners.addOwner(t_lastnode)
                        t_nodes.appendleft(node)
                        t_nodes[1].r_tail = t_nodes[0]

                        node = self.owners.addObject(item, node)
                        debug(t_nodes)
                        #t_lastnode = t_nodes[0]
                    else:
                        node = self.owners.addObject(data, t_lastnode)
                        debug(node)
                else:
                    node = self.owners.addObject(data, t_lastnode)
                    #t_nodes.appendleft(node)
                    #t_lastnode = t_nodes[0]
                    
                debug(t_nodes)
                t_currentNode += 1
            
        return self.owners
    
    def constToTree(self, sentence, constituent):
        t_currentNode = 0
        t_constituent = [(constituent, -1)]
        t_nodes       = deque()
        while t_constituent:
            ## ->[X,x,x,x,x]
            item, level  = t_constituent.pop()
            if isinstance(item, list):
                for i in reversed(item):
                    t_constituent.append((i, level + 1))
            else:
                data = [item, sentence[0][t_currentNode+1],\
                        sentence[2][t_currentNode][0],\
                        sentence[2][t_currentNode][1]]
                
                if level == 1:
                    master = self.c_Tree.insert_onto_master(t_currentNode, data)
                    t_nodes.appendleft(master)
                else:
                    previousNode = t_nodes[0]
                    if previousNode.right_tail:
                        lastNode = self.c_Tree.insert(previousNode.right_tail,
                                                      t_currentNode, data, level)
                    else:
                        lastNode = self.c_Tree.insert(previousNode,
                                                      t_currentNode, data, level)
                    t_nodes.appendleft(lastNode)

                    
                ## print '%d: %s' % (level, item)

                ## only add if we arent a list
                t_currentNode += 1
            
        return self.c_Tree
    
    
    def cTreePrint(self):
        self.c_Tree.pp_children(self.c_Tree.getMasterNode())
        for nodes in self.c_Tree.getMasterNode().master_tail:
            #debug(nodes.right_tail)
            print r.children(nodes)
        
    def analyze(self, text):
        pass


class masterNode:
    master_tail = None
    node_id     = None
    
    def __init__(self):
        self.master_tail  = []
        self.node_id      = 0
    def __repr__(self):
        return '<%s, %d>' % (self.master_tail, self.node_id)

class n_Node:
    left_tail, right_tail, data, level, node_id = None, None, None, None, None
    def __init__(self, node_id, data, level):
        ### initializes the data members
        self.left_tail  = None
        self.right_tail = None
        self.node_id    = node_id
        self.data       = data
        self.level      = level

    def __repr__(self):
        return '%s' % (self.data)
    
class R_Tree:
    def __init__(self):
        self.master = masterNode()

    def getMasterNode(self):
        return self.master
    
    def addNode(self, node_id, data, level):
        return n_Node(node_id, data, level)
    
    def graphTree(self, root_node):
        G = nx.DiGraph()
        graph_itr = 1
        visited   = []
        nodes     = deque()
        
        ###  Acyclic tree traversal
        if hasattr(root_node, '__class__'):
            if root_node.__class__.__name__ == 'masterNode':
                for x in root_node.master_tail:
                    ###  coming from the HEAD these will be less
                    ###  significant
                    G.add_edges_from([('HEAD', x)])
                    nodes.appendleft(x)
                    while nodes:
                        current = nodes.popleft()
                        if current in visited:
                            continue
                        
                        G.add_edges_from([(x, current)])
                        if hasattr(current, 'right_tail'):
                            if current.right_tail:
                                G.add_edges_from([(current, current.right_tail)])
                                
                            nodes.appendleft(current.right_tail)
                        if hasattr(current, 'left_tail'):
                            nodes.appendleft(current.left_tail)
                        
                        visited.append(current)
                        if visited[graph_itr-2] != current and current != None\
                            and visited[graph_itr-2] != None:
                            G.add_edges_from([(visited[graph_itr-2], current)])
                            
                        elif current != None:
                            G.add_node(current)
                            
                        graph_itr += 1
                    
            else:
                while nodes:
                    current = nodes.popleft()
                    if current in visited:
                        continue
                    if current.right_tail:
                        nodes.appendleft(current.right_tail)
                    if current.left_tail:
                        nodes.appendleft(current.left_tail)

                    visited.append(current)
                    G.add_edge(current, visited[i-1])

                    i += 1
        try:
            #pos = nx.draw_graphviz(G, prog='neato')
            pos = nx.spring_layout(G, iterations=40)
        except:
            pos = nx.spectral_layout(G, iterations=20)

        font = {'fontname'   : 'Helvetica',
                'color'      : 'k',
                'fontweight' : 'bold',
                'fontsize'   : 14}

        
        ### draw up the nodes
        nx.draw_networkx_nodes(G, pos, node_size=800,
                               node_color="#A0CBE2", edge_cmap=plt.cm.Blues)
        nx.draw_networkx_edges(G, pos, width=1.2, alpha=0.5,
                               edge_color='b', style='dashed')
        nx.draw_networkx_labels(G,pos,font_size=7, font_family='sans-serif')
        #nx.draw(G, pos, node_color='#A0CBE2', width=1.2, edge_cmap=plt.cm.Blues)

        plt.axis('off')
        #plt.title("Analysis of Tree", font)
        plt.savefig("c_tree_structure.png")

        
    def insert_onto_master(self,  node_id, data):
        node = self.addNode(node_id, data, 0)
        if node in self.master.master_tail:
            return False
        
        self.master.master_tail.append(node)
        self.master.node_id += 1
        #print self.master
        tail_length = len(self.master.master_tail)
        if tail_length > 1:
            rightTail = self.master.master_tail[tail_length-2]
            #if hasattr(rightTail, 'right_tail'):
            #    if not rightTail.right_tail:
            #        rightTail.right_tail = node

        return node
    
    def insert(self, root_node, node_id, data, level, new=False):
        if new:
            return self.addNode(node_id, data, level)
        else:
            if node_id <= root_node.node_id:
                ###  if the data is less than the stored one
                ###  goes into the left-sub-tree
                root_node.left_tail = self.insert(root_node.left_tail,
                                                  node_id, data, level, new=True)
            else:
                ###  processes the right-sub-tree
                root_node.right_tail = self.insert(root_node.right_tail,
                                                   node_id, data, level, new=True)

            return root_node

    def travel_left(self, root_node):
        if root_node.left_tail:
            return root_node.left_tail
        else:
            return False
    
    def travel_right(self, root_node=None):
        nodes = deque()
        
        if root_node == None:
            root_node = self.master

        if isinstance(root_node, masterNode):
            for x in root_node.master_tail:
                visited = set()
                nodes.appendleft(x)
        
                while nodes:
                    current = nodes.popleft()
                    if current in visited:
                        continue
                    if hasattr(current, 'right_tail'):
                        nodes.appendleft(current.right_tail)
                    if hasattr(current, 'left_tail'):
                        nodes.appendleft(current.left_tail)
                        
                    if current:
                        visited.add(current)
                        yield current
        else:
            visited = set()
            nodes.appendleft(root_node)
        
            while nodes:
                current = nodes.popleft()
                if current in visited:
                    continue
                if hasattr(current, 'right_tail'):
                    nodes.appendleft(current.right_tail)
                if hasattr(current, 'left_tail'):
                    nodes.appendleft(current.left_tail)
                        
                if current:
                    visited.add(current)
                    yield current

    
    def pp_children(self, root_node):
        nodes = deque()
        visited = set()
        for x in root_node.master_tail:
            indent_level = 0
            nodes.appendleft(x)
            while nodes:
                current = nodes.popleft()
                if current in visited:
                    continue
                
                if current:
                    print 'level: %s' % current.level,
                    print '  ' * indent_level,
                    print '+[%s]' % (current.data)

                if hasattr(current, 'right_tail'):
                    indent_level += 1
                    nodes.appendleft(current.right_tail)
                       
    def __children_master(self, root_node):
        nodes = deque()
        for x in root_node.master_tail:
            visited = set()

            nodes.appendleft(x)
        
            while nodes:
                current = nodes.popleft()
                if current in visited:
                    continue
                if hasattr(current, 'right_tail'):
                    nodes.appendleft(current.right_tail)
                if hasattr(current, 'left_tail'):
                    nodes.appendleft(current.left_tail)
                
                visited.add(current)
                           
        return visited

    def children(self, root_node):
        "returns a list of every child"
        if hasattr(root_node, '__class__'):
            if root_node.__class__.__name__ == 'masterNode':
                visited = self.__children_master(root_node)
            else:
                visited = set()
                nodes = deque([root_node])
        
                while nodes:
                    current = nodes.popleft()
                    if current in visited:
                        continue
                    if current.right_tail:
                        nodes.appendleft(current.right_tail)
                    #if current.left_tail:
                    #    nodes.appendleft(current.left_tail)
                
                    visited.add(current)
            
        return list(visited)


class Object:
    data    = None
    ownedBy = None
    r_tail  = None
    
    def __init__(self, data):
        self.data = data
        
    def __repr__(self):
        return '<%s, %s>' % (self.data, self.r_tail)
    
class Owner:
    owns    = None
    ownedBy = None
    
    def __init__(self):
        self.owns = []
    def __repr__(self):
        return '%s' % (self.owns)
        
class TheOwner:
    master = None
    def __init__(self):
        self.master = Owner()
        
    def addObject(self, data, ownedBy=None):
        if ownedBy == None:
            ownedBy = self.master

        obj = Object(data)
        obj.ownedBy = ownedBy
        
        if ownedBy:
            ownedBy.owns.append(obj)
            #debug(ownedBy.owns)
            
        return obj
    
    def addOwner(self, ownedBy=None):
        if ownedBy == None:
            ownedBy = self.master

        obj = Owner()
        obj.ownedBy = ownedBy
        
        if ownedBy:
            #debug(ownedBy.owns)
            ownedBy.owns.append(obj)
        
        return obj

    def getParent(self, Obj):
        return Obj.ownedBy
    
    def travel_right(self, root=None):
        nodes = deque()
        if root == None:
            root = self.master
            
        if isinstance(root, Owner):
            for x in root.owns:
                nodes.appendleft(x)
                
                while nodes:
                    current = nodes.popleft()
                    if hasattr(current, 'owns'):
                        map(nodes.appendleft, current.owns)
                        
                    yield current



class irc_logParser:
    def loadLogs(self, data, limit=None):
        "accepts data as a glob pattern"
        files    = {}
        output   = []
        
        files = glob.glob(data)
        total_bytes = 0
        line_count  = 0
        
        for _file in files:
            total_bytes = total_bytes + os.path.getsize(_file)
            fhandle = open(_file)
            source_data = fhandle.readlines()
            for c in source_data:
                line_count += 1
                if limit:
                    if line_count >= limit:
                        return output
                    
                data =  c[20:-1]
                if not data:
                    pass
                elif data[0] == '<':
                    userstring = data[1:].split('>')
                    username = userstring[0]
                    string =   userstring[1:]
                    if len(string) > 1:
                        string = ' '.join(string)
                
                    text = str(string[0][1:])

                    output.append(text)
                
            ## end: for _file in files    
            fhandle.close()
        print 'log bytes: %d' % total_bytes
        return output

if __name__ == '__main__':
    logParser = irc_logParser()
    log_data = logParser.loadLogs('logs/2009-08-1*', limit=100)
    #print log_data
    
    grammar = Grammar()
    #sentences = ["I've never really gotten into it."]
    for sentence in log_data:
        v = linkGrammar.constituents(sentence)
        s = linkGrammar.sentence(sentence)
        grammar.sentence_to_Tree(s)
        #c_Root = grammar.get_C_TreeRoot()
        
        #tree = grammar.constToTree(s, v)
        tree = grammar.const_toTree(v)
        #tree.graphTree(tree.getMasterNode())
        grammar.cTreePrint()
        q = []
        for x in tree.travel_right():
            if not isinstance(x, Owner):
                q.append(x)
                #prefix = x.level * ' '
                debug(x)
            else:
                if len(q) > 1:
                    debug('%s owns %s' % (q[-1], x))

    
        #debug(q)
