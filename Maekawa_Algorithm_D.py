#title           :Maekawa_Algorithm_D.py
#description     :Dynamic N and K Try.
#author          :Betis Baheri
#date            :09-19-2019
#version         :1.0
#python_version  :2.7
#==============================================================================



import math
import random


class Process:
    Process_State = {
        'RELEASED': True,
        'WANTED': False,
        'HELD': False
    }
    Process_Voted = {
        'Voted': False
    }
    Process_Request = []
    def __init__(self):
        self.Process_State['RELEASED']= True
        self.Process_State['WANTED']=False
        self.Process_State['HELD']=False
        self.Process_Voted['Voted']=False
    def Released_State(self):
        self.Process_State['RELEASED']=True
        self.Process_State['WANTED']=False
        self.Process_State['HELD']=False
        self.Process_Voted['Voted']=False
    def Wanted_State(self):
        self.Process_State['RELEASED']=False
        self.Process_State['WANTED']=True
    def Held_State(self,Pi):
        self.Process_State['RELEASED']=False
        self.Process_State['HELD']=True
        self.Process_Request.append(Pi)
    def Reply(self,Pi):
        if self.Process_State['RELEASED'] == True and self.Process_Voted['Voted'] == False:
            self.Process_Voted['Voted']=True
            self.Held_State(Pi)
        if self.Process_State['HELD'] == True and self.Process_Voted['Voted'] == True:
            self.Process_Request.append(Pi)
    def Exit_CS_Section(self):
        self.Released_State()
    def CS_Entering_Request(self):
        self.Wanted_State()
        print('Release State: '+str(self.Process_State['RELEASED']))
    def Release_From_Pi(self):
        if len(self.Process_Request is not 0):
            self.Process_Request.pop(0)
            self.Process_Voted['Voted'] = True
        else:
            self.Process_Voted['Voted'] = False



def voting_set(Node,Cluster):
    voting_set = dict()
    K = int(math.ceil(math.sqrt(Node)))
    (row_id, col_id) = (int(Node / K),
                        int(Node % K))
    for i in range(K):
        voting_set[K * row_id + i] = None
        voting_set[col_id + K * i] = None
    return voting_set

Nodes= input("Insert Number Of Nodes (N): ")
Clusters= input("Insert Number of K:")
#print int(math.sqrt(Nodes))
if(int(math.sqrt(Nodes)) != int(Clusters) or Clusters > Nodes):
    print("Cluster should be less than Square Root of Nodes!")
else:
    qourum=[]
    prosesses = []
    for i in xrange(Nodes):
        prosesses.insert(i,Process())
    # print(prosesses[1].Process_State)
    # prosesses[0].CS_Entering_Request()
    # print(prosesses[0].Process_State)
    shuffle= xrange(1,int(Clusters)*(int(Clusters)-1)+1)
    print voting_set(Nodes,Clusters)
    for j in xrange(Nodes):
        qourum.insert(j,voting_set(Nodes,Clusters))
        #print(qourum[j])
