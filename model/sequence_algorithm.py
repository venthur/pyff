'''
Created on 19/feb/2010

@author: Laura
'''
import copy
import random

class RVSP(object):
    
    def color_link (self,n_list,num_seq):
        self.col_trial=[]
        self.group1=list("ABCDEFGHIJ")
        self.group2=list("KLMNOPQRST")
        self.group3=list("UVWXYZ.,:<")
        
        self.group1rand1=copy.copy(self.group1)
        random.shuffle(self.group1rand1)
        self.group2rand1=copy.copy(self.group2)
        random.shuffle(self.group2rand1)
        self.group3rand1=copy.copy(self.group3)
        random.shuffle(self.group3rand1)
        
        i=0
        if (num_seq<=8):
            while (i<len(n_list)):
                self.lett=n_list[i]-1
                self.col_trial.append(self.group1rand1[self.lett])
                self.col_trial.append(self.group2rand1[self.lett])
                self.col_trial.append(self.group3rand1[self.lett])     
                i+=1   
        else:
            self.group1rand2=copy.copy(self.group1rand1)
            random.shuffle(self.group1rand2)
            self.group2rand2=copy.copy(self.group2rand1)
            random.shuffle(self.group2rand2)
            self.group3rand2=copy.copy(self.group3rand1)
            random.shuffle(self.group3rand2)
            
            while(i<80):
                self.lett=n_list[i]-1
                self.col_trial.append(self.group1rand1[self.lett])
                self.col_trial.append(self.group2rand1[self.lett])
                self.col_trial.append(self.group3rand1[self.lett])     
                i+=1
            while (i<len(n_list)):
                self.lett=n_list[i]-1
                self.col_trial.append(self.group1rand2[self.lett])
                self.col_trial.append(self.group2rand2[self.lett])
                self.col_trial.append(self.group3rand2[self.lett])     
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
            if(i<=4):
                for j in range(0,2**(i-1)):
                    self.list=range(j,12,2**(i-1))
                    self.tmp=self.tmp+self.list
                    self.rev=copy.copy(self.tmp)
                    self.rev.reverse()
            else:
                for j in range(0,2**(i-5)):
                    self.list=range(j,12,2**(i-5))         
                    self.tmp=self.tmp+self.list
                    self.rev=copy.copy(self.tmp)
                    self.rev.reverse()
            self.matrix= self.matrix+self.tmp+self.rev
       
        self.new_list=self.color_del_elem(self.matrix)
        self.col_trial=self.color_link(self.new_list,num_seq) 
        self.bursts=self.color_split(self.col_trial,num_seq)
        
        return self.bursts
    
        
    def mono_split(self,t_list,num_seq):
        self.burst = []    
        for i in range(0,3*num_seq):
            self.burst.append(t_list[(i*10):(i*10+10)])
        
        return self.burst
           
        
    def mono_link(self,a_list,num_seq):
        self.alphabet=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ.,:<")
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
                    print self.list
                    self.tmp=self.tmp+self.list
                    self.rev=copy.copy(self.tmp)
                    self.rev.reverse()
            else: 
                for j in range(0,2**(i-6)):
                    self.list=range(j,32,2**(i-6))
                    print self.list          
                    self.tmp=self.tmp+self.list
                    self.rev=copy.copy(self.tmp)
                    self.rev.reverse()
            self.matrix= self.matrix+self.tmp+self.rev
            
        self.new_list=self.mono_del_elem(self.matrix,num_seq)
        self.mono_trial= self.mono_link(self.new_list,num_seq)
        self.bursts=self.mono_split(self.mono_trial,num_seq)
        
        return self.bursts
    
    def get_trial(self,num_seq,flag): 
        if(flag==0):
            mono_bursts=[]
            mono_bursts=self.mono_algorithm(num_seq)
            return mono_bursts
        elif(flag==1):
            color_bursts=[]
            color_bursts=self.color_algorithm(num_seq)
            return color_bursts

  
        
    
    '''
    classdocs
    '''

#the number of sequences should be even,16 maximum for the color algorithm and 20 maximum for the mono_algorithm
    
if __name__ == "__main__":
    
    myobject = RVSP()
    num_sequences=14
    flag=1
    trial=myobject.get_trial(num_sequences,flag)
    print trial
    
