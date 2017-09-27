from package import *

if __name__ == "__main__":
    dataset = RegionDatabase('global', True)
    utilities.addWorldDevelopmentIndicators(dataset)
	#utilities.addWorldEconomicOutlook(dataset)
    