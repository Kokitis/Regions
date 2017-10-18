from texttable import Texttable
def compareProjections(regions, projection, year):
    table = Texttable(max_width = 0)

    table.add_row([
        'Name', 
        'Population in 2017',
        'Population in {}'.format(year),
        'Change',
        'Percent Difference',
        'Annual Growth Rate'
    ])
    table.set_cols_dtype(['t', 't', 't', 't', 't', 't'])
    table.set_cols_align(["l", "r", "r", "r", "r", "r"])
    table.set_deco(Texttable.HEADER)
    
    for region in regions:
        series = region.getSeries(projection)
        
        current = series(2017, absolute = True)
        proj = series(year, absolute = True)
        
        change = proj - current
        pct_change = (change) / current
        pct_change = "{:.2%}".format(pct_change)
        growth_rate = change / ((year - 2017) * current)
        growth_rate = "{:.2%}".format(growth_rate)
        
        table.add_row([
            region.name, 
            "{:,}".format(current),
            "{:,}".format(proj),
            "{:,}".format(change),
            pct_change,
            growth_rate])
    print(table.draw())