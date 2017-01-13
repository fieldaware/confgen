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

    def render_templates(self, path, template_inventory):
        renders = {}
        templates = self.collect_templates(self.services)
        service = path.split('/')[-1]
        for template in templates[service]:
            renders[template.split('/')[-1]] = self.jinja_environ.get_template(template).render(template_inventory or {})
        return renders

    def render_search_result(self, result):
        table = []
        for path, inventory in result.items():
            for ikey, ivalue in inventory.items():
                table.append((path, ikey, ivalue))

        return tabulate.tabulate(table, ['path', 'key', 'value'], tablefmt='psql')
