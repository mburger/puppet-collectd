from pyjolokia import Jolokia
import collectd
import re


JOLOKIA_CONNECTIONS = {}
# TODO: Fix me
JOLOKIA_MBEANS = ['java.lang:type=Memory', 'java.lang:type=GarbageCollector,*', 'java.lang:type=Threading', '*:type=GlobalRequestProcessor,*', '*:type=Manager,*']
VERBOSE_LOGGING = False

def configure_callback(conf):
  """Receive configuration block"""
  global JOLOKIA_CONNECTIONS
  for node in conf.children:
    if node.key == 'connection':
      JOLOKIA_CONNECTIONS[node.values[0]] = {}
      JOLOKIA_CONNECTIONS[node.values[0]['instance']] = node.values[1]
    elif node.key == 'verbose':
      VERBOSE_LOGGING = bool(node.values[0])
    else:
      collectd.warning('jolokia plugin: Unknown config key: %s.' % node.key)
  init_jolokia()

def init_jolokia():
  global JOLOKIA_CONNECTIONS
  global JOLOKIA_MBEANS
  for connection in JOLOKIA_CONNECTIONS.keys():
    j4p = Jolokia(connection)
    for bean in JOLOKIA_MBEANS:
      j4p.add_request(type = 'read', mbean=bean)
    JOLOKIA_CONNECTIONS[connection]['j4p'] = j4p

def log_verbose(msg):
  if not VERBOSE_LOGGING:
    return
  collectd.info('jolokia plugin [verbose]: %s' % msg)

def fetch_info():
  """Connect to Jolokia server and request mbeans"""
  global JOLOKIA_CONNECTIONS
  try:
    for connection in JOLOKIA_CONNECTIONS.keys():
      data = JOLOKIA_CONNECTIONS[connection]['j4p'].getRequests()
      for ele in data:
        parse_info(ele, JOLOKIA_CONNECTIONS[connection]['instance'])
  except Exception, e:
    collectd.error('jolokia plugin: Error - %r' % e)
    return None

def dispatch_value(type_instance, value, instance, type='gauge'):
  """Dispatch a given Value"""

  val = collectd.Values(plugin='jolokia')
  val.plugin_instance = instance
  val.type = type
  val.type_instance = type_instance
  val.values = [int(value)]
  val.dispatch()

def read_callback():
  log_verbose('Read callback called')
  fetch_info()

def parse_info(data, instance, name=''):
  value = data['value']
  if type(value) is dict:
    parse_dict(name, data, instance)
  else:
    ele_name = construct_name(name, data['request']['mbean'])
    dispatch_value(ele_name, ele_data, instance)


def parse_dict(name, data, instance):
  for ele_name, ele_data in data.iteritems():
    if 'status' in ele_name: continue
    ele_name = construct_name(name, ele_name)
    if type(ele_data) is dict:
      parse_dict(ele_name, ele_data)
    else:
      if type(ele_data) is int or type(ele_data) is float:
        dispatch_value(ele_name, ele_data, instance)

def construct_name(*args):
  names = []
  for ele in args:
    if ele not in ['status', 'value']:
      for match in ['java.lang:name=', 'type=', ',', ' ', 'name=', '"']:
        ele = ele.replace(match, '')
      for match in ['=', '/', '-', ':']:
        ele = ele.replace(match, '_')
      ele = ele.replace('__', '_')
      names.append(convert_to_camelcase(ele))
  return '.'.join(names)

def convert_to_camelcase(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

# register callbacks
collectd.register_config(configure_callback)
collectd.register_read(read_callback)
