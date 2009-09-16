import sys
import pprint

from fsm import FSM
import lg_fsm as lgFSM
import linkGrammar

import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import inspect
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
    if not prefix:
        print '[%s-%d]: ' % (caller_method, from_line),
        pprint.pprint(obj)
    else:
        print '[%s-%d] %s: ' % (caller_method, from_line, prefix),
        pprint.pprint(obj)
        
    #LastDebugged = caller_method
    #print 'value: %s ' % repr(object),
    #print 'type: %s ' % type(obj),
    #print 'id: %s ' % id(obj),
    
class list_functions:
    def flatten(self, List):
        ### take a list of varied depth
        ### and flatten it! with no recursion
        return reduce(list.__add__, map(lambda x: list(x), [y for y in List]))
    
    def print_list(self, List):
        stack = [(List, -1)]
        while stack:
            item, level = stack.pop()
            if isinstance(item, list):
                for i in reversed(item):
                    stack.append((i, level+1))
            else:
                print "\t" * level, item
        
    def max_depth(self, List):
        accessorList = self.subtree_indices(List)
        a_list = self.flatten(accessorList)
        c_max_depth = reduce(lambda x, y: max(x, y), a_list)
        if c_max_depth:
            return max(c_max_depth)
        
    def subtree_indices(self, tree_rep):
        tree = [([], tree_rep)]
        list_of_indexLists = []
        tree_indices = deque()
        while tree != []:
            (indices, sub_tree) = tree.pop(0)
            #print indices, sub_tree
            list_of_indexLists.append(indices)
            for (ordinal, subTree) in enumerate(sub_tree[1:]):
                debug(ordinal)
                debug(subTree)
                if isinstance(subTree, list):
                    idxs = indices[:]

                    debug(idxs)
                    debug(ordinal)
                    
                    if len(idxs) == 0:
                        tree_indices.append([0])
                    else:
                        tree_indices.append(idxs)
                        
                    idxs.append(ordinal+1)
                    tree.append((idxs, subTree))

        return list_of_indexLists

 
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
        
    def flatten(self, List):
        ### take a list of varied depth
        ### and flatten it! with no recursion
        return reduce(list.__add__, map(lambda x: list(x), [y for y in List]))
    
    
    def print_list(self, List):
        stack = [(List, -1)]
        while stack:
            item, level = stack.pop()
            if isinstance(item, list):
                for i in reversed(item):
                    stack.append((i, level+1))
            else:
                print "\t" * level, item
        

    def subtree_indices(self, tree_rep):
        tree = [([], tree_rep)]
        list_of_indexLists = []
        tree_indices = deque()
        while tree != []:
            (indices, sub_tree) = tree.pop(0)
            #print indices, sub_tree
            list_of_indexLists.append(indices)
            for (ordinal, subTree) in enumerate(sub_tree[1:]):
                debug(ordinal)
                debug(subTree)
                if isinstance(subTree, list):
                    idxs = indices[:]

                    debug(idxs)
                    debug(ordinal)
                    
                    if len(idxs) == 0:
                        tree_indices.append([0])
                    else:
                        tree_indices.append(idxs)
                        
                    idxs.append(ordinal+1)
                    tree.append((idxs, subTree))

        return list_of_indexLists
    

                
        
    def sentence_to_Tree(self, sentence, cur_node=1):
        for x in sentence[2]:
            self.s_Tree.insert_onto_master(cur_node, data=[x[0], x[1]])
            cur_node += 1

    def constToTree(self, sentence, constituent):
        currentNodeId = 0
        
        self.print_list(constituent)
        print constituent
        
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
                if level == 1:
                    master = self.c_Tree.insert_onto_master(t_currentNode, item)
                    t_nodes.appendleft(master)
                else:
                    previousNode = t_nodes[0]
                    lastNode = self.c_Tree.insert(previousNode, t_currentNode, item)
                    t_nodes.appendleft(lastNode)
                    
                print '%d: %s' % (level, item)
                
            t_currentNode += 1
            
        return self.c_Tree
    
    
    def cTreePrint(self):
        self.c_Tree.pp_children(self.c_Tree.getMasterNode())
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
        return '<%s, %d>' % (self.master_tail, self.node_id)

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
                    ###  coming from the HEAD these will be less
                    ###  significant
                    G.add_weighted_edges_from([('HEAD', x, 0.25)])
                    nodes.appendleft(x)
                    while nodes:
                        current = nodes.popleft()
                        if current in visited:
                            continue
                        if hasattr(current, 'right_tail'):
                            if current.right_tail:
                                G.add_weighted_edges_from([(current, current.right_tail, 0.50)])
                                
                            nodes.appendleft(current.right_tail)
                        if hasattr(current, 'left_tail'):
                            nodes.appendleft(current.left_tail)
                        
                        visited.append(current)
                        if visited[graph_itr-2] != current and current != None and visited[graph_itr-2] != None:
                            G.add_weighted_edges_from([(visited[graph_itr-2], current, 0.5)])
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

        ### draw up the nodes
        nx.draw_networkx_nodes(G, pos, node_size=1000,
                               node_color="#A0CBE2", edge_cmap=plt.cm.Blues)
        nx.draw_networkx_edges(G, pos, width=1.2, alpha=0.5,
                               edge_color='b', style='dashed')
        nx.draw_networkx_labels(G,pos,font_size=7, font_family='sans-serif')
        #nx.draw(G, pos, node_color='#A0CBE2', width=1.2, edge_cmap=plt.cm.Blues)

        plt.axis('off')
        #plt.title("Analysis of Tree", font)
        plt.savefig("c_tree_structure.png")

        
    def insert_onto_master(self,  node_id, data):
        node = self.addNode(node_id, data)
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
    
    def insert(self, root_node, node_id, data, new=False):
        if new:
            return self.addNode(node_id, data)
        else:
            if node_id <= root_node.node_id:
                ###  if the data is less than the stored one
                ###  goes into the left-sub-tree
                root_node.left_tail = self.insert(root_node.left_tail,
                                                  node_id, data, new=True)
            else:
                ###  processes the right-sub-tree
                root_node.right_tail = self.insert(root_node.right_tail,
                                                   node_id, data, new=True)

            return root_node

    def traverseLeft(self, root_node):
        return root_node.left_tail
    def traverseRight(self, root_node):
        return root_node.right_tail
    
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
                    print '   ' * indent_level,
                    print '+[%s]' % (current.data)
                #else:
                #    print '+[None]'
                if hasattr(current, 'right_tail'):
                    indent_level += 1
                    nodes.appendleft(current.right_tail)
                    

        '''
        
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
        '''            
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
    v = linkGrammar.constituents("The quick brown fox jumps over the lazy dog")
    s = linkGrammar.sentence("The quick brown fox jumps over the lazy dog")
    grammar.sentence_to_Tree(s)
    #c_Root = grammar.get_C_TreeRoot()
    rightTree = R_Tree()
    #consti = grammar.subtree_indices(v)
    tree = grammar.constToTree(s, v)
    tree.graphTree(tree.getMasterNode())
    grammar.cTreePrint()

    
    
