import os
from os.path import join, isfile

from jinja2 import Environment, FileSystemLoader

import tabulate

class Renderer(object):
    templates_dir = 'templates'

    def __init__(self, services, home):
        self.home = home
        self.services = services
        self.jinja_environ = Environment(loader=FileSystemLoader(join(home, self.templates_dir)))

    def collect_templates(self, services):
        templates = {}
        for service in services:
            service_template_dir = join(self.home, self.templates_dir, service)
            templates[service] = [join(service, f) for f in os.listdir(service_template_dir) if isfile(join(service_template_dir, f))]
        return templates

    def render_multiple_templates(self, services, template_inventory):
        renders = {}
        for service in services:
            renders.update(self.render_templates(service, template_inventory))
        return renders

    def render_templates(self, service, template_inventory):
        renders = {}
        templates = self.collect_templates(self.services)
        for template in templates[service]:
            renders[template] = self.jinja_environ.get_template(template).render(template_inventory or {})
        return renders

    def render_search_result(self, result):
        table = []
        for path, inventory in result.items():
            for ikey, ivalue in inventory.items():
                table.append((path, ikey, ivalue))

        return tabulate.tabulate(table, ['path', 'key', 'value'], tablefmt='psql')
