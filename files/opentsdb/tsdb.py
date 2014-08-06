import collectd
import json
import re
import requests
import time

# main configuration
TSDB_HOST = 'localhost'
TSDB_PORT = '443'
TSDB_PUT_URL = 'https://localhost:443/api/put'
TSDB_CA   = '/dev/null'
TSDB_CERT = '/dev/null'
TSDB_KEY  = '/dev/null'
TAGS = { }

SESSION = requests.Session()


def config(cfg):
  global TSDB_HOST, TSDB_PORT, TSDB_PUT_URL, TSDB_CA, TSDB_CERT, TSDB_KEY, TAGS
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
    elif node.key == 'tag':
      TAGS[node.values[0]] = node.values[1]
    else:
      collectd.warning('tsdb plugin: Unknown config key: %s.' % node.key)
  TSDB_PUT_URL = 'https://%s:%s/api/put' % (TSDB_HOST, TSDB_PORT)


def metric(*arr):
  return ".".join([ re.sub(r'[^-_a-z0-9.]', '_', x.lower()) for x in arr if x])


def value_to_hash(val):
  global TAGS

  ret = {
    'timestamp': val.time,
    'tags': TAGS.copy(),
    'value': val.values[0],
  }

  if val.plugin == 'cpu':
    ret['metric'] = metric('sys.cpu', val.type_instance)
    ret['tags']['core'] = val.plugin_instance
  elif val.plugin == 'entropy':
    ret['metric'] = 'sys.entropy'
  elif val.plugin == 'memory':
    ret['metric'] = metric('sys.memory', val.type_instance)
  elif val.plugin == 'swap' and val.type == 'swap':
    ret['metric'] = metric('sys.memory', 'swap_%s' % val.type_instance)
  elif val.plugin == 'swap' and val.type == 'swap_io':
    ret['metric'] = metric('sys.io', 'swap_%s' % val.type_instance)
  elif val.plugin == 'processes' and val.type == 'ps_state':
    ret['metric'] = metric('sys.processes', val.type_instance)
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
    ret['metric'] = metric('sys.if', val.plugin_instance, val.type)
  elif val.plugin == 'df':
    ret['metric'] = metric('sys.df', val.plugin_instance, val.type_instance)
  elif val.plugin == 'users':
    ret['metric'] = 'sys.users'
  elif val.plugin == 'postgresql':
    ret['metric'] = metric('db', val.type, val.type_instance)
    ret['tags']['db'] = val.plugin_instance
  elif val.plugin == 'mongodb':
    ret['metric'] = metric('db', val.plugin, val.type_instance)
  else:
    ret['metric'] = metric('default', val.plugin, val.plugin_instance, val.type, val.type_instance)

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
    elif vl.plugin == 'postgresql':
      print "HANDLED: %s (%f)" % (data['metric'], data['value'])
      print data
  else:
    if vl.plugin == None:
      print "MISSED: %s.%s (%s.%s): %s" % (vl.plugin, vl.plugin_instance, vl.type, vl.type_instance, vl.values)
      # print "MISSED: meta of %s: %s" % (vl.plugin, vl.meta)


collectd.register_config(config)
collectd.register_write(write)
