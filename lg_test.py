# -*- coding: utf-8 -*-
from collections import deque
import os
import sys
import pprint
import inspect
import glob
import time
import re

## pretty graphs
import networkx as nx
import matplotlib.pyplot as plt
import pylab

import lg_fsm as lgFSM
import linkGrammar

from debug import *
from structures.fsm import FSM
from utils.list import list_functions
from tree_utils import Print
from semantic_rules import semantic_rules
from containers import sentence

#from nltk.sem import logic
from grammar_fsm import Semantics
from grammar_fsm import NDPDA_FSM


### RELATIONSHIPS:
###   Wd(left, x) & Ss(y, z) & (x & y) -> subject(z, y)
###   TO(x, y) -> todo(x, y)
###   O(x, y) -> object(x, y)
###   Wi(x, y) -> imperative(x, y)


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
        debug(input)
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
        #self.c_root = self.c_Tree.addNode(0, 0, 0)

        
        ### and one for graphing
        self.G = nx.Graph()
        self.lists = list_functions()
        self.tree_print = Print()
        
    def sentenceFSM(self, sentence):
        if sentence:
            flat = self.lists.flatten(sentence[2])
            self.g.fsm_run(flat)
        
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
        t_visited     = set()
        t_output      = []
        
        while t_constituent:
            ## ->[X,x,x,x,x]
            item, level  = t_constituent.pop()
            if repr(item) in t_visited:
                continue
            
            t_visited.add(repr(item))

            if isinstance(item, list):
                for i in reversed(item):
                    t_constituent.append((i, level + 1))
            else:
                if item:
                    data = {'word' : item, 'level' : level}
                    t_output.append(data)
                
        return t_output
    
    def constNormalize(self, const_in):
        c_iterator  = 0
        c_previous  = [const_in[:1][0]['level']]
        c_corrected = [0]
        
        for const in const_in[1:]:
            if const['level'] - c_corrected[-1] > 1:
                c_corrected.append(c_corrected[-1] + 1)
            elif const['level'] - c_corrected[-1] == 0:
                c_corrected.append(c_corrected[-1])
            elif const['level'] - c_corrected[-1] == 1:
                c_corrected.append(c_corrected[-1] + 1)
            elif const['level'] - c_corrected[-1] < 1:
                c_corrected.append(c_corrected[-1] - 1)
                
            c_previous.append(const['level'])
            c_iterator += 1
            
        return c_corrected

    
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

                line_count += 1
                if limit:
                    if line_count >= limit:
                        return output
                
            ## end: for _file in files    
            fhandle.close()
        print 'log bytes: %d' % total_bytes
        return output

if __name__ == '__main__':
    logParser = irc_logParser()
    log_data = logParser.loadLogs('logs/2009-08-1*', limit=200)
    p = Print()
    for sentence in log_data:
        if not sentence:
            continue
        
        grammar = Grammar()
        semantics = Semantics()
        v = linkGrammar.constituents(sentence)
        s = linkGrammar.sentence(sentence)
        if s:
            p.print_sentence(s[0])
            p.print_diagram(s)
            
        grammar.sentence_to_Tree(s)
        tree = grammar.const_toTree(v)
        
        sem_output = semantics.handleSemantics(s)
        debug(sem_output)
        
        if not tree:
            continue

        #normal = grammar.constNormalize(tree)
        debug(TERM_GREEN + '--START SENTENCE--' + TERM_END)
        for x in tree:
            currentLevel = x['level']
            debug('%s+%s' % (currentLevel * '-', x['word']))
            
        debug(TERM_RED + '--END SENTENCE--' + TERM_END)

    
        #debug(q)
    graphDebugTimes()
