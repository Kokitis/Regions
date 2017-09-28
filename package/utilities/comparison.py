from itertools import zip_longest
import math

def compareSeries(left, right):
    """ Compares two Series objects against each other.
        Parameters
        ----------
            left, right: Series
    """
    if left.region.name == right.region.name:
        print("Region Name: ", left.region.name)
    else:
        print("Region Names: ", left.region.name,'\t', right.region.name)
    
    if left.name == right.name:
        print("Series Name: ", left.name)
    else:
        print("Series Names: ", left.name, '\t', right.name)
    
    if left.report.name == right.report.name:
        print(left.report.name)
    else:
        print("Reports:")
        print("\t", left.report.name)
        print("\t", right.report.name)
    
    print("\tYear\t\tLeft\tRight\tDiff\tRatio")
    for l, r in zip_longest(left, right, fillvalue = None):
        if r is None:
            r_x, r_y = math.nan, math.nan
        else:
            r_x, r_y = r.x, r.y
        if l is None:
            l_x, l_y = math.nan, math.nan
        else:
            l_x, l_y = l.x, l.y
            
        diff = l_y - r_y
        ratio = (l_y / r_y)# * 100
        
        line = "\t{}\t{:10.1f}{:10.1f}{:10.1f}\t{:.1%}".format(
            l_x, l_y, r_y, diff, ratio
        )
            
        print(line)