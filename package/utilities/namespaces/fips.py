from ...github import tabletools
from ...utilities import getDefinition

def importStateNamespace(dataset):
    identifier_map = dict()
    filename = getDefinition('file', 'State Codes')

    usps_agency = getDefinition('agency', 'USPS')
    dataset.insertEntity('agency', **usps_agency)

    namespace_config = getDefinition('namespace', 'ST')
    namespace = dataset.insertEnity('namespace', **namespace_config)

    table = tabletools.Table(filename)

    for row in table:

        region_config = {
            'name': row['Name'],
            'regionType': 'state'
        }

        region = dataset.insertEntity('region', **region_config)

        num_identifier = {
            'namespace': namespace, 
            'region': region,
            'string': '{:>02}'.format(row['FIPS State Code'])
        }

        st_identifier_config = {
            'namespace': namespace,  
            'region': region, 
            'string': row[' Official United States Postal Service (USPS) Code ']
        }

        dataset.insertEntity('identifier', **num_identifier)
        dataset.insertEntity('identifier', **st_identifier_config)

        identifier_map[st_identifier_config['string']] = region
    
    return namespace

def importFipsNamespace(dataset):

    state_namespace = importStateNamespace(dataset)
    state_map = {i['string']: i['region'] for i in state_namespace.identifiers}
    filename = getDefinition('file', 'FIPS')

    fips_namespace_config = getDefinition('namespace', 'FIPS')
    namespace = dataset.insertEntity('namespace', **fips_namespace_config)

    table = tabletools.Table(filename) 

    for row in table:
        
        region_config = {
            'regionName': row['GU Name'],
            'regionType': row['Entity Description'],
            'parentRegion': state_map[row['State FIPS Code']]
        }

        region = dataset.insertEntity('region', **region_config)

        identifier_config = {
            'namespace': namespace,
            'region': region,
            'string': row['FIPS Entity Code']
        }

        dataset.insertEntity('identifier', **identifier_config)
    
    return namespace
