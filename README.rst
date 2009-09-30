Overview
========
An interface to link grammar to build and extend the idea

Semantic Matching
=================
For the semantic matching i have a set rules, the input tags are run through 
a non-deterministic finite state machine that keeps left and right registers.
The rule sets are as follows, each rule has a regular expression to match to,
it also has a set of registers to match to and then set if they match.

Semantic rule tokenizing
========================
I have another non-deterministic finite state machine(read: regex finite state
machine) to parse the rules that were taken from RelEx into something that is
manageable.

Pre-requisites
==============
- Python 2.5+
- Link Grammar (newest)

File Overview
=============
- debug.py          -- for the pretty print debug function
- grammar_fsm.py    -- contains the FSM for the semantics
- help.py           -- will contain help in the future
- lg_fsm.py         -- the old finite state machine for link grammar
- lg_py.c           -- the C module
- lg_test.py        -- the core file currently
- semantic_rules.py -- contains all the semantic rules
- semantics.py      -- parser to retrieve the semantic rules from RelEx
- setup.py          -- to compile the C module

TO-DO
=====
- [x] Hypergraph data structure (atoms)
- [x] Atom algorithms
- [x] Tree printer
- [x] Generic sentence container
- [/] Rule engine
-  -- [x] "Feature paths"
- [ ] Support vector machine for analysis
- [ ] Rule engine output analyzer
- [x] Implement part of speech tagger
- [ ] Word tense tagger
- [ ] Emoticon tagger
- [ ] Frame analysis
- -- [ ] Rete algorithm
- [ ] First order logic prover integration
- [ ] Spelling correction (pre-link grammar)
- [ ] Hobbs anaphora [Hobbs1976]



- http://code.google.com/p/hobbs-algorithm/source/browse/#svn/trunk

License
=======
Copyright (C) 2009 Alex Toney

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
