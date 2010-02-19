#draft of the algorithm

'''
Created on 18/feb/2010

@author: Laura
'''
import copy
import random

class RVSP(object):
    
    def color_link (self,n_list):
        self.col_trial=[]
        self.group1=list("ABCDEFGHIJ")
        self.group2=list("KLMNOPQRST")
        self.group3=list("UVWXYZ.,:<")
        
        self.group1rand=copy.copy(self.group1)
        random.shuffle(self.group1rand)
        self.group2rand=copy.copy(self.group2)
        random.shuffle(self.group2rand)
        self.group3rand=copy.copy(self.group3)
        random.shuffle(self.group3rand)
        
        i=0
        while i<len(n_list):
            self.lett=n_list[i]-1
            self.col_trial.append(self.group1rand[self.lett])
            self.col_trial.append(self.group2rand[self.lett])
            self.col_trial.append(self.group3rand[self.lett])     
            i+=1    
        return self.col_trial
    
    
    def color_split(self,t_list,num_seq):
        self.burst=[]
        for i in range (0,3*num_seq):
            self.burst.append(t_list[(i*10):(i*10+10)])
        return self.burst
        
        
    def color_del_elem(self,lista):
        for elem in lista[:]:
            if (elem==0 or elem==11 ): lista.remove(elem)
        return lista
    
    def color_algorithm(self,num_seq):
        self.matrix=[]
        num=num_seq/2
        
        for i in range(1,num+1):
            self.tmp=[]
            for j in range(0,2**(i-1)):
                self.list=range(j,12,2**(i-1))
                self.tmp=self.tmp+self.list
                self.rev=copy.copy(self.tmp)
                self.rev.reverse()
            self.matrix= self.matrix+self.tmp+self.rev
        
        self.new_list=self.color_del_elem(self.matrix)
        self.col_trial=self.color_link(self.new_list) 
        self.bursts=self.color_split(self.col_trial,num_seq)
        
        return self.bursts
    
        
    def mono_split(self,t_list,num_seq):
        self.burst = []    
        for i in range(0,3*num_seq):
            self.burst.append(t_list[(i*10):(i*10+10)])
        
        return self.burst
           
        
    def mono_link(self,a_list):
        self.alphabet=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ.,:<")
        self.alpharandom=copy.copy(self.alphabet)
        random.shuffle(self.alpharandom)
        for k in range(0,30):
            i=0
            while i<len(a_list):
                if (a_list[i]==k+1): a_list[i]=self.alpharandom[k]
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
            for j in range(0,2**(i-1)):
                self.list=range(j,32,2**(i-1))
                self.tmp=self.tmp+self.list
                self.rev=copy.copy(self.tmp)
                self.rev.reverse()
            self.matrix= self.matrix+self.tmp+self.rev
            
        self.new_list=self.mono_del_elem(self.matrix,num_seq)
        self.mono_trial= self.mono_link(self.new_list)
        self.bursts=self.mono_split(self.mono_trial,num_seq)
        
        return self.bursts

  
        
    
    '''
    classdocs
    '''


if __name__ == "__main__":
    color_bursts=[]
    mono_bursts=[]
    num_sequences=12
    myobject = RVSP()
    color_bursts=myobject.color_algorithm(num_sequences)
    mono_bursts=myobject.mono_algorithm(num_sequences)
    print color_bursts
    print mono_bursts
