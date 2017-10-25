from texttable import Texttable
from fuzzywuzzy import process
def extractRegion(dataset, region_list):
    region_names = list(i.name for i in dataset.Region.select(lambda s: s))
    #print(region_names)
    table = Texttable()
    table.add_row(['providedName', 'regionName', 'code', 'exactMatch', 'fuzzyScore'])
    candidates = list()
    for region in region_list:
        if dataset.contains(region):
            key = region
            score = 100
        else:
            match = process.extractOne(region, region_names)
            key, score = match
        r = dataset.access('get', 'region', key)
        ident = [
            i for i in r.identifiers
            if (len(i.string) == 3 and not i.string.isdigit())
        ]
        if len(ident) == 1: ident = ident.pop().string

        table.add_row([region, r.name, ident, region == r.name, score])
        candidates.append(ident)
    print(table.draw())
    return candidates
