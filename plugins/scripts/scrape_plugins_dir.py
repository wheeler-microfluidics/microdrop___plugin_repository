from argparse import ArgumentParser
import logging
import sys
import tarfile

from path import path
import yaml

project_root = path(__file__).parent.parent.parent
sys.path.append(project_root)

from plugins.models import PluginVersion, Plugin, cre_plugin_info


logger = logging.getLogger(__name__)


def process_plugin_archive(plugin_path):
    match = cre_plugin_info.match(plugin_path.name)
    if match:
        major, minor, micro = (int(match.group('major')),
                               int(match.group('minor')),
                               int(match.group('micro')))

        t = tarfile.open(plugin_path)
        properties_path = [path(p) for p in t.getnames()
                           if 'properties.yml' in p][0]
        properties = yaml.load(t.extractfile(properties_path).read())

        plugin_name = properties.get('plugin_name', match.group('name'))
        plugin, created = Plugin.objects.get_or_create(name=match
                                                       .group('name'))
        plugin.plugin_name = plugin_name
        plugin.save()
        plugin_version, created = (PluginVersion.objects
                                   .get_or_create(package=plugin, major=major,
                                                  minor=minor, micro=micro))
        if created:
            print 'Added Plugin %s version %s.%s.%s' % (plugin.name,
                                                        plugin_version.major,
                                                        plugin_version.minor,
                                                        plugin_version.micro)


def scan_plugin(plugin_path):
    try:
        process_plugin_archive(plugin_path)
    except ValueError, why:
        logger.warning('skipping plugin archive %s:\n%s' % (plugin_path, why))


LOG_PARSER = ArgumentParser(add_help=False)
LOG_PARSER.add_argument('-l', '--log-level', default='error',
                        choices=['error', 'debug', 'info'])


def parse_args(args=None):
    '''Parses arguments, returns (options, args).'''
    if args is None:
        args = sys.argv

    parser = ArgumentParser(description='Microdrop plugin manager',
                            parents=[LOG_PARSER])
    subparsers = parser.add_subparsers(help='Mode', dest='command')
    file_parser = subparsers.add_parser('file', help='Scrape single file')
    file_parser.add_argument('plugin_file', help='Single plugin file to '
                             'scrape', type=path)

    dir_parser = subparsers.add_parser('directory', help='Scrape files in '
                                       'directory')
    dir_parser.add_argument('scrape_root', help='Directory to scrape',
                            default=project_root.joinpath('plugin_data'),
                            type=path, nargs='?')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    logging.basicConfig(format='[%(levelname)s] %(message)s',
                        level=getattr(logging, args.log_level.upper()))
    if args.command == 'directory':
        plugin_files = sorted(args.scrape_root.files('*.tar.gz'))
        for plugin_path_i in plugin_files:
            try:
                process_plugin_archive(plugin_path_i)
            except ValueError, exception:
                logger.warning('skipping plugin archive %s:\n%s' %
                               (plugin_path_i, exception))
    elif args.command == 'file':
        process_plugin_archive(args.plugin_file)
