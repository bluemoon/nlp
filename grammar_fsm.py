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
                    t_var_output['%s-%s' % (prefix, variables)] = []
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
                                temp.append('%s-%s' % (sub_prefix, x_variables))
                    else:
                        temp = t_grouped[2:]
                        
                    if t_grouped[:2] == '= ':
                        t_var_output['%s-%s' % (prefix, variables)].append('eq')   
                        t_var_output['%s-%s' % (prefix, variables)].append(temp)
                    else:
                        t_var_output['%s-%s' % (prefix, variables)].append('ne')
                        t_var_output['%s-%s' % (prefix, variables)].append(temp)
                        
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
        #debug(sentence)
        flat = self.lists.flatten(sentence[3])
        for f in flat:
            for k, x in self.semanticRules():
                if x[:2] == '= ':
                    current_rule = semantic_rules[k]
                    match_dict = self.tokens.tokenize(current_rule['match'])
                    set_dict = self.tokens.tokenize(current_rule['set'])
                    self.ndpda.add_transition(x[2:], match_dict , k, set_dict)
                
        return self.ndpda.process_list(flat)
            
class ExceptionFSM(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return `self.value`

class NDPDA_FSM:
    ""
    registers = None
    def __init__(self, initial_state, memory=None):
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
        output = []
        self.input_symbol = input_symbol
        for transitions in self.get_transition(self.input_symbol):
            self.state, self.action, self.next_state = transitions
            if self.match_register_state(self.state):
                #debug(self.action)
                #debug(self.state)
                #debug(self.registers)
                
                self.set_register_state(self.next_state)
                current_out = {self.action:[self.state, self.next_state]}
                output.append(current_out)
            
            
        self.current_state = self.next_state
        self.next_state = None

        return output
        
    def process_list (self, input_symbols):
        output = []
        for s in input_symbols:
            output.append(self.process(s))
            
        return output

class grammarFSM:
    def fsm_setup(self):
        self.fsm = FSM('INIT', [])
        self.fsm.set_default_transition(lgFSM.Error, 'INIT')
        
        
    def fsm_run(self, input):
        debug(input)
        return self.fsm.process_list(input)
