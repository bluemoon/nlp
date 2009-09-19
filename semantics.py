## STANDARD SUBJ
##   subj += ref
##   S.*|SX.*|Mg.*|Mx.*
##   #and not
##   Mx.[rj].*
##   MX|MXs|MXp
## INVERTED SUBJ
##   subj += ref
##   SI.*|SXI.
## RELATIVE SUBJ
##   subj += ref
##   RS-FLAG = T
##   REL-SUBJ-FLAG = T
##   B.*|\BW.*
## OBJ LINK TAG INIT 1
##   RS-FLAG != T
##   OBJ-LINK-TAG = UNSET
##   Mv.*|Pv.*|B.*|BW.*
## OBJ LINK TAG INIT 2
##   OBJ-LINK-TAG = UNSET
##   O.*|OD.*|OT.*
## GERUND OBJ
##   OBJ-LINK-TAG = Mv
##   Mv.*
## PASSIVE OBJ
##   OBJ-LINK-TAG = Pv
##   Pv.*
## DIRECT OBJ 1
import pprint
from Plex import *

s_letter     = Range("AZaz")
s_upper      = Range("AZ")
s_digit      = Range("09")
s_eol        = Any('\r\n')
s_dash       = Str("-")
s_underscore = Str("_")
s_number     = Rep1(s_digit)
s_comment_1  = Str(";") + Rep(AnyBut("\n"))
s_comment_2  = Str("#") + Rep(AnyBut("\n"))
s_title      = Rep1(s_letter|s_underscore|s_digit|s_dash) + s_eol
s_space      = Any(" \t\n")
s_regex      = Str("<LAB>") + Rep(AnyBut("\n"))
s_equal      = Str("=") + s_eol
s_set        = Str("<") + Rep(AnyBut("\n"))



lexicon = Lexicon([
  (s_space,        IGNORE),
  (s_comment_1,      'comment'),
  (s_comment_2,      'comment'),
  (s_title,        'title'),
  (s_regex,        'regex'),
  (s_equal,        'equal'),
  (s_set,          'set')
])

filename = "data/semantic-rules.txt"
f = open(filename, "r")
scanner = Scanner(lexicon, f, filename)
last_title = []
output = {}
after_equal = False
while 1:
  token = scanner.read()
  if token[0] == 'title':
      after_equal = False
      last_title.append(token[1][:-1])
      if not output.has_key(token[1][:-1]):
          output[token[1][:-1]] = {'regex':[],'set':[], 'after_eq':[]}
          
  elif token[0] == 'regex':
      output[last_title[-1]]['regex'].append(token[1][6:-1])
  elif token[0] == 'set':
      if not after_equal:
          output[last_title[-1]]['set'].append(token[1][:-1])
      else:
          output[last_title[-1]]['after_eq'].append(token[1][:-1])
  elif token[0] == 'equal':
      after_equal = True
  if token[0] is None:
    break

pprint.pprint(output)
