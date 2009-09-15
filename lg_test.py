import sys
import pprint
import linkGrammar
from fsm import FSM
import lg_fsm as lgFSM

import RBTree

import itertools
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
class CNode:
    left , right, data, data_left, data_right, data_extra = None, None, None, None, None, None
    
    def __init__(self, data, data_left, data_right, data_extra=None):
        # initializes the data members
        self.left = None
        self.right = None
        self.data = data
        self.data_extra = data_extra
        self.data_left = data_left
        self.data_right = data_right

class LR_Tree:
    def addNode(self, data, l, r, data_extra=None):
        # creates a new node and returns it
        return CNode(data, l, r, data_extra)
    
    def insert(self, root, data, l, r, data_extra=None):
        # inserts a new data
        if root == None:
            # it there isn't any data
            # adds it and returns
            return self.addNode(data, l, r, data_extra)
        else:
            # enters into the tree
            if data <= root.data:
                # if the data is less than the stored one
                # goes into the left-sub-tree
                root.left = self.insert(root.left, data, l, r, data_extra)
            else:
                # processes the right-sub-tree
                root.right = self.insert(root.right, data, l, r, data_extra)
            return root
        
    def lookup(self, root, target):
        # looks for a value into the tree
        if root == None:
            return 0
        else:
            # if it has found it...
            if target == root.data:
                return 1
            else:
                if target < root.data:
                    # left side
                    return self.lookup(root.left, target)
                else:
                    # right side
                    return self.lookup(root.right, target)
    def getLeft(self, root):
        return root.left

    def getRight(self, root):
        return root.right
    
    def minValue(self, root):
        # goes down into the left
        # arm and returns the last value
        while(root.left != None):
            root = root.left
        return root.data

    def maxDepth(self, root):
        if root == None:
            return 0
        else:
            # computes the two depths
            ldepth = self.maxDepth(root.left)
            rdepth = self.maxDepth(root.right)
            # returns the appropriate depth
            return max(ldepth, rdepth) + 1

    def size(self, root):
        if root == None:
            return 0
        else:
            return self.size(root.left) + 1 + self.size(root.right)
        
    def printTree(self, root):
        # prints the tree path
        if root == None:
            pass
        else:
            self.printTree(root.left)
            print root.data,
            print "(%s, %s)" % (root.data_left, root.data_right),
            if root.data_extra:
                print root.data_extra,
                
            self.printTree(root.right)
            
    def printRevTree(self, root):
        # prints the tree path in reverse
        # order
        if root == None:
            pass
        else:
            self.printRevTree(root.right)
            print root.data,
            self.printRevTree(root.left)

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
        self.s_Tree = LR_Tree()
        self.s_root = self.s_Tree.addNode(0, 0, 0)
        
        ### One for constituents
        self.c_Tree = LR_Tree()
        self.c_root = self.c_Tree.addNode(0, 0, 0)

    def get_C_TreeRoot(self):
        return self.c_root
    
    def sentence_to_Tree(self, sentence, cur_node=1):
        for x in sentence[2]:
            #print sentence[0][cur_node-1]
            self.s_Tree.insert(self.s_root, cur_node, x[0], x[1])
            cur_node += 1
            
        self.s_Tree.printTree(self.s_root)
        print 
        print self.s_Tree.minValue(self.s_root)
        print self.s_Tree.maxDepth(self.s_root)
        print self.s_Tree.size(self.s_root)

    def constituent_to_Tree(self, sentence, constituent, head_node=None, cur_node_id=1, last_node=None):    
        for x_const in constituent:
            if isinstance(x_const, list):
                if not last_node:
                    last_node = head_node
                    print 'Oh no'
                    
                self.constituent_to_Tree(sentence, x_const, last_node, cur_node_id)    
            else:
                left, right = sentence[2][cur_node_id]
                #print sentence[2][cur_node_id]
                extra_data = {'word' : sentence[0][cur_node_id], 'length' : sentence[1][cur_node_id]}
                last_node = self.s_Tree.insert(head_node, cur_node_id, left, right, extra_data)

            cur_node_id += 1
            

    def cTreePrint(self):
        self.c_Tree.printTree(self.c_root)
        #self.c_Tree.printRevTree(self.c_root)

        print 
        print self.c_Tree.minValue(self.c_root)
        print self.c_Tree.maxDepth(self.c_root)
        print self.c_Tree.size(self.c_root)
        print self.c_Tree.lookup(self.c_root, 3)
        
    def analyze(self, text):
        pass


#g = grammarFSM()
#g.fsm_setup()

grammar = Grammar()

v = linkGrammar.constituents("It's very hard to describe")
s = linkGrammar.sentence("It's very hard to describe")

grammar.sentence_to_Tree(s)

c_Root = grammar.get_C_TreeRoot()
grammar.constituent_to_Tree(s, v, c_Root)
grammar.cTreePrint()

#pprint.pprint(s)
#print g.fsm_run(s[3])

#j = linkGrammar.sentence("how are you?")
#c = linkGrammar.constituents("how are you?")
#s = linkGrammar.sentence("how are you?")
#print g.fsm_run(s[3])



#draw_text(j)
#print 'sentence 2,',
#pprint.pprint(j)
#relation(j)
#g = grammarFSM()
#g.fsm_setup()
#print g.fsm_run(j[3])
#map_out(j)

#j = linkGrammar.sentence("chomsky, find me cookies.")
#const = linkGrammar.constituents("chomsky, find me cookies.")
#cleanPrint(const)
#print linkGrammar.domains("chomsky, find me cookies.")

#draw_text(j)
#print 'sentence 3,',
#pprint.pprint(j)
#g = grammarFSM()
#g.fsm_setup()
#print g.fsm_run(j[3])
#relation(j)
