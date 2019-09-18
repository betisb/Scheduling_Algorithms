
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


pi = Process()
print(pi.Process_Request)
pi.CS_Entering_Request()

