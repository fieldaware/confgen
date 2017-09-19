import sys
import os
from os.path import join, isfile

from jinja2 import Environment, FileSystemLoader, StrictUndefined, exceptions

import tabulate
from logging import getLogger

log = getLogger(__name__)


class Renderer(object):
    templates_dir = 'templates'

    def __init__(self, services, home):
        self.home = home
        self.services = services
        self.jinja_environ = Environment(
            loader=FileSystemLoader(join(home, self.templates_dir)),
            undefined=StrictUndefined
        )

    def collect_templates_for_services(self, services):
        return {service: self.collect_templates_for_service(service) for service in services}

    def collect_templates_for_service(self, service):
        service_template_dir = join(self.home, self.templates_dir, service)
        return [join(service, f) for f in sorted(os.listdir(service_template_dir)) if isfile(join(service_template_dir, f))]

    def render_templates_for_services(self, services, template_inventory):
        renders = {}
        for service in services:
            renders.update(self.render_templates_for_service(service, template_inventory))
        return renders

    def render_templates_for_service(self, service, template_inventory):
        renders = {}
        templates = self.collect_templates_for_services(self.services)
        for template in templates[service]:
            try:
                renders[template] = (self.jinja_environ.get_template(template)
                                     .render(template_inventory.data or {}))
            except exceptions.UndefinedError as e:
                log.error("while rendering: {} ({})".format(template, e.message))
                sys.exit(1)
        return renders

    @staticmethod
    def render_search_result(result):
        table = []
        for path, inventory in result.items():
            for ikey, ivalue in inventory.items():
                table.append((path, ikey, ivalue))

        return tabulate.tabulate(table, ['path', 'key', 'value'], tablefmt='psql')
