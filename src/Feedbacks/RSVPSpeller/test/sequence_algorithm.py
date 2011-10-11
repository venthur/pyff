__copyright__ = """ Copyright (c) 2010 Torsten Schmits, Laura Acqualagna

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this
program; if not, see <http://www.gnu.org/licenses/>.

"""

import copy
import random

from unittest import TestCase

from Feedbacks.RSVPSpeller.sequence_algorithm import RSVP

class OriginalSequenceAlgorithm(object):
    def color_alg2(self,n_seq,n_col):
        self.col_trial=[]
        self.group=[]
        
        self.alphabet=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ.,:<")
        len_group=len(self.alphabet)/n_col
        
        k=0
        for k in range(0,n_col):
            self.group.append(self.alphabet[(k*len_group):(k*len_group+len_group)])
            k+=1
           
        i=0
        for i in range(0,n_seq):
            j=0
            for k in range (0,n_col):
                random.shuffle(self.group[k])
            while (j<len_group):
                for k in range (0,n_col):
                    self.col_trial.append(self.group[k][j])
                j+=1
            i+=1
      
        
        self.bursts=self.color_split(self.col_trial,n_seq)
        
        return (self.bursts)
    
    def color_split(self,t_list,num_seq):
        self.burst=[]
        for i in range (0,3*num_seq):
            self.burst.append(t_list[(i*10):(i*10+10)])
        return self.burst
        
    def mono_split(self,t_list,num_seq):
        self.burst = []    
        for i in range(0,3*num_seq):
            self.burst.append(t_list[(i*10):(i*10+10)])
        
        return self.burst
        
    def mono_link(self,a_list,num_seq):
        self.alphabet=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ.,:<")
        self.alpharandom1=copy.copy(self.alphabet)
        random.shuffle(self.alpharandom1)
        print self.alpharandom1
        if(num_seq<=10):
            for k in range(0,30):
                i=0
                while i<len(a_list):
                    if (a_list[i]==k+1): a_list[i]=self.alpharandom1[k]
                    i+=1
        else:
            self.alpharandom2=copy.copy(self.alpharandom1)
            random.shuffle(self.alpharandom2)
            print self.alpharandom2
            for k in range(0,30):
                i=0
                while i<300:
                    if (a_list[i]==k+1): a_list[i]=self.alpharandom1[k]
                    i+=1
                while i<len(a_list):
                    if(a_list[i]==k+1): a_list[i]=self.alpharandom2[k]
                    i+=1
            
        print a_list[:300] 
        print a_list[300:]   
        return a_list
    
    def mono_del_elem(self,lista,num_seq):
        for elem in range(0,num_seq):
            del lista[31*elem]
        for elem in range(1,num_seq+1):
            del lista[30*elem]
        return lista
        
    def mono_algorithm(self,num_seq):
        self.matrix=[]
        num=num_seq/2
        for i in range(1,num+1):
            self.tmp=[]
            if (i<=5): 
                for j in range(0,2**(i-1)):
                    #print i
                    self.list=range(j,32,2**(i-1))
                    #print j
                    print self.list
                    self.tmp=self.tmp+self.list
                    self.rev=copy.copy(self.tmp)
                    self.rev.reverse()
            else: 
                for j in range(0,2**(i-6)):
                    #print i
                    self.list=range(j,32,2**(i-6))
                    #print j
                    print self.list          
                    self.tmp=self.tmp+self.list
                    self.rev=copy.copy(self.tmp)
                    self.rev.reverse()
            self.matrix= self.matrix+self.tmp+self.rev

        print self.matrix   
        self.new_list=self.mono_del_elem(self.matrix,num_seq)
        self.mono_trial= self.mono_link(self.new_list,num_seq)
        self.bursts=self.mono_split(self.mono_trial,num_seq)
        
        return self.bursts
    
    def get_trial(self,num_seq,flag,num_col,num_item): 
        if(flag==0):
            mono_bursts=[]
            mono_bursts=self.mono_algorithm(num_seq)
            return mono_bursts
        elif(flag==1):
            if(num_item%num_col!=0):
                print ("Error:the number of colors must be a divisor of the number of items")
            else:
                color_bursts=[]
                color_bursts=self.color_alg2(num_seq,num_col)
                return color_bursts

class SequenceAlgorithmTest(TestCase):
    def test_changes(self):
        orig = OriginalSequenceAlgorithm()
        orig_trial = orig.get_trial(1, True, 3, 3000000)
        color_groups = ["ABCDEFGHIJ", "KLMNOPQRST", "UVWXYZ.,:<"]
        changed = RSVP(color_groups)
        changed_trial = changed.trial(1, True)
        self.assertEqual(len(changed_trial), len(orig_trial))
        self.assertEqual(len(changed_trial[0]), len(orig_trial[0]))
        print changed_trial
