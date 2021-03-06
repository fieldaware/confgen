import sys
import os
from os.path import join, isfile

from jinja2 import Environment, FileSystemLoader, StrictUndefined, exceptions

import tabulate
from logging import getLogger

log = getLogger(__name__)


class Renderer(object):
    templates_dir = 'templates'
    ignore_exts = ["swp", "swo"]

    def __init__(self, home):
        self.home = home
        self.jinja_environ = Environment(
            loader=FileSystemLoader(join(home, self.templates_dir)),
            undefined=StrictUndefined
        )

    def service(self, node, anon_service=False):
        if anon_service:
            template_subdir = ''
        else:
            template_subdir = node.name
        templates_path = join(self.home, self.templates_dir, template_subdir)
        rendered = {}
        for template in (i for i in os.listdir(templates_path) if isfile(join(templates_path, i))):
            if any([template.endswith(i) for i in self.ignore_exts]):
                log.warning('Ignoring file: {} because of its extension'.format(template))
                continue
            rendered[template] = self.render_template(join(template_subdir, template), node)
        return rendered

    def render_template(self, path, inventory):
        try:
            return self.jinja_environ.get_template(path).render(inventory.as_dict)
        except Exception as e:
            log.error("while rendering: {} ({})".format(
                join(inventory.path, path), e.message))
            sys.exit(1)

    @staticmethod
    def render_search_result(result):
        table = []
        for path, inventory in result:
            for ikey, ivalue in inventory.items():
                table.append((path, ikey, ivalue))

        return tabulate.tabulate(table, ['path', 'key', 'value'], tablefmt='psql')
