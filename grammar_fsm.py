import re
import string

import pydot
import networkx as nx
import matplotlib.pyplot as plt

from structures.fsm import FSM
from structures.atoms import Atoms
from utils.list import list_functions
from semantic_rules import semantic_rules
from debug import *

class SemTokenizer:
    def fsm_setup(self):
        self.fsm = ND_FSM('INIT')
        ## setup our regex finite state machine
        self.fsm.add_transition('<F_L$',  'INIT',  'front_left',        'INIT')
        self.fsm.add_transition('<F_R$',  'INIT',  'front_right',       'INIT')
        self.fsm.add_transition('<F_L>',  'INIT',  'front_left_close',  'INIT')
        self.fsm.add_transition('<F_R>',  'INIT',  'front_right_close', 'INIT')
        
        self.fsm.add_transition('([a-zA-Z_-]|[$])+' , 'INIT', 'tag', 'INIT')
        self.fsm.add_transition('!=',         'INIT', 'ne',         'INIT')
        self.fsm.add_transition('=',          'INIT', 'eq',         'INIT')
        self.fsm.add_transition('\+=',        'INIT', 'ap',         'INIT')
        self.fsm.add_transition('%',          'INIT', 'percent',   'INIT')
        
    def fsm_tokenizer(self, obj):
        split_space = obj.split(' ')
        return self.fsm.process_list(split_space)
        

class Semantics:
    def __init__(self):
        self.lists = list_functions()

        self.tokens = SemTokenizer()
        self.graph = Atoms()
    
    def semanticRules(self):
        for k, v in semantic_rules.items():
            if 'regex' in v:
                for x in v['regex']:
                    yield k, x
                    
    def semanticsToGraph(self, sentence):
        #debug(sentence)
        
        nxG = nx.Graph()

        item_counter = 0
        turing = sentence[0]
        if not sentence:
            nxG.clear()
            return
        
        for word in sentence[0]:
            next_index = item_counter + 1
            if len(turing) > next_index:
                next_word  = turing[next_index]
                item_counter += 1
            else:
                continue

            nxG.add_node(word)
            nxG.add_node(next_word)

            self.graph.add_node(word, ignore_dupes=True)
            self.graph.add_node(next_word, ignore_dupes=True)
            
            nxG.add_edge(word, next_word)
            self.graph.add_edge(word, next_word)
            
            #G.add_edge(word, next_word)

            try:
                right_index = item_counter + sentence[1][item_counter]
                tag = sentence[3][item_counter]
            except:
                continue
            if len(sentence[3]) > right_index:
                right_word = sentence[0][right_index]
            else:
                continue
            
            nxG.add_node(tag)
            nxG.add_edge(tag, word)
            nxG.add_edge(tag, next_word)
            self.graph.add_node(tag, ignore_dupes=True)
            self.graph.add_edge(tag, word)
            self.graph.add_edge(tag, next_word)

            #self.graph.add_node(right_word, ignore_dupes=True)
            #self.graph.add_edge(word, right_word)
            



        pos = nx.spring_layout(nxG, iterations=40)

        #font = {'fontname'   : 'Helvetica',
        #        'color'      : 'k',
        #        'fontweight' : 'bold',
        #        'fontsize'   : 14}

        
        ### draw up the nodes
        # nx.draw_networkx_nodes(nxG, pos, node_size=800,
        #                       node_color="#A0CBE2", edge_cmap=plt.cm.Blues)
        #nx.draw_networkx_edges(nxG, pos, width=1.2, alpha=0.5,
        #                       edge_color='b', style='dashed')
        #nx.draw_networkx_labels(nxG,pos,font_size=7, font_family='sans-serif')

        plt.axis('off')
        plt.savefig("c_tree_structure.png")
        
        nxG.clear()

        first_word = sentence[0][0]
        debug(self.graph.dfs(first_word))
        
    def handleSemantics(self, sentence):
        if not sentence:
            return

        self.ndpda = NDPDA_FSM('INIT', sentence[0])
        self.semanticsToGraph(sentence)
        
        self.tokens.fsm_setup()
        
        
        for k, x in self.semanticRules():
            match_rules = {}
            set_rules   = {}
            
            if x[:2] == '= ':
                current_rule = semantic_rules[k]
                for m in current_rule['match']:
                    tokenizer_out = self.tokens.fsm_tokenizer(m)
                    match_rules[k] = tokenizer_out
                for n in current_rule['set']:
                    tokenizer_out = self.tokens.fsm_tokenizer(n)
                    set_rules[k] = tokenizer_out
                    
                #match_dict = self.tokens.tokenize(m[0])
                #set_dict = self.tokens.tokenize(current_rule['set'])
                self.ndpda.add_transition(x[2:], match_rules, k, set_rules)
                
        processed = self.ndpda.process_list(sentence[3])
        
        return processed
    
