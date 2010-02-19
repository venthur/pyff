#draft of the algorithm

import copy
import random

class RVSP:
     
    def create_burst(self,burst_list,num_seq):
        #self.no_lett=list("%*/)?#")
        self.trial = []
        
        for i in range(0,3*num_seq):
            self.trial.append(burst_list[(i*10):(i*10+10)])
        
        return self.trial
           
        
    def link(self,a_list):
        self.alphabet=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ.,:<")
        self.alpharandom=copy.copy(self.alphabet)
        random.shuffle(self.alpharandom)
        #print self.alpharandom
        for k in range(0,30):
            i=0
            while i<len(a_list):
                if (a_list[i]==k+1): a_list[i]=self.alpharandom[k]
                i+=1
        return a_list
    
    def del_elem(self,lista,num_seq):
        for elem in range(0,num_seq):
            del lista[31*elem]
        for elem in range(1,num_seq+1):
            del lista[30*elem]
        return lista
        
    def random_sequence(self,num_seq):
        self.matrix=[]
        num=num_seq/2
        for i in range(1,num_seq):
            self.tmp=[]
            for j in range(0,2**(i-1)):
                self.list=range(j,32,2**(i-1))
                self.tmp=self.tmp+self.list
                self.rev=copy.copy(self.tmp)
                self.rev.reverse()
            self.matrix= self.matrix+self.tmp+self.rev
            
        self.new_list=self.del_elem(self.matrix,num_seq)
        self.ra_list= self.link(self.new_list)
        #print self.ra_list
        self.lungh=len(self.ra_list)
        self.trial=self.create_burst(self.ra_list,num_seq)
        print self.trial

        
            
            
        
if __name__ == "__main__":
    myobject = RVSP()
    num_sequences=10
    myobject.random_sequence(num_sequences)
    
'''
Created on 10/feb/2010

@author: Laura
'''
