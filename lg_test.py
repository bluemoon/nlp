import sys
import pprint
import linkGrammar
from fsm import FSM
import lg_fsm as lgFSM

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

## Wd(left, x) & Ss(y, z) & (x & y) -> subject(z, y)
## TO(x, y) -> todo(x, y)
## O(x, y) -> object(x, y)
## Wi(x, y) -> imperative(x, y)

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
        self.fsm.process_list(input)

class Grammar:
    def __init__(self):
        self.g = grammarFSM()
        self.g.fsm_setup()



def map_out((words,lengths,links,extra)):
    mapCharacter = '+'
    
    print words, lengths, links
    matrix = []
    for x in xrange(len(lengths)):
        matrix.append([])
        y = lambda y: matrix[x].append(links[x])
        map(y, range(lengths[x]))
    
    print matrix
    word_counter = lambda wc: reduce(lambda x,y: x+y, map(lambda x: len(x), wc))
    remap = lambda remap: reduce(lambda x,y: x+y, map(word_counter, remap))
    total_map = map(remap, matrix)
    print total_map
    ## Get the longest string length
    c_max_len = reduce(lambda x, y: max(x, y), total_map)
    c_max_row = reduce(max, lengths)
    i = 0
    for row in matrix:
        for subrow in row:
            for column in subrow:               
                    print column,
                    print '+',
                    
        if len(row) % c_max_row == 0: 
            print
            
        i += 1
        
    print
    

def draw_text((words, lengths, links)):
    i = 0
    pad_len = 4
    while len(links) >= i:
        l_pad_len = pad_len - len(links[i]) 
        try:
            r_pad_len = pad_len -len(links[i+1])
            
        except:
            return
        r_pad = r_pad_len * ' '
        l_pad = l_pad_len * ' '
        
        print '%d %s%s   %s' % (lengths[i], links[i], l_pad, words[i])
        i += 1
    print
    
def relation((words, lengths, links)):
    i = 0
    while i < len(words):
        try:
            links[i+1]
        except:
            return

        ## Regex:
        ##    (*, Wd) & (Ss, *) -> subject(v1, v2)
        ##
        #print words[i],
        #print links[i]
        #
        #print 'frame %d:' % (i),
        ## Wd(left, x) & Ss(y, z) & (x & y) -> subject(z, y)
        if links[i][1] == 'Wd' and links[i+1][0] == 'Ss':
            print 'frame %d:' % (i),
            print 'subject(%s, %s)' % (words[i], words[i+1])

        ## TO(x, y) -> todo(x, y)
        if links[i][0] == 'TO':
            print 'frame %d:' % (i),
            print 'todo(%s, %s) ' % (words[i-1], words[i+1])

        if links[i][0] == 'Ox':
            print 'frame %d:' % (i),
            print 'object(%s, %s)' % (words[i-1], words[i])
        ## O(x, y) -> object(x, y)
        if links[i][0] == 'O':
            print 'frame %d:' % (i),
            print 'object(%s, %s)' % (words[i-1], words[i+1])

        ## Wi(x, y) -> imperative(x, y)
        if links[i][0] == 'Wi' and links[i-1][0] == 'Wi':
            print 'frame %d:' % (i),
            print 'imperative(%s -> %s)' % (words[i-2], words[i])

        if links[i][0] == 'AF':
            print 'frame %d:' % (i),
            print 'object(%s, %s)' % (words[i+1], words[i-1])

        i += 1


def r_Const(const, input='', current=[]):
    #r_filter = lambda y: filter(lambda x: isinstance(x, list), y)
    #rmap = lambda y: map(lambda x:r_Const(x), y)
    #r_map = map(rmap, const)
    #print r_map
    #r2_map = map(lambda x: r_Const(x), r_map)
    for x in const:
        if isinstance(x, list):
            current.insert(0, len(x))
            output = r_Const(x, input, current)
            print output
        else:
            input += '('
            input += x

            cur = current.pop(0)
            cur -= 1
            
            if cur == 0:
                input += ')'
            else:
                current.insert(0, cur)
         
    for y in current:
        for z in xrange(y):
            input += ')'
            
    print input
    return input
    #if r_map:
    #    r_Const(r_map)
    
def const_analysis(const):
    r_Const(const)

    


g = grammarFSM()
g.fsm_setup()



v = linkGrammar.constituents("It's very hard to describe")
s = linkGrammar.sentence("It's very hard to describe")
print const_analysis(v)
#pprint.pprint(v)
print g.fsm_run(s[3])

#j = linkGrammar.sentence("how are you?")
c = linkGrammar.constituents("how are you?")
s = linkGrammar.sentence("how are you?")
const_analysis(c)
print g.fsm_run(s[3])



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
