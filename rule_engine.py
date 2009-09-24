from Plex import *
from debug import *
import re
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

def ADJ1(fsm):
    pass
def ADJ2(fsm):
    pass

def POS_VERB(fsm):
    # <F_L POS> = verb
    #fsm.memory.pos[fsm.counter] == 'verb'
    debug(fsm.counter)
    
def POS_VERB_INVERTED(fsm):
    # <F_L POS> = verb
    #fsm.memory.pos[fsm.counter] == 'verb'
    pass

def POS_NOUN(fsm):
    pass

def DETERMINER_POS(fsm):
    # <F_L POS> = det
    string = re.compile('(a|A|an|An|the|The|This|this|These|these|Those|those|That|that)')
    s_match = string.match(fsm.memory.words[fsm.counter])
    if s_match:
        fsm.registers['DETERMINER_LINK_FLAG'] = True
        fsm.L_registers['DETERMINER_FLAG'] = True
        return True
    
    else:
        return False

def DETERMINER_POS2(fsm):
    current_word = fsm.memory.words[fsm.counter]
    if current_word == 'the' or current_word == 'The':
        fsm.registers['DETERMINER_LINK_FLAG'] = True
        fsm.L_registers['DETERMINER_FLAG'] = True
        return True

def POS_NOUN_DET(fsm):
    if fsm.registers.has_key('DETERMINER_LINK_FLAG'):
        if fsm.registers['DETERMINER_LINK_FLAG']:
            return True
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
        
    def parse_text(self, text):
        self.ndpda = NDPDA_FSM('INIT', text)
        self.set_rules()
        print self.ndpda.process_list(text.tags)
        
    def parse_rules(self):
        pass
    
    def set_rules(self):
        self.ndpda.add_transition('(A.*|DT.*)',        'INIT',  action=ADJ1)
        self.ndpda.add_transition('(Mp.*|MVp.*|Ma\.*)', 'INIT', action=ADJ2)

        pos_verb_ = '(S.*|SF.*|SX.*|I.*|B.*|BW.*|P.*|PP.*|Mv.*|Mg.*)'
        self.ndpda.add_transition(pos_verb_, 'INIT', action=POS_VERB)

        pos_verb_inverted_ = '(SI.*|O.*|U.*|PP.*|SXI.*|SFI.*)'
        self.ndpda.add_transition(pos_verb_inverted_, 'INIT', action=POS_VERB_INVERTED)

        pos_noun_ = '(S.*|SX.*|SF.*|AN.*|GN.*|YS.* |YP.*)'
        self.ndpda.add_transition(pos_noun_, 'INIT', action=POS_NOUN)

        determiner_pos_ = '(D.*|DD.*|NS.*)'
        self.ndpda.add_transition(determiner_pos_, 'INIT', action=DETERMINER_POS)
        self.ndpda.add_transition('(DG.*)', 'INIT', action=DETERMINER_POS2)
        
        self.ndpda.add_transition('.*', 'INIT', action=POS_NOUN_DET)
        
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
        self.L_registers = {}
        self.R_registers = {}
        self.registers = {}
        self.counter = 0
        
        
        
    def reset (self):
        self.current_state = self.initial_state
        self.input_symbol = None
        
    def set_register_state(self, in_state):
        #debug(in_state)
        pass
    
    def match_register_state(self, in_state):
        #debug(in_state)
        pass

    
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



