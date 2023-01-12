from dace_query.exoplanet import Exoplanet

filters = {
    'obj_id_catname': {
        'contains':
            ['TOI', 'HD'],
        'notEqual': ['TOI-755 b']
    },
    'obj_orb_period_day': {
        'min': 2.5,
        'max': 3
    },
    'pub_info_detectiontype': {
        'equal': ['RV']
    }
}

values = Exoplanet.query_database(filters=filters, limit=10)
sort: dict = {
    'obj_phys_radius_rjup': 'asc',
    'obj_id_catname': 'desc'
}

values = Exoplanet.query_database(sort=sort, limit=10)

print(list(values.keys()))
print(values['obj_phys_radius_rjup'])
print(values['obj_id_catname'])

values = Exoplanet.query_database(output_format='numpy', limit=10)
print(values)
