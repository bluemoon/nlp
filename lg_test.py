import sys
import pprint

from fsm import FSM
import lg_fsm as lgFSM
import linkGrammar

import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
#from nltk.sem import logic


link_definitions ={
    'A'  : 'Attributive',
    'AA' : 'AA is used in the construction "How big a dog was it?"',
    'AF' : 'Connects adjectives to verbs in cases where the adjectiveis "fronted"',
    'B'  : 'Is used in a number of situations, involving relative clauses and questions.',
    'D'  : 'Connects determiners to nouns',
    'EA' : 'Connects adverbs to adjectives',
    'EB' : 'Connects adverbs to forms of "be" before an object, adjective, or prepositional phrase',
    'I'  : 'Connects certain verbs with infinitives',
    'J'  : 'Connects prepositions to their objects',
    'M'  : 'Connects nouns to various kinds of post-nominal modifiers without commas',
    'Mv' : 'Connects verbs (and adjectives) to modifying phrases',
    'O*' : 'Connects transitive verbs to direct or indirect objects',
    'OX' : 'Is a special object connector used for "filler" subjects like "it" and "there"',
    'Pp' : 'Connects forms of "have" with past participles',
    'Pa' : 'Connects certain verbs to predicative adjectives',
    'R'  : 'Connects nouns to relative clauses',
    'S'  : 'Connects subject-nouns to finite verbs',
    'Ss' : 'Noun-verb Agreement',
    'Sp' : 'Noun-verb Agreement',
    'Wd' : 'Declarative Sentences',
    'Wq' : 'Questions',
    'Ws' : 'Questions',
    'Wj' : 'Questions',
    'Wi' : 'Imperatives',
    'Xi' : 'Abbreviations',
    'Xp' : 'Periods',
    'Xx' : 'Colons and semi-colons',
    'Z'  : 'Connects the preposition "as" to certain verbs',
    
}


