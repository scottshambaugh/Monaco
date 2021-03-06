from Monaco.MCVal import MCOutVal
import numpy as np

class MCCase():
    def __init__(self, ncase, mcinvars, constvals, isnom, seed=np.random.get_state()[1][0]):
        self.ncase = ncase        # ncase is an integer
        self.isnom = isnom        # isnom is a boolean
        self.mcinvars = mcinvars  # mcvars is a dict of MCVar objects
        self.constvals = constvals
        self.mcoutvars = dict()
        self.seed = seed
        
        self.starttime = None
        self.endtime = None
        self.runtime = None
        
        self.filepath = None
        self.runsimid = None
        self.hasrun = False
        self.haspostprocessed = False
        
        self.mcinvals = self.getMCInVals()
        self.mcoutvals = dict()
        
        self.siminput = None
        self.simrawoutput = None
        

    def getMCInVals(self):
        mcvals = dict()
        for mcvar in self.mcinvars.values():
            mcval = mcvar.getVal(self.ncase)
            mcvals[mcval.name] = mcval
        return mcvals


    def getMCOutVals(self):
        mcvals = dict()
        for mcvar in self.mcoutvars.values():
            mcval = mcvar.getVal(self.ncase)
            mcvals[mcval.name] = mcval
        return mcvals
    
    
    def addOutVal(self, name, val, split=True, valmap=None):
        self.mcoutvals[name] = MCOutVal(name=name, ncase=self.ncase, val=val, valmap=valmap, isnom=self.isnom)
        if split:
            self.mcoutvals.update(self.mcoutvals[name].split())


'''
### Test ###
if __name__ == '__main__':
    import numpy as np
    from scipy.stats import norm
    from MCVar import MCInVar
    np.random.seed(74494861)
    var = {'Test':MCInVar('Test', norm, (10, 4), 10)}
    case = MCCase(0, var, False)
    print(case.mcinvals['Test'].val)
    
    case.addOutVal('TestOut', [[0,0],[0,0],[0,0]])
    print(case.mcoutvals['TestOut'].val)
    print(case.mcoutvals['TestOut'].size)
    valmap = {'a':0,'b':-1,'c':-2,'d':-3,'e':-4,'f':-5}
    case.addOutVal('TestOut2', [['a','b'],['c','d'],['e','f']], valmap = valmap)
    print(case.mcoutvals['TestOut2'].num)
#'''
