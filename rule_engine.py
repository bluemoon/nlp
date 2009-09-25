from Plex import *
from debug import *
import re
import pprint

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

class rule_engine:
    def __init__(self):
        self.rules = []
        self.feature_path = feature_path()
        
    def semanticRules(self):
        for k, v in semantic_rules.items():
            if 'regex' in v:
                for x in v['regex']:
                    yield k, x
                    
    def setup_rules(self):
        for k, x in self.semanticRules():
            match_rules = {}
            set_rules   = {}
            
            if x[:2] == '= ':
                ## Also "\." is replaced with "[a-z\*]"
                current_rule = semantic_rules[k]
                for m in current_rule['match']:
                    if not match_rules.has_key(k):
                        match_rules[k] = []
                        
                    match_rules[k].append(self.feature_path.build_path(m))
                    
                for n in current_rule['set']:
                    if not set_rules.has_key(k):
                        set_rules[k] = []
                        
                    set_rules[k].append(self.feature_path.build_path(n))
                    
                self.ndpda.add_transition(x[2:], match_rules, name=k, next_state=set_rules)

    def parse_text(self, sentence):
        if not sentence:
            return

        self.ndpda = NDPDA_FSM('INIT', sentence)
        self.setup_rules()
        processed = self.ndpda.process_list(sentence.tags)
        #self.tokens.fsm_setup()

        pprint.pprint(processed)
        
        return processed


class feature_path:
    def __init__(self, fsm=None):
        if fsm:
            self.fsm = fsm
    
    literals = [
        '%',   ## signifies null
        'str', ## is the literal for the current string
    ]
    
    ## a feature path is made up of
    ## left side, action, right side
    def build_path(self, string):
        idx, action = self.resolve_action(string)
        left, right = self.words_before_and_after(string, idx)
        ## now match the <...>
        left_m = self.match_to_path(left)
        right_m = self.match_to_path(right)
        
        return (left_m, action, right_m)
        
    def match_to_path(self, to_match):
        if '<' in to_match:
            ## it may not be the first character
            L_idx = to_match.index('<')
            if '>' in to_match:
                R_idx = to_match.index('>')
                substring = to_match[L_idx+1:R_idx]
                return substring.split(' ')
            else:
                ## it should really have a matching bracket
                ## but dump the whole thing anyway to play
                ## it safe
                if to_match[0] == ' ':
                    return [to_match[1:]]
                else:
                    return [to_match]
        else:
            ## it doesnt like to pick up that first space
            if to_match[0] == ' ':
                return [to_match[1:]]
            else:
                return [to_match]

    def dict_set(self, object, dictlist, value, action):
        for x in dictlist:
            if object.has_key(x):
                pass
            else:
                if len(dictlist) > 1:
                    object[x] = {}
                else:
                    if action == 'eq':
                        if value == ['%']:
                            try:
                                del object[x]
                            except KeyError:
                                pass
                        else:
                            object[x] = value
                    elif action == 'ap':
                        if isinstance(object[x], list):
                            object[x].append(value)
                        else:
                            object[x] = []
                            object[x].append(value)
                    
            dictlist.pop(0)
            if isinstance(object, dict):
                if not object.has_key(x):
                    object[x] = {}
                self.dict_set(object[x], dictlist, value, action)

    def _has(self, has, sentence):
        if has in sentence:
            has = sentence.index(has)
            return (True, has)
        else:
            return (False, 0)
        
    def resolve_words(self, s_tuple, memory):
        LEFT_TAG  = 'F_L'
        RIGHT_TAG = 'F_R'

        fsm_memory = self.fsm.memory
        left_wall  = self._has('LEFT-WALL',  fsm_memory.words)
        ## start the indexer at 0 if we dont have the left wall
        ## or with 1 if we do, overloaded logic because of no
        ## ternary operator
        i = (left_wall[0] != True and 0 or 1)
        if self.fsm.counter == 0:
            current_span = fsm_memory.spans[self.fsm.counter]
            current_word = fsm_memory.words[self.fsm.counter]
        else:
            current_span = fsm_memory.spans[self.fsm.counter-i]
            current_word = fsm_memory.words[self.fsm.counter-i]
            
        word_set_len = len(fsm_memory.words)
        if word_set_len > (self.fsm.counter + current_span):
            right_word = fsm_memory.words[self.fsm.counter-i + current_span]
        else:
            ## the right word is probably buried in a wall or
            ## actually i have no idea
            right_word = fsm_memory.words[-1]

        
        left_side = s_tuple[0]
        right_side = s_tuple[2]
        
        ## handle left side
        if LEFT_TAG in left_side:
            idx = left_side.index(LEFT_TAG)
            left_side[idx] = current_word
        if RIGHT_TAG in left_side:
            idx = left_side.index(RIGHT_TAG)
            left_side[idx] = right_word
            
        ## handle the right side
        if LEFT_TAG in right_side:
            idx = right_side.index(LEFT_TAG)
            right_side[idx] = current_word
        if RIGHT_TAG in right_side:
            idx = right_side.index(RIGHT_TAG)
            right_side[idx] = right_word
            
        

    def resolve_action(self, parsed):
        for idx, x in enumerate(parsed):
            if '!=' == x:
                return (idx, 'ne')
            if '+=' == x:
                return (idx, 'ap')
            if '=' == x:
                return (idx, 'eq')

            
    def words_before_and_after(self, sentence, idx):
        before = sentence[:idx]
        after = sentence[idx+1:]
        return (before, after)
    
    def match_action(self, s_tuple, memory):
        self.resolve_words(s_tuple, memory)
        if s_tuple[1] == 'eq':
            ## probing the dictionary wildly
            ## good idea to catch non-existant items
            try:
                entry = reduce(getattr, s_tuple[0], object)
                debug(entry)
                if entry == s_tuple[2]:
                    return True
                else:
                    if s_tuple[2] == ['%']:
                        return True
                    else:
                        return False
                    
            except Exception, E:
                if s_tuple[2] == ['%']:
                    return True
                else:
                    return False
        
        if s_tuple[1] == 'ne':
            ## probing the dictionary wildly
            ## good idea to catch non-existant items
            try:
                entry = reduce(getattr, s_tuple[0], object)
                debug(entry)
                if entry == s_tuple[2]:
                    return False
                else:
                    if s_tuple[2] == ['%']:
                        return False
                    else:
                        return True
                    
            except Exception, E:
                if s_tuple[2] == ['%']:
                    return True
                else:
                    return False       

            
    
    def do_action(self, s_tuple, memory):
        ## memory has to be a dictionary
        self.resolve_words(s_tuple, memory)

        if s_tuple[1] == 'eq':
            self.doActionEqual(s_tuple, memory)
        if s_tuple[1] == 'ap':
            self.doActionAppend(s_tuple, memory)
            
    def doActionEqual(self, s_tuple, memory):
        left = s_tuple[0]
        right = s_tuple[2]
        self.dict_set(memory, left, right, 'eq')
        #debug(memory)
        
    def doActionAppend(self, s_tuple, memory):
        left = s_tuple[0]
        right = s_tuple[2]
        self.dict_set(memory, left, right, 'ap')
        #debug(memory)
        
