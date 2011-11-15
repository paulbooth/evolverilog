"""
    Class       : Computer Architecture, FALL 2011, Olin College
    Project     : 
    Author      : Shane Moon, Paul Booth
    Date        : 11/10/2011
    File Name   : OrganismManager.py
    Description :
"""

from Organism import *
import random
import selector
import matplotlib.pyplot as pyplot

class OrganismManager:
    def __init__(self, population, survival, generation, resultMap):
        """
            organisms  : <List> of <Organism>s
            population : the maximum number of <Organism>s
            survival   : the number of <Organism>s that will survive
                         each generation
            resultMap  : <testOrgs.SimulationMap> of correct behavior
        """
        assert (survival > 0), "At least one Organism should survive."
        assert (population > 0), "At least one Organism should exist."
        assert (generation > 0), "The number of evolution should exceed 0."
        assert (population > survival), "population should be greater than " \
                                         "survival."
        
        self.organisms = []
        self.population = population
        self.survival = survival
        self.generation = generation
        
        self._resultMap = resultMap
        self._selectorPmf = None

    def __str__(self):
        s = "Population : %i \n" % (self.population)
        s += '\n'.join(str(organism) for organism in self.organisms)
        return s

    def _updateSelectorPmf(self):
        self._selectorPmf = selector.MakeOrganismPmfFromOrganisms(self.organisms)

    def selectOrganism(self):
        """
            Return Type: <Organism>
            Selects one <Organism> from the list, with higher possibility
            of choosing the one with higher fitness.
        """

        return self._selectorPmf.Random()

    def updateOrganisms(self,visualize=False):
        """
            Return Type: void
            1. Keep the certain number of the best <Organism>s from the
               previous generation
            2. Selects two <Organism>s from the list, crossover them and add
               a new <Organism>
            3. Repeat 2. (population - survival) times
            4. Sort the list by their fitness.
        """
        newGeneration = self.organisms[0:self.survival]
        for i in range(self.population - self.survival):
            parent1 = self.selectOrganism()
            parent2 = self.selectOrganism()
            print "\nVVVVVVVVVVVVVVVVVVVVVVVVVVV"
            print parent1, "\nORGANISM crossing over with\n", parent2
            newOrganism = parent1.crossover(parent2)
            print "TTTTTTTTTTTTTTTTTTTTTTTTTTT"
            newOrganism.evaluate(self._resultMap)
            newGeneration.append(newOrganism)
        self.organisms = newGeneration
        self.organisms.sort(reverse = True)
        self._updateSelectorPmf()
        if visualize:
            self.visualize()

    def populate(self):
        """
            Return Type: void
            Populates <Organism>s and store them in self.organisms
        """
        for i in range(self.population):
            # CHANGE THIS LINE
            randOrganism = BooleanLogicOrganism('TestCode/fourBool.v',4,4,randomInit=True,moduleName='fourBool')
            randOrganism.evaluate(self._resultMap)
            self.organisms.append(randOrganism)
        self._updateSelectorPmf()

    def execute(self,visualize=False):
        """
            Return Type: void
            MainLoop
        """
        self.populate()
        for i in range(self.generation):
            self.updateOrganisms(visualize)
            
    def visualize(self):
        selector.drawOrganismPmfAsCdf(self._selectorPmf)
        
if __name__ == '__main__':
    import matplotlib.pyplot as pyplot
    
    defaultResult = testOrgs.testOrganism('fourBool.v', 'TestCode', 4, 4, 'fourBool',clearFiles=True)
    simMap = testOrgs.SimulationMap(defaultResult)

    pyplot.ion()
    manager = OrganismManager(15, 5, 10, simMap)
    manager.execute(True)
    pyplot.show()
    pyplot.ioff()
    
