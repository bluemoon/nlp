import re
import string

import pydot
import networkx as nx
import matplotlib.pyplot as plt

from structures.fsm import FSM
from structures.graph import Graph
from utils.list import list_functions
from semantic_rules import semantic_rules
from debug import *

class SemTokenizer:
    def tokenize(self, obj):
        t_head_type   = None
        t_head_left   = '<F_L'
        t_head_right  = '<F_R'
        t_variable    = re.compile('((\|%)|[a-zA-Z_-])+')
        t_type        = re.compile('(=|!=|\+=).*')
        t_var_output  = {}

        if obj[:4] == t_head_left:
            t_head_type = 'left'
        elif obj[:4] == t_head_right:
            t_head_type = 'right'

        for x_obj in obj:
            t_variable_match = t_variable.search(x_obj)
            t_type_match = t_type.search(x_obj)
            if t_variable_match:
                v = t_variable_match.group()
                variable_split = v.split(' ')
                prefix = variable_split[:1][0]

                for variables in variable_split[1:]:
                    #t_var_output = {'L':None,'R':None}
                    if prefix == 'F_L':
                        t_var_output['L'] = {variables:[]}
                    elif prefix == 'F_R':
                        t_var_output['R'] = {variables:[]}
                        
                    if t_type_match:
                        t_grouped = t_type_match.group()
                        
                    #debug(t_grouped[2:])
                    t_submatch = t_variable.search(t_grouped[2:])
                    if t_submatch:
                        v = t_submatch.group()
                        variable_split = v.split(' ')
                        sub_prefix = variable_split[:1][0]
                        temp = []
                        if len(variable_split) > 1:
                            for x_variables in variable_split[1:]:
                                if sub_prefix[:3] == 'F_L':
                                    temp.append({'L': x_variables})
                                elif sub_prefix[:3] == 'F_R':
                                    temp.append({'R': x_variables})
                                else:
                                    debug(sub_prefix)
                                    debug(x_variables)
                        elif len(variable_split) == 1:
                            temp.append({'N': variable_split})

                    else:
                        temp = t_grouped[2:]
                        
                    if t_grouped[:2] == '= ':
                        if prefix[:3] == 'F_L':
                            #debug(t_var_output['L'][variables])
                            t_var_output['L'][variables].append('eq')
                            if temp:
                                t_var_output['L'][variables].append(temp)
                        else:
                            t_var_output['R'][variables].append('eq')
                            if temp:
                                t_var_output['R'][variables].append(temp)

                    elif t_grouped[:2] == '!=':
                        if prefix[:3] == 'F_L':
                            t_var_output['L'][variables].append('ne')
                            if temp:
                                t_var_output['L'][variables].append(temp)
                        else:
                            t_var_output['R'][variables].append('ne')
                            if temp:
                                t_var_output['R'][variables].append(temp)

                    elif t_grouped[:2] == '+=':
                        if prefix[:3] == 'F_L':
                            t_var_output['L'][variables].append('ap')
                            if temp:
                                t_var_output['L'][variables].append(temp)
                        else:
                            t_var_output['R'][variables].append('ap')
                            if temp:
                                t_var_output['R'][variables].append(temp)
        #debug(t_var_output)
        return t_var_output


