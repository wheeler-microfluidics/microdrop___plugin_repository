from django_jsonrpc import jsonrpc_method
from django.shortcuts import redirect

from .models import Plugin as package_class, PluginVersion as version_class

import repository.views 


@jsonrpc_method('plugins.available_packages')
def available_packages(request):
    return repository.views.available_packages(package_class, request)


@jsonrpc_method('plugins.package_latest_version')
def package_latest_version(request, package_name):
    return repository.views.package_latest_version(version_class, request,
            package_name)


@jsonrpc_method('plugins.package_versions')
def package_versions(request, package_name):
    return repository.views.package_versions(version_class, request, package_name)


@jsonrpc_method('plugins.package_url')
def package_url(request, package_name, version):
    return repository.views.package_url(version_class, request, package_name,
            version)


def redirect_to_latest(request, package_name):
    latest_version = package_latest_version(request, package_name)
    return redirect(package_url(request, package_name, latest_version))