class NDPDA_FSM:
    def __init__(self, initial_state, memory=[]):
        self.feature_path = feature_path(fsm=self)
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
        self.words = {}
        self.frame_memory = {}
        self.frames = []
        
        
    def reset (self):
        self.current_state = self.initial_state
        self.input_symbol = None
        
    
    def match_register_state(self, in_state):
        if len(in_state.items()) < 1:
            return True
        
        head = in_state.keys()[0] 
        state = in_state[head]
        output = None
        match_value = None
            
        for cur_state in state:
            if 'str' in cur_state[0]:
                self.resolve_words(cur_state, self.words)
                words_to_match = cur_state[2][0].split('|')
                debug(words_to_match)
                if cur_state[0] in words_to_match:
                    return True
            
            match = self.feature_path.match_action(cur_state, self.words)
            if not match_value:
                match_value = match
            else:
                if match_value:
                    match_value = match
                    
                    
        return match_value
                    
                
    def set_register_state(self, in_state):
        if len(in_state.items()) < 1:
            return

        head = in_state.keys()[0]
        state = in_state[head]
        #debug(state)
        for cur_state in state:
            self.feature_path.do_action(cur_state, self.words)
    
    def add_transition(self, input_symbol, state, next_state=None, name=None, action=None):
        if next_state is None:
            next_state = state
            
        self.state_transitions[input_symbol] = (state, action, next_state, name)
        
    def get_transition(self, input_symbol):
        for regex_transitions in self.state_transitions:
            regex = regex_transitions
            regex.replace('\.', '[a-z]')
            if regex[0] == ' ':
                regex = regex[1:]
                
            if regex[0] != '(':
                to_compile = '(%s)' % regex
            else:
                to_compile = regex
                
            re_to_match = re.compile(to_compile)
            re_search = re_to_match.match(input_symbol)
            if re_search:
                yield self.state_transitions[regex_transitions]


    def process(self, input_symbol):
        output = None
        self.input_symbol = input_symbol
        for transitions in self.get_transition(self.input_symbol):
            self.state, self.action, self.next_state, self.name = transitions
            if self.match_register_state(self.state):
                self.set_register_state(self.next_state)
                break
            

            #output = {self.name:{'set_state':self.next_state}}

        self.frames.append((self.counter, self.frame_memory))
        self.frame_memory = {}
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
            
        return self.words



