import collectd
import requests
import json
import time

# main configuration
TSDB_HOST = 'localhost'
TSDB_PORT = '443'
TSDB_PUT_URL = 'https://localhost:443/api/put'
TSDB_CA   = '/dev/null'
TSDB_CERT = '/dev/null'
TSDB_KEY  = '/dev/null'
TAGS = { 'host': 'opentsdb01', 'dc': 'int' }

SESSION = requests.Session()

def config(cfg):
  global TSDB_HOST, TSDB_PORT, TSDB_PUT_URL, TSDB_CA, TSDB_CERT, TSDB_KEY
  for node in cfg.children:
    if node.key == 'server':
      TSDB_HOST = node.values[0]
    elif node.key == 'port':
      TSDB_PORT = node.values[0]
    elif node.key == 'ca':
      TSDB_CA   = node.values[0]
    elif node.key == 'cert':
      TSDB_CERT = node.values[0]
    elif node.key == 'key':
      TSDB_KEY  = node.values[0]
    else:
      collectd.warning('tsdb plugin: Unknown config key: %s.' % node.key)
  TSDB_PUT_URL = 'https://%s:%s/api/put' % (TSDB_HOST, TSDB_PORT)

def value_to_hash(val):
  global TAGS

  ret = {
    'timestamp': val.time,
    'tags': TAGS.copy(),
    'value': val.values[0],
  }

  if val.plugin == 'cpu':
    ret['metric'] = 'sys.cpu.%s' % val.type_instance
    ret['tags']['core'] = val.plugin_instance
  elif val.plugin == 'entropy':
    ret['metric'] = 'sys.entropy'
  elif val.plugin == 'memory':
    ret['metric'] = 'sys.memory.%s' % val.type_instance
  elif val.plugin == 'swap' and val.type == 'swap':
    ret['metric'] = 'sys.memory.swap_%s' % val.type_instance
  elif val.plugin == 'swap' and val.type == 'swap_io':
    ret['metric'] = 'sys.io.swap_%s' % val.type_instance
  elif val.plugin == 'processes' and val.type == 'ps_state':
    ret['metric'] = 'sys.processes.%s' % val.type_instance
  elif val.plugin == 'processes' and val.type == 'fork_rate':
    ret['metric'] = 'sys.fork_rate'
  elif val.plugin == 'contextswitch':
    ret['metric'] = 'sys.contextswitches'
  elif val.plugin == 'load':
    ret['metric'] = 'sys.load'
    ret = [ ret.copy(), ret.copy(), ret.copy() ]
    ret[0]['metric'] += '.1m'
    ret[0]['value'] = val.values[0]
    ret[1]['metric'] += '.5m'
    ret[1]['value'] = val.values[1]
    ret[2]['metric'] += '.15m'
    ret[2]['value'] = val.values[2]
  elif val.plugin == 'interface':
    ret['metric'] = 'sys.if.%s.%s' % (val.plugin_instance, val.type)
  elif val.plugin == 'df':
    ret['metric'] = 'sys.df.%s.%s' % (val.plugin_instance, val.type_instance)
  elif val.plugin == 'users':
    ret['metric'] = 'sys.users'
  else:
    ret['metric'] = ".".join([ x for x in ['default', val.plugin, val.plugin_instance, val.type, val.type_instance] if x])

  return ret


def write(vl, data=None):
  global TSDB_HOST, TSDB_PORT, TSDB_PUT_URL, TSDB_CA, TSDB_CERT, TSDB_KEY, SESSION
  data = value_to_hash(vl)
  if data != None:
    r = SESSION.post(TSDB_PUT_URL, data=json.dumps(data), verify=TSDB_CA, cert = (TSDB_CERT, TSDB_KEY))
    if r.status_code != 204:
      print "ERROR: %s.%s (%s.%s): %s" % (vl.plugin, vl.plugin_instance, vl.type, vl.type_instance, vl.values)
      print data
      print "%i: %s" % (r.status_code, r.content)
    elif vl.plugin != 'irq':
      print "HANDLED: %s.%s (%s.%s)" % (vl.plugin, vl.plugin_instance, vl.type, vl.type_instance)
  else:
    if vl.plugin == None:
      print "MISSED: %s.%s (%s.%s): %s" % (vl.plugin, vl.plugin_instance, vl.type, vl.type_instance, vl.values)
      # print "MISSED: meta of %s: %s" % (vl.plugin, vl.meta)


collectd.register_config(config)
collectd.register_write(write)