class ExceptionFSM(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return `self.value`
    
class ND_FSM:
    """ So this is a non-deterministic FSM can be used as a
    push-down Automata (PDA) since a PDA is a FSM + memory."""
    
    def __init__(self, initial_state, memory=[]):
        # Map (input_symbol, current_state) --> (action, next_state).
        self.state_transitions = {}
        # Map (current_state) --> (action, next_state).

        self.input_symbol = None
        self.initial_state = initial_state
        self.current_state = self.initial_state
        self.next_state = None
        self.action = None
        self.memory = memory
        
    def reset (self):
        self.current_state = self.initial_state
        self.input_symbol = None
        
    def add_transition(self, input_symbol, state, action=None, next_state=None):
        #debug(state)
        if next_state is None:
            next_state = state
            
        self.state_transitions[input_symbol] = (state, action, next_state)
        
    def get_transition(self, input_symbol):
        for regex_transitions in self.state_transitions:
            re_to_match = re.compile(regex_transitions)
            re_search = re_to_match.match(input_symbol)
            if re_search:
                #debug(self.current_state)
                #debug(self.state_transitions[regex_transitions])
                #if self.state_transitions[regex_transitions][0] == self.current_state:
                yield self.state_transitions[regex_transitions]


    def process(self, input_symbol):
        output = None
        #debug(self.current_state)
        self.input_symbol = input_symbol
        for transitions in self.get_transition(self.input_symbol):
            self.state, self.action, self.next_state = transitions
            
            #self.memory.append(input_symbol)
            output = (self.action, input_symbol)

            
        self.current_state = self.next_state
        self.next_state = self.initial_state

        #self.memory.pop(0)
        if output:
            return output
        
        
        
    def process_list (self, input_symbols):
        #debug(input_symbols)
        output = []
        current_item = 0
        for s in input_symbols:
            #debug(s)
            runner = self.process(s)
            output.append(runner)
                
            current_item += 1
            
        return output




class NDPDA_FSM:
    """ So this is a non-deterministic FSM can be used as a
    push-down Automata (PDA) since a PDA is a FSM + memory."""
    
    registers = None
    def __init__(self, initial_state, memory=[]):
        # Map (input_symbol, current_state) --> (action, next_state).
        self.state_transitions = {}
        # Map (current_state) --> (action, next_state).

        self.input_symbol = None
        self.initial_state = initial_state
        self.current_state = self.initial_state
        self.next_state = None
        self.action = None
        self.memory = memory
        
        self.registers = {}
        self.register_history = []
        self.L_registers = {}
        self.R_registers = {}
        
        self.fsm = FSM('INIT')
        self.fsm.add_transition('front_left',  'INIT', None, 'FRONT_L')
        self.fsm.add_transition('front_right', 'INIT', None, 'FRONT_R')
        
        
    def reset (self):
        self.current_state = self.initial_state
        self.input_symbol = None
        
    def set_register_state(self, in_state):
        #debug(in_state)
        pass
    
    def match_register_state(self, in_state):
        #debug(in_state)
        pass
        
    def add_transition(self, input_symbol, state, action=None, next_state=None):
        #debug(state)
        if next_state is None:
            next_state = state
            
        #debug(state)
        #debug(input_symbol)
        self.state_transitions[input_symbol] = (state, action, next_state)
        
    def get_transition(self, input_symbol):
        for regex_transitions in self.state_transitions:
            re_to_match = re.compile(regex_transitions)
            re_search = re_to_match.search(input_symbol)
            if re_search:
                yield self.state_transitions[regex_transitions]


    def process(self, input_symbol):
        output = None
        self.input_symbol = input_symbol
        for transitions in self.get_transition(self.input_symbol):
            self.state, self.action, self.next_state = transitions
            #debug(self.registers)

            if self.match_register_state(self.state):
                self.set_register_state(self.next_state)
                if self.state:
                    output = {self.action:{'state':self.state,'set_state':self.next_state}}
                else:
                    output = {self.action:{'set_state':self.next_state}}
                break

            
        self.current_state = self.next_state
        self.next_state = None
        
        self.memory.pop(0)
        if output:
            return output
        
        
        
    def process_list (self, input_symbols):
        debug(input_symbols)
        output = []
        current_item = 0
        for s in input_symbols:
            #debug(s)
            runner = self.process(s)
            output.append((current_item, runner))
                
            current_item += 1
            
        return output


