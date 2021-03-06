# -*- coding: utf-8 -*-

## LAB [string]
## F_L[node] the word on the left side of the link 
## F_R[node] the word on the right side of the link
## name: points to a string value for the name of the refent.
## tense: if the referent is a verb/event, points to a string value representing a tense
## HYP: if the referent is a verb/event, points to a string with value “T” iff the event is hypothetical.
## TRUTH-QUERY-FLAG: if the referent is a verb/event, points to a string with value “T” iff the event a question (i.e., 'eat' in “Did John eat the cake?”).
## COPULA-QUERY-FLAG: Points to the string “T” for particular entities involved in particular forms of copula questions (i.e., 'John' in “Who is john?”).
## noun_number: if the referent is a noun/thing, points to a string value representing a noun number
## links: points to a a feature node, with features representing the dependency relations in which this referent is the first argument.
## memberN: if the referent represents a group of things, it will contain only memberN features where N is an integer, and the memberN feature points to the Nth member in the group. 

semantic_rules = {
 'ADJ1': {'set': ['<F_R BACKGROUND-FLAG> = T',
                  '<F_R ref links _amod> += <F_L ref>'],
          'regex': ['= A\.*|DT\.*'],
          'match': []},
 'ADJ2': {'set': ['<F_L BACKGROUND-FLAG> = T',
                       '<F_L ref links _amod> += <F_R ref>'],
          'regex': ['=  Mp\.*| MVp\.*| Ma\.*'],
          'match': ['<F_R PREP-OBJ> = %']},
 'ADV1': {'set': ['<F_L head-word BACKGROUND-FLAG> = T',
                       '<F_L head-word ref links _advmod> += <F_R ref>'],
          'regex': ['= MVa\.*|EB\.*', '!= EBx\.*'],
          'match': ['<F_R str> != not', '<F_L head-word> != %']},
 'ADV2': {'set': ['<F_R head-word BACKGROUND-FLAG> = T',
                       '<F_R head-word ref links _advmod> += <F_L ref>'],
          'regex': ['= E\.*|EA\.*', '!= EA[my]\.*'],
          'match': ['<F_R head-word ref> != %']},
 'ADV2_HEADLESS': {'set': ['<F_R BACKGROUND-FLAG> = T',
                                '<F_R ref links _advmod> += <F_L ref>'],
                   'regex': ['= E\.*|EA\.*', '!= EA[my]\.*'],
                   'match': ['<F_R head-word ref> = %']},
 'ADV3': {'set': ['<F_R BACKGROUND-FLAG> = T',
                       '<F_R ref links _advmod> += <F_L ref>'],
          'regex': ['= EE\.* | EA'],
          'match': []},
 'ADV4': {'set': ['<F_L POS> = adv',
                       '<F_R head-word BACKGROUND-FLAG> = T',
                       '<F_R head-word ref links _advmod> += <F_L ref>'],
          'regex': ['= CO\.*'],
          'match': ['<F_L obj> = %', '<F_L head-word> = %']},
 'APPO_LEFT': {'set': ['<F_R ref links _nn> += <F_L ref>'],
               'regex': ['= GN\.*'],
               'match': []},
 'APPO_RIGHT': {'set': ['<F_L ref links _appo> += <F_R ref>'],
                'regex': ['= MX|MXs|MXp'],
                'match': []},
 'CLEAN_UP_BAD_REFS1': {'set': ['<GOOD-REF-FLAG> = T'],
                        'regex': [],
                        'match': ['<ref name> != %']},
 'CLEAN_UP_BAD_REFS2': {'set': ['<ref> = %'],
                        'regex': [],
                        'match': ['<GOOD-REF-FLAG> != T', '<ref> != %']},
 'COMPARATIVE_OBJ1': {'set': ['<F_L comparative-obj-word> = <F_R>'],
                      'regex': ['=  U\.c\.*| O\.c\.*'],
                      'match': ['<F_L str> = than|as']},
 'COMPARATIVE_OBJ2': {'set': ['<F_L comparative-obj-word> = <F_R comparative-obj-word>'],
                      'regex': ['=  MV[tz]\.*'],
                      'match': ['<F_R comparative-obj-word> != % ']},
 'COMPARATIVE_OBJ3A': {'set': ['<F_R comparative-cvar name> = _$cVar',
                                    '<F_R comparative-cvar links _$crVar> = <F_L comparative-obj-word ref>'],
                       'regex': ['=  O\.*'],
                       'match': ['<F_R COMP-SUBJ-FLAG> = T']},
 'COMPARATIVE_OBJECT_FINAL': {'set': [],
                              'regex': [],
                              'match': ['<COMP-SUBJ-FLAG> = T',
                                      '<this> = $modified',
                                      '<comparative-relation-word ref name> = $prep',
                                      '<comparative-relation-word> = $prep_source',
                                      '<comparative-cvar> = $prep_obj']},
 'COMPARATIVE_RELATION1': {'set': ['<F_R comparative-relation-word> = <F_L>',
                                        '<F_R COMP-SUBJ-FLAG> = T'],
                           'regex': ['=  D\.\.[my]\.*'],
                           'match': []},
 'COPULA_QUESTION1': {'set': ['<head> = %',
                                   '<head> = $O',
                                   '<head COPULA-QUESTION-FLAG> = T'],
                      'regex': [],
                      'match': ['<head name> = be',
                              '<head links _subj name> = _$qVar',
                              '<head links _obj> = $O']},
 'COPY_POS_TO_REF': {'set': ['<ref pos> = <POS>'],
                     'regex': [],
                     'match': ['<POS> != %']},
 'DECLARATIVE_QUESTION1': {'set': ['<F_L punc> = <F_R str>'],
                           'regex': ['=  Xp\.*'],
                           'match': []},
 'DECLARATIVE_QUESTION2': {'set': ['<F_R head-word ref TRUTH-QUERY-FLAG> = T',
                                        '<F_R head-word ref HYP> = T',
                                        '<F_L wall sentence_type> = QUERY'],
                           'regex': ['=  Wd\.*'],
                           'match': ['<F_L punc> =  [  ?]',
                                   '<F_L head-word> != %']},
 'DIR_OBJ1': {'set': ['<F_L OBJ-LINK-TAG> = O',
                           '<F_L obj> += <F_R ref>'],
              'regex': ['=  O\.*| OD\.*| OT\.*',
                        '!=  O\.n\.*',
                        '!=  O\.i\.*'],
              'match': ['<F_L OBJ-LINK-TAG> = O|UNMATCH']},
 'DIR_OBJ2': {'set': ['<F_L OBJ-LINK-TAG> = O-n',
                           '<F_L obj> += <F_R ref>',
                           '<F_L iobj> += <F_R ref>'],
              'regex': ['=  O\.n\.*',
                        '!=  O\.i\.*',
                        '=  O\.n\.*',
                        '!=  O\.i\.*'],
              'match': ['<F_L OBJ-LINK-TAG> = O-n|UNMATCH',
                      '<F_L OBJ-LINK-TAG> != O-n|UNMATCH']},
 'DO_QUESTION1': {'set': ['<F_R obj> = %',
                               '<F_R ref name> = %',
                               '<F_R ref name> = _$qVar',
                               '<F_R ref QUERY-FLAG> = T'],
                  'regex': ['=  B.w'],
                  'match': ['<F_R str> = do']},
 'DROP_REF': {'set': ['<ref> = %'],
              'regex': [],
              'match': ['<ref DROP-REF-FLAG> = T']},
 'FILLER_FIX': {'set': ['<F_R subj> = <F_R obj>', '<F_R obj> = %'],
                'regex': ['=  Ix\.*| PPf\.*'],
                'match': ['<F_R subj> = %', '<F_R obj> != %']},
 'GER_OBJ': {'set': ['<F_R OBJ-LINK-TAG> = Mv',
                          '<F_R obj> += <F_L ref>'],
             'regex': ['=  Mv\.*'],
             'match': []},
 'HEAD-QUESTION-WHICH': {'set': ['<F_L head-question-word> += <F_R head-question-word>',
                                      '<F_L head-question-word> += <F_R head-word>'],
                         'regex': ['=  D\.\.w\.*', '=  D\.\.w\.*'],
                         'match': ['<F_R head-question-word> != %',
                                 '<F_R head-question-word> = %']},
 'HEAD-QUESTION-WORD': {'set': ['<F_L head-question-word> += <F_R head-word>'],
                        'regex': ['=  Rw\.*|Q'],
                        'match': []},
 'HEAD-QUESTION-WORD2': {'set': ['<F_L head-word> += <F_R head-question-word>'],
                         'regex': ['=  W[qs]\.*'],
                         'match': ['<F_R head-question-word> != %']},
 'HEAD-QUESTION-WORD2NULL': {'set': ['<F_L head-word> += <F_R head-word>'],
                             'regex': ['=  W[qs]\.*'],
                             'match': ['<F_R head-question-word> = %']},
 'HEAD-WORD_GROUP0': {'set': ['<head-word ref> += $R', '<head> += $R'],
                      'regex': [],
                      'match': ['<head-word member0 ref> = $R',
                              '<head-word member0 ref> = $R']},
 'HEAD-WORD_GROUP1': {'set': ['<head-word ref> += $R', '<head> += $R'],
                      'regex': [],
                      'match': ['<head-word member1 ref> = $R',
                              '<head-word member1 ref> = $R']},
 'HEAD-WORD_GROUP2': {'set': ['<head-word ref> += $R', '<head> += $R'],
                      'regex': [],
                      'match': ['<head-word member2 ref> = $R',
                              '<head-word member2 ref> = $R']},
 'HEAD-WORD_GROUP3': {'set': ['<head-word ref> += $R', '<head> += $R'],
                      'regex': [],
                      'match': ['<head-word member3 ref> = $R',
                              '<head-word member3 ref> = $R']},
 'HEAD-WORD_GROUP4': {'set': ['<head-word ref> += $R', '<head> += $R'],
                      'regex': [],
                      'match': ['<head-word member4 ref> = $R',
                              '<head-word member4 ref> = $R']},
 'HEAD-WORD_GROUP5': {'set': ['<head-word ref> += $R', '<head> += $R'],
                      'regex': [],
                      'match': ['<head-word member5 ref> = $R',
                              '<head-word member5 ref> = $R']},
 'HEAD-WORD_GROUP6': {'set': ['<head-word ref> += $R', '<head> += $R'],
                      'regex': [],
                      'match': ['<head-word member6 ref> = $R',
                              '<head-word member6 ref> = $R']},
 'HEAD_IDENTIFY': {'set': ['<HEAD-FLAG> = T'],
                   'regex': [],
                   'match': ['<tense> != %', '<tense MODAL-FLAG> = %']},
 'HEAD_INIT': {'set': ['<ref tense> = <tense name>'],
               'regex': [],
               'match': ['<HEAD-FLAG> = T']},
 'HEAD_TO_CLAUSE_AND_WALL': {'set': ['<F_L head-word> += <F_R head-word>'],
                             'regex': ['=  W\.*| C\.*| RS\.*| Qd\.*',
                                       '!=  C[ie]| Ct\.*',
                                       '!=  W[qs]\.*'],
                             'match': []},
 'HEAD_TO_FIRST_VERB': {'set': ['<tense first_verb head-word> += <this>'],
                        'regex': [],
                        'match': ['<HEAD-FLAG> = T']},
 'HEAD_TO_SUBJ_AND_OBJ1': {'set': ['<F_L head-word> += <F_R head-word>'],
                           'regex': ['=  S\.*| SX\.*| B.w\.*| SF\.*'],
                           'match': []},
 'HEAD_TO_SUBJ_AND_OBJ2': {'set': ['<F_L head-word> += <F_R head-word>'],
                           'regex': ['=  S\.*| SX\.*'],
                           'match': []},
 'HEAD_WORD_REF_TO_HEAD': {'set': ['<head> = $R'],
                           'regex': [],
                           'match': ['<head-word ref> = $R']},
 'HOW': {'set': ['<F_L ref name> = %',
                      '<F_L ref name> = _$qVar',
                      '<F_L ref QUERY-TYPE> = how',
                      '<F_L head-question-word ref links how> = <F_L ref>'],
         'regex': ['= Q'],
         'match': ['<F_L str> = How|how']},
 'HOW_BIG': {'set': ['<F_L ref name> = %',
                          '<F_L ref name> = _$qVar',
                          '<F_L ref QUERY-TYPE> = how_much',
                          '<F_R head-word ref HYP> = T'],
             'regex': ['=  EAh| EEh'],
             'match': ['<F_L str> = how']},
 'HOW_MUCH': {'set': ['<F_L ref name> = %',
                           '<F_L ref name> = _$qVar',
                           '<F_L ref QUERY-TYPE> = how_much',
                           '<F_L ref POLYWORD-FLAG> = %'],
              'regex': ['=  B.m'],
              'match': ['<F_L str> = how_much']},
 'HOW_MUCH2': {'set': ['<F_L ref name> = %',
                            '<F_L ref name> = _$qVar',
                            '<F_L ref QUERY-TYPE> = how_much',
                            '<F_L ref POLYWORD-FLAG> = %',
                            '<F_R head-word ref HYP> = T'],
               'regex': ['=  Dm.*'],
               'match': ['<F_L str> = how_much|how_many']},
 'HYP-IF': {'set': ['<if HYP> = T'], 'regex': [], 'match': ['<if> != %']},
 'HYP-THAT': {'set': ['<_that HYP> = T'],
              'regex': [],
              'match': ['<_that> != %']},
 'HYP-THAT2': {'set': ['<that HYP> = T'],
               'regex': [],
               'match': ['<that> != %']},
 'HYP-TO-BE': {'set': ['<_to-be HYP> = T'],
               'regex': [],
               'match': ['<_to-be> != %']},
 'HYP-TO-DO': {'set': ['<to-do HYP> = T'],
               'regex': [],
               'match': ['<to-do> != %']},
 'INDIR_OBJ1': {'set': ['<F_L iobj> += <F_R ref>'],
                'regex': ['=  O\.*| OD\.*| OT\.*',
                          '!=  O\.n\.*',
                          '!=  O\.i\.*'],
                'match': ['<F_L OBJ-LINK-TAG> != O|UNMATCH']},
 'INV-MARK_TOBE': {'set': ['<F_R TO-BE-FLAG> = T'],
                   'regex': ['=  AF\.*'],
                   'match': []},
 'INV-SUBJECT_LINKING': {'set': ['<F_L subj> = <F_R subj>'],
                         'regex': ['=  AF\.*'],
                         'match': ['<F_R obj> = %',
                                 '<F_R FILLER-OBJ-FLAG> != T']},
 'INVERTED_SUBJ': {'set': ['<F_L subj> += <F_R ref>'],
                   'regex': ['=  SI\.*| SXI\.*'],
                   'match': []},
 'INV_OBJECT_LINKING': {'set': ['<F_L subj> = <F_R obj>'],
                        'regex': ['=  AF\.*'],
                        'match': ['<F_R obj> != %']},
 'INV_TENSE_LIST_CONNECT2': {'set': ['<F_R tense MODAL-FLAG> = T',
                                          '<F_L tense first_verb> = <F_R tense first_verb>'],
                             'regex': [],
                             'match': ['<INV-TENSE-LINK-FLAG> = T']},
 'INV_TOBE': {'set': ['<F_R to-be> += <F_L ref>'],
              'regex': ['=  AF\.*'],
              'match': ['<F_R str> != be']},
 'MARK_FILLER_OBJ': {'set': ['<F_L FILLER-OBJ-FLAG> = T'],
                     'regex': ['=  OX\.*'],
                     'match': []},
 'MARK_TOBE': {'set': ['<F_L TO-BE-FLAG> = T'],
               'regex': ['=  Pa\.*'],
               'match': []},
 'MODIFYING_PHRASES_TO_BACKGROUND': {'set': ['<F_R BACKGROUND-FLAG> = T'],
                                     'regex': ['=  Mv\.*| Mg\.*'],
                                     'match': []},
 'NEGATIVE-IS-HYP': {'set': ['<HYP> = T'],
                     'regex': [],
                     'match': ['<NEGATIVE-FLAG> = T', '<HYP> = %']},
 'NEGATIVE1': {'set': ['<F_L tense first_verb head-word ref NEGATIVE-FLAG> += T'],
               'regex': ['=  N\.*| EB\.*'],
               'match': ['<F_R str> = not']},
 'NEGATIVE_CONTR1': {'set': ['<F_R tense first_verb head-word ref NEGATIVE-FLAG> += T'],
                     'regex': ['=  I\.*| PP\.*| P\.*'],
                     'match': ["<F_L orig_str> = didn't|doesn't|don't|won't|weren't|aren't|isn't|wasn't|hasn't|haven't|hadn't",
                             '<F_L tense first_verb head-word name> != _%copula']},
 'NEGATIVE_CONTR2': {'set': ['<F_L tense first_verb head-word ref NEGATIVE-FLAG> += T'],
                     'regex': ['=  P\.*'],
                     'match': ["<F_L orig_str> = weren't|aren't|isn't|wasn't",
                             '<F_L tense first_verb head-word name> = _%copula']},
 'NEGATIVE_CONTR3': {'set': ['<F_L tense first_verb head-word ref NEGATIVE-FLAG> += T'],
                     'regex': ['=  I\.*| O\.*'],
                     'match': ["<F_L orig_str> = can't|cannot|wouldn't|shouldn't|couldn't|hadn't|haven't|hasn't"]},
 'NEGATIVE_INF1': {'set': ['<F_R NEG-SYN-FLAG> = T'],
                   'regex': ['=  NT\.*'],
                   'match': ['<F_L str> = not']},
 'NEGATIVE_INF2': {'set': ['<F_R tense first_verb head-word ref NEGATIVE-FLAG> += T'],
                   'regex': ['=  I\.*'],
                   'match': ['<F_L NEG-SYN-FLAG> = T']},
 'NOUN-MOD': {'set': ['<F_R ref links _nn> += <F_L ref>',
                           '<F_R BACKGROUND-FLAG> = T'],
              'regex': ['=  AN\.*'],
              'match': []},
 'NUMBER-1': {'set': ['<F_R ref links _%quantity> = <F_L ref>'],
              'regex': ['=  D\.*| ND\.*| NW\.*',
                        '!=  D..y',
                        '!=  D..w'],
              'match': ['<F_L DETERMINER_FLAG> != T',
                      '<F_L QUERY_INDEFINATE_DETERMINER_FLAG> != T',
                      '<F_L POSSESSIVE-FLAG> != T',
                      '<F_L QUANTITY-EXCEPTION-FLAG> != T']},
 'NUMBER-MOD': {'set': ['<F_R ref links _%quantity_mod> = <F_L ref>'],
                'regex': ['=  EN\.*'],
                'match': []},
 'NUMBER-MULT': {'set': ['<F_R ref links _%quantity_mult> = <F_L ref>'],
                 'regex': ['=  NN\.*'],
                 'match': []},
 'OBJ-LINK-TAG-INIT1': {'set': ['<F_R OBJ-LINK-TAG> = UNMATCH'],
                        'regex': ['=  Mv\.*| Pv\.*| B\.*| BW\.*'],
                        'match': ['<F_R RS-FLAG> != T']},
 'OBJ-LINK-TAG-INIT2': {'set': ['<F_L OBJ-LINK-TAG> = UNMATCH'],
                        'regex': ['=  O\.*| OD\.*| OT\.*'],
                        'match': []},
 'OBJ2_TO_LINKS': {'set': ['<ref links _iobj> = <iobj>'],
                   'regex': [],
                   'match': ['<HEAD-FLAG> = T', '<iobj> != %']},
 'OBJ2_TO_LINKS_GERUND': {'set': ['<ref links _iobj> = <iobj>'],
                          'regex': [],
                          'match': ['<POS> = noun', '<iobj> != %']},
 'OBJECT_LINKING': {'set': ['<F_R subj> = <F_L obj>'],
                    'regex': ['=  Pg\.*| Pa\.*| Pp\.*| PP\.*| I\.*'],
                    'match': ['<F_L obj> != %']},
 'OBJECT_LINKING_TO': {'set': ['<F_R subj> = <F_L obj>'],
                       'regex': ['=  TO\.*| MVi\.*'],
                       'match': ['<F_L str> != be',
                               '<F_L obj> != %',
                               '<F_L ADJ-OBJ-FLAG> = %']},
 'OBJ_TO_LINKS': {'set': ['<ref links _obj> = <obj>'],
                  'regex': [],
                  'match': ['<HEAD-FLAG> = T', '<obj> != %']},
 'OBJ_TO_LINKS_GERUND': {'set': ['<ref links _obj> = <obj>'],
                         'regex': [],
                         'match': ['<POS> = noun', '<obj> != %']},
 'PAREN_1': {'set': ['<F_R head-word BACKGROUND-FLAG> = T'],
             'regex': ['=  MX.[rj]\.*'],
             'match': []},
 'PASSIVE_OBJ_LINK': {'set': ['<F_R obj> = <F_L subj>'],
                      'regex': ['=  Pv\.*'],
                      'match': []},
 'PASS_OBJ': {'set': ['<F_R OBJ-LINK-TAG> = Pv'],
              'regex': ['=  Pv\.*'],
              'match': []},
 'POSSRDET_TO_GERUND': {'set': ['<F_R ref links _poss> += <F_L ref>'],
                        'regex': ['=  DP\.*'],
                        'match': []},
 'POSSR_TO_APOSTROPHE': {'set': ['<F_R possessor> += <F_L ref>'],
                         'regex': ['=  YS\.* | YP\.*'],
                         'match': []},
 'POSSR_TO_DET': {'set': ['<F_R ref links _poss> += <F_L ref>'],
                  'regex': ['=  D\.*'],
                  'match': ['<F_L POSSESSIVE-FLAG> = T']},
 'POSSR_TO_POSS': {'set': ['<F_R ref links _poss> += <F_L possessor>'],
                   'regex': ['=  D\.*'],
                   'match': ['<F_L possessor> != %']},
 'PRECEEDING_PREP_CLAUSE_OBJECT': {'set': [],
                                   'regex': ['=  CO..\.*'],
                                   'match': ['<F_R head-word> = $modified',
                                           '<F_L str> = $prep',
                                           '<F_L> = $prep_source',
                                           '<F_L head-word ref> = $prep_obj']},
 'PRECEEDING_PREP_LINK': {'set': [],
                          'regex': ['=  CO\.*| Qd\.*'],
                          'match': ['<F_L PREP-OBJ> = T',
                                  '<F_R head-word> = $modified',
                                  '<F_L str> = $prep',
                                  '<F_L> = $prep_source',
                                  '<F_L obj> = $prep_obj']},
 'PREDICATIVE_ADJECTIVE_LINKING': {'set': ['<F_L subj links _predadj> = <F_R ref>'],
                                   'regex': ['=  Pa\.*'],
                                   'match': ['<F_L obj> = %',
                                           '<F_L FILLER-OBJ-FLAG> != T',
                                           '<F_L str> = be']},
 'PREPOSITION_MARKING': {'set': ['<F_L ref name> = %',
                                      '<F_L ref name> = _%copula'],
                         'regex': ['=  Pp\.*'],
                         'match': ['<F_L str> = be']},
 'PREP_CLAUSE_LINKING': {'set': [],
                         'regex': ['=  Mp\.*| MVp\.*| MX.x\.*| OF\.*| MG\.*| LI\.*| Pp\.*'],
                         'match': ['<F_R head-word> !=%',
                                 '<F_L> = $modified',
                                 '<F_R str> = $prep',
                                 '<F_R> = $prep_source',
                                 '<F_R head-word ref> = $prep_obj']},
 'PREP_CLAUSE_LINKING_WHERE': {'set': ['<F_L head-word> += <F_R>'],
                               'regex': ['=  WR\.*'],
                               'match': ['<F_L ref QUERY-TYPE> = %']},
 'PREP_CLAUSE_OBJECT': {'set': [],
                        'regex': ['= MVs| TH\.*| WN\.*'],
                        'match': ['<F_L head-word> != %',
                                '<F_L head-word> = $modified',
                                '<F_R str> = $prep',
                                '<F_R> = $prep_source',
                                '<F_R head-word ref> = $prep_obj']},
 'PREP_CLAUSE_OBJECT2': {'set': [],
                         'regex': ['= MVs| TH\.*| WN\.*'],
                         'match': ['<F_L head-word> = %',
                                 '<F_L> = $modified',
                                 '<F_R str> = $prep',
                                 '<F_R> = $prep_source',
                                 '<F_R head-word ref> = $prep_obj']},
 'PREP_LINKING': {'set': [],
                  'regex': ['=  Mp\.*| MVp\.*| MX.x\.*| OF\.*| MG\.*| LI\.*| Pp\.*',
                            '=  MVi\.*'],
                  'match': ['<F_R head-word> = %',
                          '<F_L> = $modified',
                          '<F_R str> = $prep',
                          '<F_R> = $prep_source',
                          '<F_R obj> = $prep_obj',
                          '<F_L> = $modified',
                          '<F_R str> = $prep',
                          '<F_R> = $prep_source',
                          '<F_R to-do> = $prep_obj']},
 'PREP_OBJ': {'set': ['<F_L obj> += <F_R ref>'],
              'regex': [],
              'match': ['<PREP-OBJ-LINK-FLAG> = T']},
 'PREP_RELATIVE_BACKGROUND': {'set': ['<F_L background ref> += <F_R head-word ref>',
                                           '<F_L background wall> = <F_L wall>',
                                           '<F_L background BACKGROUND-FLAG> = T'],
                              'regex': ['=  Mj\.*| MX.j\.*'],
                              'match': []},
 'PREP_RELATIVE_LINK': {'set': [],
                        'regex': ['=  Mj\.*| MX.j\.*'],
                        'match': ['<F_R head-word> = $modified',
                                '<F_R str> = $prep',
                                '<F_R> = $prep_source',
                                '<F_R obj> = $prep_obj']},
 'PROPOGATE_HEAD-WORD': {'set': ['<head-word> = $Z'],
                         'regex': [],
                         'match': ['<tense first_verb head-word> = $Z']},
 'QUANTITY_EXCEPTION': {'set': ['<F_L QUANTITY-EXCEPTION-FLAG> = T'],
                        'regex': ['=  D\.*| DD\.*'],
                        'match': ["<F_L str> = more|More|'s|fewer|Fewer"]},
 'QUERY_INDEFINATE_DETERMINER1': {'set': ['<F_L QUERY_INDEFINATE_DETERMINER_FLAG> = T'],
                                  'regex': ['=  D\.*| DD\.*'],
                                  'match': ['<F_L wall sentence_type> = QUERY',
                                          '<F_L str> = a|A|an|An|some|Some|any|Any']},
 'QUERY_INDEFINATE_DETERMINER2': {'set': ['<F_R ref TRUTH-QUERY-FLAG> = T'],
                                  'regex': ['=  D\.*| DD\.*'],
                                  'match': ['<F_L QUERY_INDEFINATE_DETERMINER_FLAG> = T']},
 'QUESTION-ID': {'set': ['<F_L wall sentence_type> = QUERY'],
                 'regex': ['=  Q\.*'],
                 'match': []},
 'QUESTION2': {'set': ['<F_R ref QUERY-FLAG> = T',
                            '<F_L wall sentence_type> = QUERY'],
               'regex': ['=  D\.\.w\.*'],
               'match': []},
 'QUESTION3_DO': {'set': ['<F_R head-word ref TRUTH-QUERY-FLAG> = T',
                               '<F_R head-word ref HYP> = T'],
                  'regex': ['=  Qd\.*'],
                  'match': ['<F_L str> = LEFT-WALL']},
 'QUESTIONS-COPULA': {'set': ['<F_L head-question-word ref name> = %',
                                   '<F_L head-question-word ref name> = _%copula'],
                      'regex': ['= Q'],
                      'match': ['<F_L head-question-word str> = be',
                              '<F_L head-question-word obj> = %']},
 'RELATIVE_CLAUSE_TO_BACKGROUND': {'set': ['<F_L background ref> += <F_R head-word ref>',
                                                '<F_L background wall> = <F_L wall>',
                                                '<F_L background BACKGROUND-FLAG> = T'],
                                   'regex': ['=  R\.*', '!=  Rw\.*'],
                                   'match': []},
 'REL_INDIR_OBJ': {'set': ['<F_R iobj> += <F_L ref>'],
                   'regex': ['= B\.*| BW\.*'],
                   'match': ['<F_R RS-FLAG> != T',
                           '<F_R OBJ-LINK-TAG> != B|UNMATCH']},
 'REL_OBJ': {'set': ['<F_R OBJ-LINK-TAG> = B', '<F_R obj> += <F_L ref>'],
             'regex': ['= B\.*|BW\.*'],
             'match': ['<F_R RS-FLAG> != T', '<F_R OBJ-LINK-TAG> = B|UNMATCH']},
 'REL_SUBJ': {'set': ['<F_R REL-SUBJ-FLAG> = T',
                           '<F_R subj> += <F_L ref>'],
              'regex': ['= B\.*|BW\.*'],
              'match': ['<F_R RS-FLAG> = T']},
 'SPECIAL-ADJ': {'set': ['<F_R obj> = %',
                              '<F_R obj> = <F_L subj>',
                              '<F_L ADJ-OBJ-FLAG> = T'],
                 'regex': ['= B\.*|BW\.*'],
                 'match': ['<F_L POS> = adj']},
 'SPECIAL_PREP_RULE': {'set': ['<F_R ref SPECIAL-PREP-FLAG> = T',
                                    '<F_R ref links _psubj> = <F_R ref links _subj> ',
                                    '<F_R ref links _pobj> = <F_R ref links _obj>',
                                    '<F_R ref links _subj> = %',
                                    '<F_R ref links _obj> = %'],
                       'regex': ['= Pp\.*'],
                       'match': ['<F_L str> = be',
                               '<F_R ref links _subj> != %',
                               '<F_R ref links _obj> != %']},
 'SPECIAL_PREP_RULE_WHEN': {'set': ['<F_L ref name> = %',
                                         '<F_L ref name> = _%atTime'],
                            'regex': ['= PF\.*'],
                            'match': ['<F_L str> = when']},
 'SPECIAL_PREP_RULE_WHEN_WHEN': {'set': ['<F_L ref SPECIAL-PREP-FLAG> = T',
                                              '<F_L ref links _psubj> = <F_R ref links _subj>',
                                              '<F_L ref links _pobj name> = _$qVar',
                                              '<F_L ref links _pobj nameSource> = %',
                                              '<F_L ref links _pobj nameSource> = <F_L>',
                                              '<F_L ref links _pobj QUERY-TYPE> = when',
                                              '<F_L ref tense> = <F_R ref tense>',
                                              '<F_L head-word> = <F_L>'],
                                 'regex': ['= PF\.*'],
                                 'match': ['<F_L str> = when']},
 'SPECIAL_PREP_RULE_WHERE': {'set': ['<F_L ref name> = %',
                                          '<F_L ref name> = _%atLocation'],
                             'regex': ['= PF\.*'],
                             'match': ['<F_L str> = where']},
 'SPECIAL_PREP_RULE_WHERE_WHERE': {'set': ['<F_L ref SPECIAL-PREP-FLAG> = T',
                                                '<F_L ref links _psubj> = <F_R ref links _subj>',
                                                '<F_L ref links _pobj name> = _$qVar',
                                                '<F_L ref links _pobj nameSource> = %',
                                                '<F_L ref links _pobj nameSource> = <F_L>',
                                                '<F_L ref links _pobj QUERY-TYPE> = where',
                                                '<F_L ref tense> = <F_R ref tense>',
                                                '<F_L head-word> = <F_L>'],
                                   'regex': ['= PF\.*'],
                                   'match': ['<F_L str> = where']},
 'STANDARD_SUBJ': {'set': ['<F_R subj> += <F_L ref>'],
                   'regex': ['= S\.*|SX\.*|Mg\.*|MX\.*',
                             '!= MX.[rj]\.*',
                             '!= MX|MXs|MXp'],
                   'match': []},
 'SUBJECT_LINKING': {'set': ['<F_R subj> = <F_L subj>'],
                     'regex': ['= Pg\.*|Pp\.*|PP\.*|I\.*'],
                     'match': ['<F_L obj> = %', '<F_L FILLER-OBJ-FLAG> != T']},
 'SUBJECT_LINKING_TO': {'set': ['<F_R subj> = <F_L subj>'],
                        'regex': ['=  TO\.*| MVi\.*'],
                        'match': ['<F_L str> != be',
                                '<F_L obj> = %',
                                '<F_L ADJ-OBJ-FLAG> = %']},
 'SUBJ_TO_LINKS': {'set': ['<ref links _subj> = <subj>'],
                   'regex': [],
                   'match': ['<HEAD-FLAG> = T', '<subj> != %']},
 'SUPERLATIVE-1': {'set': ['<F_L det-mod> += <F_R ref>'],
                   'regex': ['= L\.*'],
                   'match': []},
 'SUPERLATIVE-2': {'set': ['<F_R BACKGROUND-FLAG> = T',
                                '<F_R ref links _amod> += <F_L det-mod>'],
                   'regex': ['= D\.*| DD\.*'],
                   'match': ['<F_L det-mod> != %']},
 'SUPERLATIVE-3': {'set': ['<F_R ref SUPERLATIVE-FLAG> = T'],
                   'regex': ['=  L\.*'],
                   'match': ['<F_R str> != <F_R orig_str>']},
 'TENSE_CONJOIN': {'set': [], 'regex': [], 'match': ['<HEAD-FLAG> = T']},
 'TENSE_LIST_CONNECT1': {'set': ['<tense first_verb> = <this>'],
                         'regex': [],
                         'match': ['<tense prev> = %', '<tense> = $T']},
 'TENSE_LIST_CONNECT2': {'set': ['<F_L tense MODAL-FLAG> = T',
                                      '<F_R tense first_verb> = <F_L tense first_verb>'],
                         'regex': [],
                         'match': ['<TENSE-LINK-FLAG> = T']},
 'THAT1': {'set': ['<F_L that> += <F_R head-word ref>'],
           'regex': ['=  C[ei]\.*', '!= Cet\.*'],
           'match': []},
 'THAT_TO_LINKS': {'set': ['<ref links _that> = <that>'],
                   'regex': [],
                   'match': ['<str> != %', '<str> != that', '<that> != %']},
 'TOBE-TOINF': {'set': ['<F_L to-be> += <F_R head-word ref>'],
                'regex': ['= I\.*'],
                'match': ['<F_R TO-BE-FLAG> = T']},
 'TOBE1': {'set': ['<F_L to-be> += <F_R ref>'],
           'regex': ['= Pa\.*'],
           'match': ['<F_L str> != be', '<F_R head-word> = %']},
 'TOBE1z': {'set': ['<F_L to-be> += <F_R head-word ref>'],
            'regex': ['= Pa\.*'],
            'match': ['<F_L str> != be', '<F_R head-word> != %']},
 'TOBE2': {'set': ['<F_L to-be> += <F_R to-be>'],
           'regex': ['= TO\.*'],
           'match': ['<F_R to-be> != %']},
 'TOBE_TO_LINKS': {'set': ['<ref links _to-be> = <to-be>'],
                   'regex': [],
                   'match': ['<HEAD-FLAG> = T', '<to-be> != %']},
 'TODO1z': {'set': ['<F_L to-do> += <F_R head-word ref>'],
            'regex': ['= I\.*|Pg\.*', '!= Pg*b'],
            'match': ['<F_R TO-BE-FLAG> != T']},
 'TODO2': {'set': ['<F_L to-do> += <F_R to-do>'],
           'regex': ['= TO\.*'],
           'match': ['<F_R to-do> != %']},
 'TODO_TO_LINKS': {'set': ['<ref links _to-do> = <to-do>'],
                   'regex': [],
                   'match': ['<HEAD-FLAG> = T', '<to-do> != %']},
 'TODO_TO_LINK_FOR_NOUNS': {'set': ['<ref links _to-do> = <to-do>'],
                            'regex': [],
                            'match': ['<POS> = noun', '<to-do> != %']},
 'WALL_BACKGROUND': {'set': ['<wall background> += <ref>'],
                     'regex': [],
                     'match': ['<BACKGROUND-FLAG> = T']},
 'WHEN': {'set': ['<F_L ref name> = %',
                       '<F_L ref name> = _$qVar',
                       '<F_L ref QUERY-TYPE> = when',
                       '<F_L head-question-word ref links _%atTime> = <F_L ref>'],
          'regex': ['= Q'],
          'match': ['<F_L str> = When|when']},
 'WHERE1': {'set': ['<F_L ref name> = %',
                         '<F_L ref name> = _$qVar',
                         '<F_L ref QUERY-TYPE> = where',
                         '<F_L head-question-word ref links _%atLocation> = <F_L ref>'],
            'regex': ['= Q'],
            'match': ['<F_L str> = Where|where']},
 'WHERE2': {'set': ['<F_R ref links _%atLocation> = <F_L ref>'],
            'regex': ['= WR\.*'],
            'match': ['<F_L ref QUERY-TYPE> = where']},
 'WHERE2q': {'set': ['<F_R ref name> = %',
                          '<F_R ref name> = _$qVar',
                          '<F_L ref QUERY-TYPE> = where'],
             'regex': ['= Wq\.*'],
             'match': ['<F_R str> = Where|where']},
 'WHERE_HACK_FOR_QP': {'set': ['<F_L head-question-word ref links _to-do links _%atLocation> = <F_L head-question-word ref links _%atLocation>',
                                    '<F_L head-question-word ref links _%atLocation> = %'],
                       'regex': ['= Q'],
                       'match': ['<F_L str> = Where|where',
                               '<F_L ref QUERY-TYPE> = where',
                               '<F_L head-question-word ref links _%atLocation> != %',
                               '<F_L head-question-word ref links _to-do> != %']},
 'WHY': {'set': ['<F_L ref name> = %',
                      '<F_L ref name> = _$qVar',
                      '<F_L ref QUERY-TYPE> = why',
                      '<F_L head-question-word ref links _%because> = <F_L ref>'],
         'regex': ['= Q'],
         'match': ['<F_L str> = Why|why', '<F_L head-question-word> != %']},
 'WILL_TODO': {'set': ['<DROP-REF-FLAG> = T'],
               'regex': [],
               'match': ['<links _to-do> != %',
                       '<links _subj> != %',
                       '<name> = go',
                       '<HYP> = T',
                       '<tense> = present_progressive']},
 'WILL_TODO_FUTURE': {'set': ['<NEXT NEXT head tense> = future'],
                      'regex': [],
                      'match': ['<head DROP-REF-FLAG> = T',
                              '<NEXT NEXT head tense> = infinitive']}}
