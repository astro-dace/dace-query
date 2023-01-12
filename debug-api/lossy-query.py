from dace_query.lossy import Lossy

sample_id_to_retrieve = 'SAMPLE_Ice_LN2_11_20140221_000'
x = Lossy.get_sample(sample_id=sample_id_to_retrieve)

print(x['sample_id'])

x = Lossy.query_database(limit=5)
