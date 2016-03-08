import json

from django_jsonrpc import jsonrpc_method
from django.http import HttpResponse
from django.shortcuts import redirect

import settings
from utils import unique


@jsonrpc_method('api_version')
def api_version(request):
    return {'major': 0, 'minor': 2, 'micro': 0}


#@jsonrpc_method('available_packages')
def available_packages(package_class, request):
    return [p.name for p in package_class.objects.filter(public=True)
            .order_by('name')]


#@jsonrpc_method('package_latest_version')
def package_latest_version(version_class, request, package_name,
                           major_version=0):
    package_version = (version_class.objects
                       .filter(major=major_version, publish=True,
                               package__name=package_name)
                       .order_by('-major', '-minor', '-micro')[0])
    return {'major': package_version.major, 'minor': package_version.minor,
            'micro': package_version.micro}


#@jsonrpc_method('package_versions')
def package_versions(version_class, request, package_name, major_version=0):
    package_versions = (version_class.objects
                        .filter(major=major_version, publish=True,
                                package__name=package_name)
                        .order_by('major', 'minor', 'micro'))
    return [{'major': version.major, 'minor': version.minor,
             'micro': version.micro} for version in package_versions]


#@jsonrpc_method('package_url')
def package_url(version_class, request, package_name, version):
    package_version = version_class.objects.get(package__name=package_name,
                                                major=version['major'],
                                                minor=version['minor'],
                                                micro=version['micro'])
    return str(package_version.url())


def redirect_to_latest(version_class, request, package_name, major_version=0):
    latest_version = package_latest_version(version_class, request,
                                            package_name, major_version)
    latest_url = package_url(version_class, request, package_name,
                             latest_version)
    if latest_url.startswith('/'):
        latest_url = latest_url[1:]
    return redirect(getattr(settings, 'SITE_ROOT', '/') + latest_url)


RELEASES_SCHEMA = {
    'type': 'array',
    'items': {
        'oneOf': [{'type': 'object',
                  'additionalProperties': {
                      'type': 'object',
                      'properties': {
                          "filename": {'type': 'string'},
                          "md5_digest": {'type': 'string'},
                          "size": {'type': 'integer'},
                          "upload_time": {'type': 'string', 'format':
                                          'date-time'},
                          "url": {'type': 'string'}},
                      'required': ['filename', 'md5_digest', 'size',
                                   'upload_time', 'url']}}]}}


PACKAGE_RELEASES_SCHEMA = {
    'type': 'object',
    'properties': {
        'releases': RELEASES_SCHEMA},
    'required': ['releases']}


PACKAGES_SCHEMA = {
    'type': 'object',
    'properties': {
        'packages': {
            'type': 'object',
            'additionalProperties': {
                'type': 'object',
                'properties': {
                    "latest_version": {'type': 'string'},
                    "url": {'type': 'string'}},
                'required': ['url']}}},
    'required': ['packages']}


def releases_info(versions, base_uri=''):
    '''
    Args
    ----

        versions (list) : List of version objects with `path()` and `url()`
            methods and `major`, `minor`, and `micro` attributes.

    Returns
    -------

        (dict) : Dictionary of releases info corresponding to the list of
            version objects.  See `RELEASES_SCHEMA` for format.
    '''
    from datetime import datetime
    from path_helpers import path

    root_directory = path(__file__).abspath()

    def version_release_info(v):
        file_path = root_directory.joinpath(v.path())
        upload_time = datetime.utcfromtimestamp(file_path.mtime).isoformat()
        return [{'upload_time': upload_time, 'url': base_uri + v.url(),
                 'size': file_path.size, 'filename': file_path.name,
                 'md5_digest': file_path.read_hexhash('md5')}]

    releases = dict([('%d.%d.%d' % (v.major, v.minor, v.micro),
                      version_release_info(v)) for v in versions])
    return releases


def package_releases(version_class, request, package_name):
    '''
    Args
    ----

        version_class (django.db.models.Model) : Version model class.
        request : Django request instance.
        package_name (string) : Name of package.

    Returns
    -------

        (dict) : Dictionary of releases info corresponding to the available
            published versions of the specified package.  See
            `PACKAGE_RELEASES_SCHEMA` for format.
    '''
    versions = (version_class.objects
                .filter(publish=True, package__name=package_name))
    base_uri = (request.build_absolute_uri()
                .replace(r'/plugins/%s/json/' % package_name, ''))
    data = {'releases': releases_info(versions, base_uri=base_uri)}
    # Validation requires Python 2.7+
    # jsonschema.validate(data, PACKAGE_RELEASES_SCHEMA)
    return HttpResponse(json.dumps(data), content_type='application/json')


def packages(version_class, request):
    package_versions = (version_class.objects.filter(package__public=True,
                                                     publish=True)
                        .order_by('package__name', '-major', '-minor',
                                  '-micro'))
    latest_versions = unique(package_versions, key=lambda v: v.package.name,
                             sort=False)
    uri = request.build_absolute_uri()
    data = {'packages': dict([(v.package.name,
                               {'latest_version': '%s.%s.%s' % (v.major,
                                                                v.minor,
                                                                v.micro),
                                'latest_url':
                                request.build_absolute_uri(v.url()),
                                'package_url': uri.replace('json/', '%s/json/'
                                                           % v.package.name)})
                              for v in latest_versions])}
    # Validation requires Python 2.7+
    # jsonschema.validate(data, PACKAGES_SCHEMA)
    return HttpResponse(json.dumps(data), content_type='application/json')