###  Wd(left, x) & Ss(y, z) & (x & y) -> subject(z, y)
###  TO(x, y) -> todo(x, y)
###  O(x, y) -> object(x, y)
###  Wi(x, y) -> imperative(x, y)

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
        #self.c_root = self.c_Tree.addNode(0, 0, 0)
        
        ### and one for graphing
        self.G = nx.Graph()
        
    #def flatten(self, List):
    #    if isinstance(List, list):
    #        return map(self.flatten, List)
    #    else:
    #        return List

    def flatten(self, List):
        return reduce(list.__add__, map(lambda x: list(x), [y for y in List]))

    def subtree_indices(self, tree_rep):
        tree = [([], tree_rep)]        
        list_of_indexLists = []
        while tree != []:  
            (indices, sub_tree) = tree.pop(0)
            print indices
            list_of_indexLists.append(indices)
            for (ordinal, sst) in enumerate(sub_tree[1:]):
                if isinstance(sst, list):
                    idxs = indices[:]
                    idxs.append(ordinal+1)
                    tree.append((idxs, sst))

        
        return list_of_indexLists
    
    def max_depth(self, List):
        accessorList = self.subtree_indices(List)
        a_list = self.flatten(accessorList)
        c_max_depth = reduce(lambda x, y: max(x, y), a_list)
        if c_max_depth:
            return max(c_max_depth)
        
    def sentence_to_Tree(self, sentence, cur_node=1):
        #G = nx.Graph()
        #colors = range(len(sentence )*2)
        for x in sentence[2]:
            self.s_Tree.insert_onto_master(cur_node, data=[x[0], x[1]])
            #G.add_nodes_from([x[0],x[1]])
            #G.add_edge(sentence[2][cur_node-1][0], sentence[2][cur_node-1][1])
            #G.add_edge(sentence[2][cur_node-2][1], sentence[2][cur_node-1][0])
            
            cur_node += 1
            
        #self.s_Tree.printTree(self.s_root)
        #pos = nx.graphviz_layout(G,prog='twopi',args='')
        #nx.draw(G, pos, node_color='#A0CBE2', width=1.25, edge_cmap=plt.cm.Blues)
        #plt.axis('off')
        #plt.savefig("tree_structure.png")
        #plt.show()
        
    def constituent_to_Tree(self, sentence, constituent, consti_depths, cur_node_id=1, last_node=None, depth=0, last_depth=0):
        x_const_len = 0
        r_depth     = depth
        last_node_  = None
        
        flat_depths = self.flatten(consti)
        #print 'flat: %s' % flat_depths
        #print 'depth: %s' % consti_depths[cur_node_id-1]
        #print 'const: %s' % constituent
        for x_const in constituent:
            x_const_len = len(x_const)
            #print 'r_depth: %d' % r_depth
            #print 'cur_node: %d' % cur_node_id
            
            if isinstance(x_const, list):
                if len(x_const) >= 1:
                    r_depth += 1
                    
                self.constituent_to_Tree(sentence, x_const, consti_depths, cur_node_id, last_node_, r_depth)
                
            else:
                left, right = sentence[2][cur_node_id]
                data = [sentence[0][cur_node_id]]#, left, right, sentence[1][cur_node_id]]
                word = sentence[0][cur_node_id]
                #self.G.add_node(x_const)
                #self.G.add_edge(x_const, right)
                

                hasList = False
                
                for possibleList in range(x_const_len):
                    if isinstance(x_const[possibleList], list):
                        if len(x_const[possibleList]) >= 1:
                            hasList = True

                
                if not last_node:
                    last_node_ = self.c_Tree.insert_onto_master(cur_node_id, data)
                    #self.G.add_edge(sentence[0][cur_node_id-1], word)
                else:
                    last_node_ = self.c_Tree.insert(last_node, cur_node_id, data)
                    #self.G.add_edge(sentence[0][cur_node_id-1], word)
                    
                if not hasList:
                    r_depth -= 1

                if r_depth <= 1:
                    last_node_ = None


            cur_node_id += 1
            
        
        #pos = nx.spring_layout(self.G)
        #nx.draw(self.G, node_color='#A0CBE2', width=1.2, edge_cmap=plt.cm.Blues)
        #plt.savefig("c_tree_structure.png")
        #plt.show()   
        return self.c_Tree
    
    def cTreePrint(self):
        #self.c_Tree.printTree(self.c_root)
        #pprint.pprint(self.c_root.__dict__['right'])
        #print self.c_Tree.getMasterNode().master_tail
        for nodes in self.c_Tree.getMasterNode().master_tail:
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
        return '<%s>' % (self.master_tail)

class n_Node:
    head, left_tail, right_tail, data = None, None, None, None
    def __init__(self, node_id, data):
        ### initializes the data members
        self.head       = None
        self.left_tail  = None
        self.right_tail = None
        self.node_id    = node_id
        self.data       = data

    def __repr__(self):
        return '<%d, %s>' % (self.node_id, self.data)
    
