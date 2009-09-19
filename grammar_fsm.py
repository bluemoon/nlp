import re
import string

from structures.fsm import FSM
from utils.list import list_functions
from semantic_rules import semantic_rules
from debug import *


class SemTokenizer:
    def tokenize(self, obj):
        t_head_type   = None
        t_head_left   = '<F_L'
        t_head_right  = '<F_R'
        t_variable    = re.compile('( |[a-zA-Z_-])+')
        t_type        = re.compile('(=|!=).*')
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
                    else:
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
                                else:
                                    temp.append({'R': x_variables})
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

                    else:
                        if prefix[:3] == 'F_L':
                            t_var_output['L'][variables].append('eq')
                            if temp:
                                t_var_output['L'][variables].append(temp)
                        else:
                            t_var_output['R'][variables].append('eq')
                            if temp:
                                t_var_output['R'][variables].append(temp)
                                                
        #debug(t_var_output)
        return t_var_output


class Semantics:
    def __init__(self):
        self.lists = list_functions()
        self.ndpda = NDPDA_FSM('INIT')
        self.tokens = SemTokenizer()
    
    def semanticRules(self):
        for k, v in semantic_rules.items():
            if 'regex' in v:
                for x in v['regex']:
                    yield k, x
    
    def handleSemantics(self, sentence):
        if not sentence:
            return
        for k, x in self.semanticRules():
            if x[:2] == '= ':
                current_rule = semantic_rules[k]
                match_dict = self.tokens.tokenize(current_rule['match'])
                set_dict = self.tokens.tokenize(current_rule['set'])
                self.ndpda.add_transition(x[2:], match_dict, k, set_dict)
                
        processed = self.ndpda.process_list(sentence[3])
        for item_number, dictionary in processed:
            #debug(sentence[1][item_number], prefix='length')
            #debug(sentence[0][item_number], prefix='left_word')
            #try:
            #    debug(sentence[0][item_number+sentence[1][item_number]], prefix='right_word')
            #except:
            #    pass
            if not dictionary:
                continue
            for m_key, m_value in dictionary.items():
                for key, value in m_value.items():
                    side = value.keys()[0]
                    name = m_value['set_state'][side].keys()[0]
                    #debug('w: %d side: %s name: %s' % (item_number, side, name))                    
                    side_ = m_value['set_state'][side][name][1][0].keys()[0]
                    array = m_value['set_state'][side][name][1][0][side_]
                    #debug('w: %d side: %s name: %s' % (item_number, side_, array))
                    if side == 'R' and side_ == 'L':
                        previous = sentence[0][item_number-1]
                        current  = sentence[0][item_number]
                        if name == 'subj' and array == 'ref':
                            debug('subject(%s, %s)' % (current, previous))
                        if name == '_amod' and array == 'ref':
                            debug('_amod(%s, %s)' % (current, previous))
                            
                    if side == 'L' and side_ == 'R':
                        current_len = sentence[1][item_number]
                        next_item = sentence[0][item_number + current_len]
                        current_item = sentence[0][item_number]
                        if name == 'head-question-word' and array == 'head-word':
                            debug('head(%s, %s)' % (current_item, next_item))
                    

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
    def __init__(self, initial_state):
        # Map (input_symbol, current_state) --> (action, next_state).
        self.state_transitions = {}
        # Map (current_state) --> (action, next_state).

        self.input_symbol = None
        self.initial_state = initial_state
        self.current_state = self.initial_state
        self.next_state = None
        self.action = None
        self.memory = []
        self.registers = {}

    def reset (self):
        self.current_state = self.initial_state
        self.input_symbol = None
        
    def set_register_state(self, in_state):
        for key, value in in_state.items():
            if self.registers.has_key(key):
                if not self.registers[key] == value:
                    self.registers[key] = value
            else:
                self.registers[key] = value

    
    def match_register_state(self, in_state):
        matches = True
        for key, value in in_state.items():
            if self.registers.has_key(key):
                if not self.registers[key] == value:
                    matches = False
            else:
                matches = False

        return matches
    
    def add_transition(self, input_symbol, state, action=None, next_state=None):
        #debug(state)
        if next_state is None:
            next_state = state
            
        self.state_transitions[input_symbol] = (state, action, next_state)
        
    def get_transition (self, input_symbol):
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


