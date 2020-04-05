import numpy as np
from datetime import datetime
from MCCase import MCCase
from MCVar import MCInVar, MCOutVar

class MCSim:
    def __init__(self, name, ndraws, firstcaseisnom=True, seed=np.random.get_state()[1][0]):
        self.name = name                     # name is a string
        self.ndraws = ndraws                 # ndraws is an integer
        self.firstcaseisnom = firstcaseisnom # firstcaseisnom is a boolean
        self.ncases = ndraws + 1

        self.seed = seed                     # seed is a number between 0 and 2^32-1
        np.random.seed(seed)
        
        self.starttime = datetime.now()
        self.endtime = None
        self.runtime = None
        
        self.mcinvars = dict()     
        self.mcoutvars = dict()     
        self.mccases = []        
        
        self.setFirstCaseNom(firstcaseisnom)
        self.setNDraws(self.ndraws)


    def setFirstCaseNom(self, firstcaseisnom):  # firstdrawisnom is a boolean
        if firstcaseisnom:
           self.firstcaseisnom = True
           self.ncases = self.ndraws + 1
        else:
           self.firstcaseisnom = False
           self.ncases = self.ndraws
        if self.mcinvars != dict():
            for mcvar in self.mcinvars.values():
                mcvar.setFirstCaseNom(firstcaseisnom)

    def addInVar(self, name, dist, distargs):  
        # name is a string
        # dist is a scipy.stats.rv_discrete or scipy.stats.rv_continuous 
        # distargs is a tuple of the arguments to the above distribution
        self.mcinvars[name] = MCInVar(name, dist, distargs, self.ndraws, self.ncases, self.firstcaseisnom)


    def setNDraws(self, ndraws):  # ncases is an integer
        self.ndraws = ndraws
        self.setFirstCaseNom(self.firstcaseisnom)
        np.random.seed(self.seed)
        if self.mcinvars == dict():
            self.clearCases()
        else:
            for mcvar in self.mcinvars.values():
                mcvar.setNDraws(ndraws)
            if self.mccases != []:
                self.genCases()


    def genCases(self):
        self.clearCases()
        for ncase in range(self.ncases):
            isnom = False
            if self.firstcaseisnom and ncase == 0:
                isnom = True
            self.mccases.append(MCCase(ncase, self.mcinvars, isnom))


    def genOutVars(self):
        for varname in self.mccases[0].mcoutvals.keys():
            vals = []
            for i in range(self.ncases):
                vals.append(self.mccases[i].mcoutvals[varname].val)
            self.mcoutvars[varname] = MCOutVar(varname, vals, self.ndraws, self.firstcaseisnom)
            for i in range(self.ncases):
                self.mccases[i].mcoutvars[varname] = self.mcoutvars[varname]

    def clearCases(self):
        self.mccases = []


    def clearInVars(self):
        self.mcinvars = dict()
        self.setNDraws(self.ndraws)


'''
### Test ###
from scipy.stats import *
np.random.seed(74494861)
sim = MCSim('Sim', 10)
sim.addInVar('Var1', randint, (1, 5))
sim.addInVar('Var2', norm, (10, 4))
sim.genCases()
print(sim.mcinvars['Var1'].name)
print(sim.mccases[0].mcinvals['Var1'].val)
print(sim.mcinvars['Var2'].name)
print(sim.mccases[0].mcinvals['Var2'].val)
#'''
