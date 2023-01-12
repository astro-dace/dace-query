from pathlib import Path

import pytest

from dace_query import DaceClass
from dace_query.opendata import OpenDataClass


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance')
])
def test_open_data_query_database_keys(instance, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = OpenDataClass(dace_instance=dace_instance)

    expected_keys = ['main_project_leader', 'main_project_label', 'project_label', 'project_leader', 'pub_first_author',
                     'pub_title', 'pub_date', 'pub_journal', 'pub_bibcode', 'pub_doi', 'pub_openaccess_url',
                     'data_dace_id', 'data_license', 'data_dace_archive_path', 'data_dace_readme_path',
                     'data_external_repositories', 'pub_all_authors', 'data_status', 'user_id', 'pub_major',
                     'pub_referred', 'ads_link', 'doi_link']

    results = instance.query_database(limit=5, output_format='dict')
    # Result is not empty
    assert results
    # Check if all parameters are returned
    assert all((key in results.keys()) for key in expected_keys)


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance')
])
def test_open_data_query_database(instance, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = OpenDataClass(dace_instance=dace_instance)

    filters = {'main_project_label': {'equal': ['project_dev']}}
    results = instance.query_database(filters=filters, output_format='dict')

    for external_repositories in results['data_external_repositories']:
        assert isinstance(external_repositories, list)


@pytest.mark.parametrize('instance', [
    pytest.param('anon_dace_instance')
])
def test_open_data_download_readme(instance, request):
    dace_instance: DaceClass = request.getfixturevalue(instance)
    instance = OpenDataClass(dace_instance=dace_instance)

    output_directory = '/tmp'
    output_filename = 'README.md'
    instance.download(
        dace_data_id='dace-od-20226',
        file_type='readme',
        output_directory=output_directory,
        output_filename=output_filename
    )
    assert Path(output_directory, output_filename).exists()
    Path(output_directory, output_filename).unlink(missing_ok=True)
