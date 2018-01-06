from texttable import Texttable
from pony.orm import db_session

@db_session
def compareProjections(dataset, regions, projection, *years):
    
    
    _pop_col = lambda s: 'Population in {}'.format(s)
    _dif_col = lambda s: 'Change {}'.format(s)
    _per_col = lambda s: '% difference'.format(s)
    header = ['regionName', 'Current Population']
    for y in years:
        header += [_pop_col(y), _dif_col(y), _per_col(y)]
        
    table = Texttable(max_width = 0)
    table.add_row(header)
    table.set_cols_align(["l"] + ['r']*(len(header) - 1))
    table.set_deco(Texttable.HEADER)
    
    for region in regions:
        series = region.getSeries(projection)
        
        current = series(2017, absolute = True)
        
        row = [
            region.name,
            "{:,}".format(current)
        ]
        
        for y in years:
            proj = series(y, absolute = True)
            change = proj - current
            pct_change = change / current
            
            row += ["{:,}".format(proj), "{:,}".format(change), "{:.2%}".format(pct_change)]
        
        table.add_row(row)
    print(table.draw())