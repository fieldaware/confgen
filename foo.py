SERVICES = ['auth', 'ipsec-mngt']
CLUSTERS = [
  Item('mngt', as_keys=SERVICES),
  Item('test1', as_keys=SERVICES),
]
DCS = [
  Item('eu1', as_keys=CLUSTERS),
  Item('eu2', as_keys=CLUSTERS),
]
GLOBAL = Item(as_keys=DCS, as_attributes={'foo': 8})
GLOBAL['eu1']

# tree = Node('root', nodes=[
#     [Node('eu1', nodes=[
#         Node('mngt',)), Node('eu2', nodes=)]
# ])
for dc in GLOBAL:
  for cluster in dc:
    for service in cluster:
      print dc, cluster, service
      # inventory at each level
      dc.foo
      cluster.foo
      service.foo

{% for dc in GLOBAL %}
  {% for cluster in dc %}
    conn {{DC}}-{{CLUSTER}}-{{dc}}
      subnet={{cluster.subnet}}
      endpoint={{cluster.endpoint}}
  {% endfor %}
{% endfor %}