class Semantics:
    def __init__(self):
        self.lists = list_functions()

        self.tokens = SemTokenizer()
        self.graph = Graph()
    
    def semanticRules(self):
        for k, v in semantic_rules.items():
            if 'regex' in v:
                for x in v['regex']:
                    yield k, x
                    
    def semanticsToGraph(self, sentence):
        item_counter = 0
        turing = sentence[0]
        if not sentence:
            return
        
        for word in sentence[0]:
            next_index = item_counter + 1
            if len(turing) > next_index:
                next_word  = turing[next_index]
                item_counter += 1
            else:
                continue

            self.graph.add_node(word, ignore_dupes=True)
            self.graph.add_node(next_word, ignore_dupes=True)
            self.graph.add_edge(word, next_word)
            
            #G.add_edge(word, next_word)

            try:
                right_index = item_counter + sentence[1][item_counter]
            except:
                continue
            if len(turing) > right_index:
                right_word = turing[right_index]
            else:
                continue
            
            #debug('%s <- %s -> %s' % (prev_word, current_word, right_word))
            #G.add_edge(word, right_word)
            
            self.graph.add_node(right_word, ignore_dupes=True)
            self.graph.add_edge(word, right_word)
            
            
            
        first_word = sentence[0][0]
        
        #pos = nx.graphviz_layout(G, prog="dot")
        #pos = nx.spring_layout(G, iterations=40)
        #nx.draw_networkx_nodes(G, pos, node_size=800,
        #                       node_color="#A0CBE2", edge_cmap=plt.cm.Blues)
        #nx.draw_networkx_edges(G, pos, width=1.2, alpha=0.5,
        #                       edge_color='b', style='dashed')
        #nx.draw_networkx_labels(G,pos,font_size=7, font_family='sans-serif')
        #nx.draw(G, pos, node_color='#A0CBE2', width=1.2, edge_cmap=plt.cm.Blues)

        #plt.axis('off')
        #plt.title("Analysis of Tree", font)
        #plt.savefig("dots/%s.png" % (time.time()), dpi=75)

    def handleSemantics(self, sentence):
        if not sentence:
            return

        self.ndpda = NDPDA_FSM('INIT', sentence[0])
        self.semanticsToGraph(sentence)

        for k, x in self.semanticRules():
            if x[:2] == '= ':
                current_rule = semantic_rules[k]
                match_dict = self.tokens.tokenize(current_rule['match'])
                set_dict = self.tokens.tokenize(current_rule['set'])
                self.ndpda.add_transition(x[2:], match_dict, k, set_dict)
                
        processed = self.ndpda.process_list(sentence[3])
        #for item_number, dictionary in processed:
        #    if not dictionary:
        #        continue
        #    for m_key, m_value in dictionary.items():
        #        for key, value in m_value.items():
        #            side = value.keys()[0]
        #            name = m_value['set_state'][side].keys()[0]
        #            #debug('w: %d side: %s name: %s' % (item_number, side, name))                    
        #            side_ = m_value['set_state'][side][name][1][0].keys()[0]
        #            array = m_value['set_state'][side][name][1][0][side_]
        #            #debug('w: %d side: %s name: %s' % (item_number, side_, array))
        #            if side == 'R' and side_ == 'L':
        #                previous = sentence[0][item_number-1]
        #                current  = sentence[0][item_number]
        #                debug('%s(%s, %s)' % (name, current, previous))#
        #
        #                    
        #            if side == 'L' and side_ == 'R':
        #                current_len = sentence[1][item_number]
        #                next_item = sentence[0][item_number + current_len]
        #                current_item = sentence[0][item_number]
        #                #if name == 'head-question-word' and array == 'head-word':
        #                debug('%s(%s, %s)' % (array, current_item, next_item))
                        
                    

        return processed
    
class ExceptionFSM(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return `self.value`

class NDPDA_FSM:
    """ So this is a non-deterministic FSM can be used as a
    push-down Automata (PDA) since a PDA is a FSM + memory."""
    
    registers = None
    def __init__(self, initial_state, memory):
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
        
    def reset (self):
        self.current_state = self.initial_state
        self.input_symbol = None
        
    def set_register_state(self, in_state):
        for key, value in in_state.items():
            head = value.keys()[0]
            #debug(value)
            if len(value[head]) >= 1:
                if key == 'R':
                    if value[head][0] == 'eq':
                        self.R_registers[head] = value[head][1]
                    elif value[head][0] == 'ap':
                        if self.R_registers.has_key(head):
                            self.R_registers[head].append(value[head][1])
                        else:
                            self.R_registers[head] = value[head][1]
                        
                if key == 'L':
                    if value[head][0] == 'eq':
                        self.L_registers[head] = value[head][1]
                    elif value[head][0] == 'ap':
                        if self.L_registers.has_key(head):
                            self.L_registers[head].append(value[head][1])
                        else:
                            self.L_registers[head] = value[head][1]

            debug(self.L_registers)
            debug(self.R_registers)
            
            if self.registers.has_key(key):
                if not self.registers[key] == value:
                    self.registers[key] = value
            else:
                self.registers[key] = value

    
    def match_register_state(self, in_state):
        matches = True
        for key, value in in_state.items():
            head = value.keys()[0]
            #debug(value)
            if len(value[head]) >= 1:
                if key == 'R':
                    if value[head][0] == 'eq':
                        if self.R_registers[head] == value[head][1]:
                            print 'yeah'
                        else:
                            pass
                        
                    elif value[head][0] == 'ap':
                        pass
                        
                if key == 'L':
                    if value[head][0] == 'eq':
                        if self.L_registers[head] == value[head][1]:
                            print 'yeah'
                    elif value[head][0] == 'ap':
                        pass
                    
            debug(self.L_registers, prefix='L registers')
            debug(self.R_registers, prefix='R registers')
            #self._match_variable(value)
            if self.registers.has_key(key):
                if not self.registers[key] == value:
                    matches = False
            else:
                matches = False

        return matches
    
    def _match_variable(self, LR):
        for key, value in LR.items():
            if key == 'str':
                if len(value) > 1:
                    #debug(value)
                    regex = re.compile(value[1][0]['N'])
                    r_search = regex.search(self.memory[0])
                    if r_search:
                        print r_search.group()
        
    def add_transition(self, input_symbol, state, action=None, next_state=None):
        #debug(state)
        if next_state is None:
            next_state = state
            
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

        if output:
            return output
        
        self.memory.pop()
        
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


