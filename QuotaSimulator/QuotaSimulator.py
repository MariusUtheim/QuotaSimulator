import math
import random


# The simulation model, for an abstract generator, selector and evaluator

def runSimulation(generator, selector, evaluator):
	applicants = generator()
	selection = selector(applicants)
	score = evaluator(applicants, selection)
	return score


# Define the Person class and the components of the simulation model

class Person():
	def __init__(self, skillLevel: float, isPrivileged: bool):
		self.skillLevel = skillLevel
		self.isPrivileged = isPrivileged


def uniformGenerator(nApplicants: int):
	return lambda: [ Person(random.uniform(0., 1.), random.choice([ True, False ])) for _ in range(nApplicants) ]


def unbiasedSelector(nSelections: int):
	sortKey = lambda person: person.skillLevel;
	return lambda applicants: sorted(applicants, key = sortKey, reverse = True)[:nSelections]

def biasedSelector(nSelections: int, biasFactor: float):
	sortKey = lambda person: person.skillLevel if person.isPrivileged else person.skillLevel * biasFactor
	return lambda applicants: sorted(applicants, key = sortKey, reverse = True)[:nSelections]

def quotaSelector(nSelections: int, biasFactor: float, maxQuotaFraction: float):
	sortKey = lambda person: person.skillLevel if person.isPrivileged else person.skillLevel * biasFactor
	def _quotaSelector(applicants):
		sortedApplicants = sorted(applicants, key = sortKey, reverse = True)
		nPrivileged, nNonPrivileged = 0, 0
		maxFromEachGroup = math.ceil(nSelections * maxQuotaFraction)
		selection = []
		# Assumes there are enough applicants from each group; 
		# otherwise, the number of selected candidates might be smaller than nSelections
		for applicant in sortedApplicants:
			if len(selection) >= nSelections:
				break
			if applicant.isPrivileged:
				if nPrivileged < maxFromEachGroup:
					nPrivileged += 1
					selection.append(applicant)
			else:
				if nNonPrivileged < maxFromEachGroup:
					nNonPrivileged += 1
					selection.append(applicant)
		return selection
	return _quotaSelector


def skillLevelEvaluator(applicants: list, selection: list):
	optimalSelection = sorted(applicants, key = lambda person: -person.skillLevel)[:len(selection)]
	optimalPicks = sum((person in optimalSelection) for person in selection)
	return optimalPicks / len(selection)


# Run sample simulation with 50 applicants and 10 open positions
import statistics 
import io

stream = io.open("Results.csv", "w")
stream.write("Quota;Bias=0.01;Bias=0.33;Bias=0.67;Bias=0.9;Bias=1.0\n");

myGenerator = uniformGenerator(50)
myEvaluator = skillLevelEvaluator

for quotaFactor in [ 0.5, 0.6, 0.7, 0.8, 0.9, 1.0 ]:
	stream.write(f"{100 * (1 - quotaFactor)} %")
	for biasFactor in [ 0.01, 0.33, 0.67, 0.9, 1.0 ]:
		mySelector = quotaSelector(10, biasFactor, quotaFactor)
		score = statistics.mean([ runSimulation(myGenerator, mySelector, myEvaluator) for _ in range(1000) ])
		stream.write(";")
		stream.write(str(score))
	stream.write("\n")

stream.close()
