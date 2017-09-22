import sys
import os
from os.path import join, isfile

from jinja2 import Environment, FileSystemLoader, StrictUndefined, exceptions

import tabulate
from logging import getLogger

log = getLogger(__name__)


class Renderer(object):
    templates_dir = 'templates'

    def __init__(self, home):
        self.home = home
        self.jinja_environ = Environment(
            loader=FileSystemLoader(join(home, self.templates_dir)),
            undefined=StrictUndefined
        )

    def service(self, leaf):
        templates_path = join(self.home, self.templates_dir, leaf.name)
        rendered = {}
        for template in (i for i in os.listdir(templates_path) if isfile(join(templates_path, i))):
            rendered[template] = self.render_template(join(leaf.name, template), leaf)
        return rendered

    def render_template(self, path, inventory):
        try:
            return self.jinja_environ.get_template(path).render(inventory.as_dict)
        except exceptions.UndefinedError as e:
            log.error("while rendering: {} ({})".format(path, e.message))
            sys.exit(1)

    @staticmethod
    def render_search_result(result):
        table = []
        for path, inventory in result.items():
            for ikey, ivalue in inventory.items():
                table.append((path, ikey, ivalue))

        return tabulate.tabulate(table, ['path', 'key', 'value'], tablefmt='psql')