class R_Tree:
    def __init__(self):
        self.master = masterNode()

    def getMasterNode(self):
        return self.master
    
    def addNode(self, node_id, data):
        return n_Node(node_id, data)
    
    def graphTree(self, root_node):
        G = nx.DiGraph()
        graph_itr = 1
        visited   = []
        nodes     = deque()
        ###  Acyclic tree traversal
        if hasattr(root_node, '__class__'):
            if root_node.__class__.__name__ == 'masterNode':
                for x in root_node.master_tail:
                    nodes.appendleft(x)
                    while nodes:
                        current = nodes.popleft()
                        if current in visited:
                            continue
                        if hasattr(current, 'right_tail'):
                            if current.right_tail:
                                G.add_edge(current, current.right_tail)
                                
                            ###print 'c: %s' % current
                            ###print 'c_tail: %s' % current.right_tail
                            nodes.appendleft(current.right_tail)
                        if hasattr(current, 'left_tail'):
                            nodes.appendleft(current.left_tail)
                        
                        visited.append(current)
                        if visited[graph_itr-2] != current and current != None and visited[graph_itr-2] != None:
                            G.add_edge(visited[graph_itr-2], current)
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
            pos = nx.spring_layout(G, iterations=20)
        except:
            pos = nx.spectral_layout(G, iterations=20)

        font = {'fontname'   : 'Helvetica',
                'color'      : 'k',
                'fontweight' : 'bold',
                'fontsize'   : 14}

        # find node near center (0.5,0.5)
        dmin = 1
        ncenter = 0
        for n in pos:
            x, y = pos[n]
            d = (x-0.5) ** 2 + (y - 0.5) ** 2
            if d < dmin:
                ncenter = n
                dmin = d

        p = nx.single_source_shortest_path_length(G, ncenter)
        l = filter(lambda x: x > 1, p.values())
        # nodes
        nx.draw_networkx_nodes(G, pos, node_size=1000, node_color="#A0CBE2", edge_cmap=plt.cm.Blues)
        nx.draw_networkx_edges(G, pos, width=1.2, alpha=0.5, edge_color='b', style='dashed')
        nx.draw_networkx_labels(G,pos,font_size=7, font_family='sans-serif')
        #nx.draw(G, pos, node_color='#A0CBE2', width=1.2, edge_cmap=plt.cm.Blues)

        plt.axis('off')
        #plt.title("Analysis of Tree", font)
        plt.savefig("c_tree_structure.png")

        
    def insert_onto_master(self,  node_id, data):
        node = self.addNode(node_id, data)
        self.master.master_tail.append(node)
        tail_length = len(self.master.master_tail)
        if tail_length > 1:
            rightTail = self.master.master_tail[tail_length-2]
            #print 'ontoMaster:', rightTail
            if hasattr(rightTail, 'right_tail'):
                if not rightTail.right_tail:
                    rightTail.right_tail = node

        return node
    
    def insert(self, root_node, node_id, data, new=False):
        if new:
            return self.addNode(node_id, data)
        else:
            if node_id <= root_node.node_id:
                ###  if the data is less than the stored one
                ###  goes into the left-sub-tree
                root_node.left_tail = self.insert(root_node.left_tail, node_id, data, new=True)
            else:
                ###  processes the right-sub-tree
                root_node.right_tail = self.insert(root_node.right_tail, node_id, data, new=True)

            return root_node

    def traverseLeft(self, root_node):
        return root_node.left_tail
    def traverseRight(self, root_node):
        return root_node.right_tail
    
    #def masterChildren(self, root_node):
        
    def children(self, root_node):
        "returns a list of every child"
        if hasattr(root_node, '__class__'):
            if root_node.__class__.__name__ == 'masterNode':
                for x in root_node.master_tail:
                    visited = set()
                    nodes = deque([root_node])
        
                    while nodes:
                        current = nodes.popleft()
                        if current in visited:
                            continue
                        if current.right_tail:
                            nodes.appendleft(current.right_tail)
                        if current.left_tail:
                            nodes.appendleft(current.left_tail)
                
                        visited.add(current)
                    
            else:
                visited = set()
                nodes = deque([root_node])
        
                while nodes:
                    current = nodes.popleft()
                    if current in visited:
                        continue
                    if current.right_tail:
                        nodes.appendleft(current.right_tail)
                    if current.left_tail:
                        nodes.appendleft(current.left_tail)
                
                    visited.add(current)
            
        return list(visited)



if __name__ == '__main__':
    r = R_Tree()
    #masterNode = r.master_Node()
    #root = r.addNode(0, 'arg!')
    to_master = r.insert_onto_master(1, 'blah!')
    more = r.insert(to_master, 2, 'blah!')
    mm = r.insert(more, 3, 'fuck you')
    
    print r.getMasterNode().__dict__
    print r.children(more)
    
    grammar = Grammar()
    v = linkGrammar.constituents("It's very hard to describe")
    s = linkGrammar.sentence("It's very hard to describe")
    grammar.sentence_to_Tree(s)
    #c_Root = grammar.get_C_TreeRoot()
    rightTree = R_Tree()
    consti = grammar.subtree_indices(v)
    tree = grammar.constituent_to_Tree(s, v, consti)
    tree.graphTree(tree.getMasterNode())
    grammar.cTreePrint()

    
    
