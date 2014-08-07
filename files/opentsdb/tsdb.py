import collectd
import re

from json import dumps
from pprint import pprint
from Queue import Queue, Empty
from requests import Session
from threading import Lock
from time import time

# main configuration
TSDB_HOST = 'localhost'
TSDB_PORT = '443'
TSDB_PUT_URL = 'https://localhost:443/api/put'
TSDB_CA   = '/dev/null'
TSDB_CERT = '/dev/null'
TSDB_KEY  = '/dev/null'
TAGS = { }

SESSION = None
QUEUE = None
LAST_POST = None
POST_LOCK = None


# monotonic_time from http://stackoverflow.com/a/1205762
import ctypes, os

CLOCK_MONOTONIC_RAW = 4 # see <linux/time.h>

class timespec(ctypes.Structure):
  _fields_ = [
    ('tv_sec', ctypes.c_long),
    ('tv_nsec', ctypes.c_long)
  ]

librt = ctypes.CDLL('librt.so.1', use_errno=True)
clock_gettime = librt.clock_gettime
clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]

def monotonic_time():
  t = timespec()
  if clock_gettime(CLOCK_MONOTONIC_RAW , ctypes.pointer(t)) != 0:
    errno_ = ctypes.get_errno()
    raise OSError(errno_, os.strerror(errno_))
  return t.tv_sec + t.tv_nsec * 1e-9
# end monotonic_time


def init():
  global SESSION, QUEUE, LAST_POST, POST_LOCK
  SESSION = Session()
  QUEUE = Queue()
  LAST_POST = monotonic_time()
  POST_LOCK = Lock()


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


def create_self_metric(events, last_post, now):
  ts = time()
  return [
    {
      'metric': 'sys.collectd.events',
      'timestamp': ts,
      'tags': TAGS.copy(),
      'value': events,
    },
    {
      'metric': 'sys.collectd.queue_dur_s',
      'timestamp': ts,
      'tags': TAGS.copy(),
      'value': now - last_post,
    }]


def try_post():
  global TAGS, TSDB_PUT_URL, TSDB_CA, TSDB_CERT, TSDB_KEY, SESSION, QUEUE, LAST_POST, POST_LOCK
  second_last_post = LAST_POST
  to_post = []

  POST_LOCK.acquire()
  try:
    now = monotonic_time()
    if LAST_POST + 10 < now or QUEUE.qsize() > 1024:
      LAST_POST = now
      try:
        while True:
          to_post.append(QUEUE.get_nowait())
      except Empty:
        pass
  finally:
    POST_LOCK.release()

  if len(to_post) > 0:
    to_post.extend(create_self_metric(len(to_post), second_last_post, LAST_POST))
    print "Posting %i events" % len(to_post)
    r = SESSION.post(TSDB_PUT_URL, data=dumps(to_post), verify=TSDB_CA, cert = (TSDB_CERT, TSDB_KEY))
    if r.status_code == 204:
      print "Posted %i events" % len(to_post)
    else:
      print "%i: error received" % r.status_code
      print pprint(r.content)
      print pprint(to_post)[:1024]


def write(vl, data=None):
  data = value_to_hash(vl)
  if data != None:
    if isinstance(data, dict):
      QUEUE.put(data)
    else:
      for d in data:
        QUEUE.put(d)
  else:
    if vl.plugin == None:
      print "MISSED: %s.%s (%s.%s): %s" % (vl.plugin, vl.plugin_instance, vl.type, vl.type_instance, vl.values)
      # print "MISSED: meta of %s: %s" % (vl.plugin, vl.meta)
  try_post()


collectd.register_init(init)
collectd.register_config(config)
collectd.register_write(write)
