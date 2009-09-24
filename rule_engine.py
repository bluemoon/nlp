from Plex import *
from debug import *
import re

from semantic_rules import semantic_rules
from grammar_fsm import ND_FSM
###  type l:tag(-|+) r:tag(-|+)
###  - = left of
###  + = right of

### RELATIONSHIPS:
###  subject l:Wd-[n] r:Ss-[n+1];
###  todo l:TO-[n] r:TO+[n];
###  object l:O-[n] r:O+[n];
###  imperative l:Wi-[n] r:Wi+[n];

###  adj1 l:(A.*|DT.*)+[n] r:(A.*|DT.*)-[n];
###  adj2 l:(Mp.*|MVp.*|Ma.*)-[n] r:(Mp.*|MVp.*)+[n];
###  adv1 l:(EB.*|MVa.*)-[n] r:(EB.*|MVa.*)+[n] !(EBx.*)
###  adv2 l:(E.*|EA.*)+[n] r:(E.*|EA.*)-[n] !(EA(m|y).*)
###  adv3

def test_rules(sentence):
    r = rule_engine()
    r.parse_text(sentence)

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
        
        
class rule_engine:
    def __init__(self):
        self.rules = []
        self.rule_file = "rules.txt"
        self.tokens = SemTokenizer()
        
    def semanticRules(self):
        for k, v in semantic_rules.items():
            if 'regex' in v:
                for x in v['regex']:
                    yield k, x
                    
    def parse_text(self, sentence):
        if not sentence:
            return

        self.ndpda = NDPDA_FSM('INIT', sentence)
        
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
                    
                self.ndpda.add_transition(x[2:], match_rules, name=k, next_state=set_rules)

        
        processed = self.ndpda.process_list(sentence.tags)
        
        return processed
    
class feature_path:
    def build_path(self, string):
        idx, action = self._resolve_action(string)
        left, right = self._words_before_and_after(string, idx)
        
        
    def _resolve_word(self, parsed):
        for x in parsed:
            if x[0] == 'front_left':
                return self.memory.tag_set[self.counter].left
            if x[0] == 'front_right':
                return self.memory.tag_set[self.counter].right
            
    def _resolve_action(self, parsed):
        idx = 0
        for x in parsed:
            if 'ne' == x[0]:
                return (idx, 'ne')
            if 'ap' == x[0]:
                return (idx, 'ap')
            if 'eq' == x[0]:
                return (idx, 'eq')
            idx += 1
            
    def _words_before_and_after(self, sentence, idx):
        before = sentence[:idx]
        after = sentence[idx+1:]
        return (before, after)
        

    def _variable_list(self, parsed):
        variables = []
        for y in parsed:
            if y[0] == 'ne' or y[0] == 'ap' or y[0] == 'eq':
                break
            if (y[1] != '<F_L') and (y[1] != '<F_R'):
                if '>' in y[1]:
                    variables.append(y[1][:-1])
                    break
                else:
                    variables.append(y[1])
                    
        return variables
            
class NDPDA_FSM:
    def __init__(self, initial_state, memory=[]):
        self.state_transitions = {}

        self.input_symbol = None
        self.initial_state = initial_state
        self.current_state = self.initial_state
        self.next_state = None
        self.action = None
        self.memory = memory
        self.output = []
        self.registers = {}
        self.counter = 0
        self.words  = {}
        
        
    def reset (self):
        self.current_state = self.initial_state
        self.input_symbol = None
        
    

    def _words_before_and_after(self, sentence, word):
        if word in sentence:
            idx = sentence.index(word)
            before = sentence[:idx]
            after = sentence[idx+1:]
            return (before, after)
        else:
            print '%s not in %s' % (word, sentence)
            return False
        
    def _resolve_word(self, parsed):
        for x in parsed:
            if x[0] == 'front_left':
                return self.memory.tag_set[self.counter].left
            if x[0] == 'front_right':
                return self.memory.tag_set[self.counter].right
            
    def _variable_list(self, parsed):
        #self._words_before_and_after(parsed)
        variables = []
        for y in parsed:
            if y[0] == 'ne' or y[0] == 'ap' or y[0] == 'eq':
                break
            if (y[1] != '<F_L') and (y[1] != '<F_R'):
                if '>' in y[1]:
                    variables.append(y[1][:-1])
                    break
                else:
                    variables.append(y[1])
                    
        return variables
    
    def _resolve_action(self, parsed):
        idx = 0
        for x in parsed:
            if 'ne' == x[0]:
                return (idx, 'ne')
            if 'ap' == x[0]:
                return (idx, 'ap')
            if 'eq' == x[0]:
                return (idx, 'eq')
            idx += 1
            
    def _match_str(self, match_rule):
        current_word = self.memory.words[self.counter]
        c_regex = re.compile(match_rule[0][1])
        c_match = c_regex.match(current_word)
        if c_match:
            return True
        else:
            return False
        
    def _has_word(self, word):
        if self.words.has_key(word):
            return True
        else:
            self.words[word] = {}
            
    def r_getattr(self, object, attr):
        return reduce(getattr, attr, object)

    def r_setattr(self, object, attr, value):
        return setattr(reduce(getattr, attrs[:-1], object), attrs[-1], value)

    def dict_set(self, object, dictlist, value):
        for x in dictlist:
            if object.has_key(x):
                pass
            else:
                if len(dictlist) > 1:
                    object[x] = {}
                else:
                    object[x] = value
                    
            dictlist.pop(0)
            self.dict_set(object[x], dictlist, value)
    
    def match_register_state(self, in_state):
        if len(in_state.items()) < 1:
            return
        
        head = in_state.keys()[0]
        
        state = in_state[head]
        
        debug(state)
        variables = self._variable_list(state)
        reference = self._resolve_word(state)
        idx, action = self._resolve_action(state)

        if action == 'eq':
            for y in variables:
                if y == 'str':
                    return self._match_str(state[idx+1:])

                else:
                    self._has_word(reference)
                    if self.words[reference].has_key(y):
                        #self.words[reference][y]
                        pass
                    else:
                        if state[idx+1:][0][0] == 'percent':
                            return True
                        else:
                            return False
                    
        #pass

    def set_register_state(self, in_state):
        head = in_state.keys()[0]
        state = in_state[head]
        debug(state)
        variables = self._variable_list(state)
        reference = self._resolve_word(state)
        #print self.r_getattr(self.words[reference], variables)
        idx, action = self._resolve_action(state)
        if action == 'eq':
            self.dict_set(self.words[reference], variables, state[idx+1:][1])
            
        debug(self.words)
        debug(variables)
        if 'ref' in variables:
            position = variables.index('ref')
            right_of = variables[position+1:]
    
    
    def add_transition(self, input_symbol, state, next_state=None, name=None, action=None):
        if next_state is None:
            next_state = state
            
        self.state_transitions[input_symbol] = (state, action, next_state, name)
        
    def get_transition(self, input_symbol):
        for regex_transitions in self.state_transitions:
            re_to_match = re.compile(regex_transitions)
            re_search = re_to_match.match(input_symbol)
            if re_search:
                yield self.state_transitions[regex_transitions]


    def process(self, input_symbol):
        output = None
        self.input_symbol = input_symbol
        for transitions in self.get_transition(self.input_symbol):
            self.state, self.action, self.next_state, self.name = transitions
            if self.match_register_state(self.state):
                debug('were getting somewhere')
                self.set_register_state(self.next_state)
                
            if self.action is not None:
                if self.action(self):
                    break

            #output = {self.name:{'set_state':self.next_state}}

            
        self.current_state = self.next_state
        self.next_state = None
        self.counter += 1
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



