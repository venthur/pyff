import copy
import random

class RVSP:
    
    matrix=[]
    
    
    def crea_burst(self,burst_list):
        self.no_lett=list("%*/)?#")
        self.trial = []
        
        for i in range(0,30):
            self.trial.append(self.no_lett+burst_list[(i*10):(i*10+10)])
        
        return self.trial
           
        
    def associa(self,a_list):
        self.alphabet=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ.,:<")
        self.alpharandom=copy.copy(self.alphabet)
        random.shuffle(self.alpharandom)
        print self.alpharandom
        for k in range(0,30):
            i=0
            while i<len(a_list):
                if (a_list[i]==k+1): a_list[i]=self.alpharandom[k]
                i+=1
        return a_list
    
    def canc_elem(self,lista):
        for elem in range(0,10):
            del lista[31*elem]
        print lista
        for elem in range(1,11):
            del lista[30*elem]
        return lista
        
    def random_sequence(self):
        for i in range(1,6):
            #print "i= ", i
            self.tmp=[]
            for j in range(0,2**(i-1)):
                #print "j= ", j
                self.list=range(j,32,2**(i-1))
                #print self.list
                self.tmp=self.tmp+self.list
                #print self.tmp
                self.rev=copy.copy(self.tmp)
                self.rev.reverse()
            self.matrix= self.matrix+self.tmp+self.rev
        #print self.matrix
        self.new_list=self.canc_elem(self.matrix)
        #print self.new_list
        self.ra_list= self.associa(self.new_list)
        print self.ra_list
        self.lungh=len(self.ra_list)
        #print self.lungh
        self.trial=self.crea_burst(self.ra_list)
        print self.trial

        
            
            
        
if __name__ == "__main__":
    myobject = RVSP()
    myobject.random_sequence()
    
'''
Created on 10/feb/2010

@author: Laura
'''
