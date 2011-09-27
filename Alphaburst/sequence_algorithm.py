__copyright__ = """ Copyright (c) 2010 Laura Acqualagna

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

class RSVP(object):
    def __init__(self, groups):
        self.groups = map(list, groups)
        self.alphabet = sum(self.groups, [])
    
    def color_algorithm(self,n_seq):
        self.col_trial=[]
        n_col = len(self.groups) 
        len_group=len(self.alphabet)/n_col
        i=0
        for i in range(0,n_seq):
            j=0
            for k in range (0,n_col):
                random.shuffle(self.groups[k])
            while (j<len_group):
                for k in range (0,n_col):
                    self.col_trial.append(self.groups[k][j])
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
        self.alpharandom1=copy.copy(self.alphabet)
        random.shuffle(self.alpharandom1)
       
        if(num_seq<=10):
            for k in range(0,30):
                i=0
                while i<len(a_list):
                    if (a_list[i]==k+1): a_list[i]=self.alpharandom1[k]
                    i+=1
        else:
            self.alpharandom2=copy.copy(self.alpharandom1)
            random.shuffle(self.alpharandom2)
           
            for k in range(0,30):
                i=0
                while i<300:
                    if (a_list[i]==k+1): a_list[i]=self.alpharandom1[k]
                    i+=1
                while i<len(a_list):
                    if(a_list[i]==k+1): a_list[i]=self.alpharandom2[k]
                    i+=1
  
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
                    self.list=range(j,32,2**(i-1))
                    self.tmp=self.tmp+self.list
                    self.rev=copy.copy(self.tmp)
                    self.rev.reverse()
            else: 
                for j in range(0,2**(i-6)):
                    self.list=range(j,32,2**(i-6))
                    self.tmp=self.tmp+self.list
                    self.rev=copy.copy(self.tmp)
                    self.rev.reverse()
            self.matrix= self.matrix+self.tmp+self.rev
            
        self.new_list=self.mono_del_elem(self.matrix,num_seq)
        self.mono_trial= self.mono_link(self.new_list,num_seq)
        self.bursts=self.mono_split(self.mono_trial,num_seq)
        
        return self.bursts
    
    def trial(self, num_seq, color): 
        """ The number of sequences should be even, 16 maximum for the
        color algorithm and 20 maximum for the mono_algorithm.
        """
        algo = self.color_algorithm if color else self.mono_algorithm
        return algo(num_seq)
