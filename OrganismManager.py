"""
    Class       : Computer Architecture, FALL 2011, Olin College
    Project     : 
    Author      : Shane Moon, Paul Booth
    Date        : 11/10/2011
    File Name   : OrganismManager.py
    Description :
"""

import testOrgs
import random
import selector
import matplotlib.pyplot as pyplot
import os

class OrganismManager:
    def __init__(self, organismType, population, survival, threshold, 
        resultMap, verilogWriteFileName = 'organism.v', 
        verilogModuleName = None, **kwargs):
        """
            organisms  : <List> of <Organism>s
            population : the maximum number of <Organism>s
            survival   : the number of <Organism>s that will survive
                         each generation
            threshold  : fitness at which the simulation stops
            resultMap  : <testOrgs.SimulationMap> of correct behavior
        """
        assert (survival > 0), "At least one Organism should survive."
        assert (population > 0), "At least one Organism should exist."
        assert (population > survival), "population should be greater than " \
                                         "survival."
        
        self.generationNumber = 0
        
        self.organismType = organismType
        
        self.organisms = []
        self.population = population
        self.survival = survival
        self.threshold = threshold
        
        self._resultMap = resultMap
        self._numberOfInputs = resultMap.getNumberOfInputs()
        self._numberOfOutputs = resultMap.getNumberOfOutputs()
        
        self._selectorPmf = None
        
        self.verilogWriteFileName = verilogWriteFileName
        
        if verilogModuleName is None:
            verilogModuleName = verilogWriteFileName.split('.')[0]
            
        self.verilogModuleName = verilogModuleName
        
        self.kwargs = kwargs

    def __str__(self):
        s = "Population : %i \n" % (self.population)
        s += '\n'.join(str(organism) for organism in self.organisms)
        return s

    def getNumberOfInputs(self):
        return self._numberOfInputs
    
    def getNumberOfOutputs(self):
        return self._numberOfOutputs

    def _updateSelectorPmf(self):
        
        self._selectorPmf = selector.MakeOrganismPmfFromOrganisms(self.organisms)

    def selectOrganism(self):
        """
            Return Type: <Organism>
            Selects one <Organism> from the list, with higher possibility
            of choosing the one with higher fitness.
        """
        
        return self._selectorPmf.Random()

    def generateParents(self):
        generatorPmf = self._selectorPmf.Copy()
        parent1 = generatorPmf.Random()
        generatorPmf.Remove(parent1)
        generatorPmf.Normalize()
        parent2 = generatorPmf.Random()
        return parent1,parent2

    def updateOrganisms(self,visualize=False):
        """
            Return Type: void
            1. Keep the (self.survival) best <Organism>s from the
               previous generation
            2. Selects two <Organism>s from the list, crossover them and add
               a new <Organism>
            3. Repeat 2. (population - survival) times
            4. Sort the list by their fitness.
        """
        newGeneration = self.organisms[0:self.survival]
        
        for i in range(self.population - self.survival):
            p1,p2 = self.generateParents()
            # print parent1, "\nORGANISM crossing over with\n", parent2
            newOrganism = p1.crossover(p2)
            newOrganism.mutate()
            newOrganism.evaluate(self._resultMap)
            newGeneration.append(newOrganism)
        
        self.organisms = newGeneration
        self.organisms.sort(reverse = True)
        self._updateSelectorPmf()
        
        if visualize:
            self.visualize()

    def populate(self,visualize=True):
        """
            Return Type: void
            Populates <Organism>s and store them in self.organisms
        """
        
        for i in range(self.population):
            randOrganism = self.getRandomOrganism()
            self.organisms.append(randOrganism)
        self.organisms.sort(reverse = True)
        self._updateSelectorPmf()
        
        if visualize:
            self.visualize()

    def getRandomOrganism(self):
        randOrganism = self.organismType(
            self.verilogWriteFileName,
            self.getNumberOfInputs(),
            self.getNumberOfOutputs(),
            randomInit=True,
            moduleName=self.verilogModuleName,
            **self.kwargs
            )
        
        randOrganism.evaluate(self._resultMap)
        return randOrganism

    def execute(self,visualize=False):
        """
            Return Type: void
            MainLoop
        """
        self.writeSimulation()
        self.populate(visualize)
        while self.organisms[0].getFitness() < self.threshold:
            self.generationNumber += 1
            self.updateOrganisms(visualize)
        self.organisms[0].toVerilog('Winner.v', self.verilogModuleName)
        self.deleteSimulation()
    
    def writeSimulation(self):
        testOrgs.writeSimulation(
            os.path.join('TestCode','%s.v'%'organismTest'),
            self.verilogWriteFileName,
            self._numberOfInputs,
            self._numberOfOutputs,
            self.verilogModuleName
        )
        
    def deleteSimulation(self):
        try:
            os.remove(os.path.join('TestCode','%s.v'%'organismTest'))
            os.remove(os.path.join('TestCode','%s.v'%'organismTest'))
        except:
            print "Error clearing files!"
            print "Files are to be cleared, but the files probably don't exist."
    
    def visualize(self):
        selector.drawOrganismPmfAsCdf(
            self._selectorPmf, self.generationNumber
        )
        
if __name__ == '__main__':
    import matplotlib.pyplot as pyplot
    import testOrgs
    from BooleanLogic import BooleanLogicOrganism
    from TreeOrganism import TreeOrganism
    
    defaultResult = testOrgs.testOrganism('fourBoolCorrect.v', '', 4, 4,'fourBool',clearFiles=True)
    simMap = testOrgs.SimulationMap(defaultResult)
    
    pyplot.ion()
    #manager = OrganismManager(BooleanLogicOrganism,
    #    10,2,16,simMap,verilogWriteFileName = 'fourBool.v',nLayers = 1)
    manager = OrganismManager(TreeOrganism,
        15,3,16,simMap,verilogWriteFileName = 'fourBool.v',
        maxDepth=3,inputProbability=.2)
        
    manager.execute(True)
    pyplot.show()
    pyplot.ioff()
