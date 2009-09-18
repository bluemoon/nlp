#!/usr/bin/python25

'''
Copyright (c) 2007, Kevin Scott 
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
     * Redistributions of source code must retain the above copyright
       notice, this list of conditions and the following disclaimer.
     * Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.     * The name of the author may be used to endorse or promote products
       derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY <copyright holder> ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <copyright holder> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import BitVector
import math
import random
from mm_hash import murmurHash

def hashpjw(s):
  Mhash = murmurHash(s, 64, 3141)
  #print Mhash
  return Mhash

class BloomFilter:
  def __init__(self, m, k):
    """Instantiate an m-bit Bloom filter using k hash indices per value."""
    self.n = 0
    self.m = m
    self.k = k
    self.bv = BitVector.BitVector(size = self.m)
    self.bits_in_inserted_values = 0

  def _HashIndices(self, s):
    """Hash s into k bit-vector indices for an m-bit Bloom filter."""
    indices = []
    for i in xrange(1, self.k + 1):
      indices.append((hash(s) + i * hashpjw(s)) % self.m)
    return indices

  def Insert(self, s):
    """Insert s into the Bloom filter."""
    for i in self._HashIndices(s): 
      self.bv[i] = 1
    self.n += 1
    self.bits_in_inserted_values += 8 * len(s)

  def InFilter(self, s):
    """Return True if s is in the Bloom filter."""
    for i in self._HashIndices(s):
      if self.bv[i] != 1:
        return False
    return True

  def PrintStats(self):
    k = float(self.k)
    m = float(self.m)
    n = float(self.n)
    p_fp = math.pow(1.0 - math.exp(-(k * n) / m), k) * 100.0
    compression_ratio = float(self.bits_in_inserted_values) / m
    print "Number of filter bits (m) : %d" % self.m
    print "Number of filter elements (n) : %d" % self.n
    print "Number of filter hashes (k) : %d" % self.k
    print "Predicted false positive rate = %.2f" % p_fp
    print "Compression ratio = %.2f" % compression_ratio

def TestBloomFilter():
  import random
  holdback = set()
  bf = BloomFilter(109017700, 32)
  #f = open('data/words.dat')
  #for line in f:
  #  val = line.rstrip()
  #  if random.random() <= 0.10:
  #    holdback.add(val)
  #  else:
  #    bf.Insert(val)
  #f.close()
  bf.PrintStats()
  #num_false_positives = 0
  #for val in holdback:
  #  if bf.InFilter(val):
  #    num_false_positives += 1
  #rate = 100.0 * float(num_false_positives) / float(len(holdback))
  #print "Actual false positive rate = %.2f%% (%d of %d)" % (rate, 
  #    num_false_positives, len(holdback))

if __name__ == '__main__':
  TestBloomFilter()
