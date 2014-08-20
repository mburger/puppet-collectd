import collectd
from pymongo import Connection

MONGO_CONNECTION_STRING = 'mongodb://localhost'
MONGO_DB_NAME           = 'admin'
VERBOSE_LOGGING         = False


def configure_callback(conf):
    """Receive configuration block"""
    global MONGO_CONNECTION_STRING
    for node in conf.children:
        if node.key == 'connection':
            MONGO_CONNECTION_STRING = node.values[0]
        elif node.key == 'database':
            MONGO_DB_NAME = node.values[0]
        elif node.key == 'verbose':
            VERBOSE_LOGGING = bool(node.values[0])
        else:
            collectd.warning('mongodb plugin: Unknown config key: %s.'
                             % node.key)
    log_verbose('Configured with connection=%s' % (MONGO_CONNECTION_STRING))


def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('mongodb plugin [verbose]: %s' % msg)

def fetch_info():
    """Connect to Mongodb server and request server status"""
    try:
        connection = Connection(MONGO_CONNECTION_STRING)
        db = connection[MONGO_DB_NAME]
        server_status = db.command("serverStatus")
        log_verbose('Connected to Mongodb with %s' % (MONGO_CONNECTION_STRING))
    except e:
        collectd.error('mongo plugin: Error connecting to %s - %r' % (MONGO_CONNECTION_STRING, e))
        return None
    return parse_info(server_status)

def dispatch_value(type_instance, value, type='gauge'):
    """Dispatch a diven Values"""

    val = collectd.Values(plugin='mongodb')
    val.type = type
    val.type_instance = type_instance
    val.values = [int(value)]
    val.dispatch()


def parse_info(data):
    """Parse info response from Mongo and dispatch the Metrics"""
    # db locks
    for db_name, val in data['locks'].iteritems():
        for metric, sub_val in val.iteritems():
            for sub_metric, metric_value in sub_val.iteritems():
                name = 'serverstatus.locks.%s.%s.%s' % (db_name, metric, sub_metric)
                dispatch_value(name, metric_value)

    # global locks
    for metric in ['readers', 'writers']:
        for queue in ['currentQueue', 'activeClients']:
            name = 'serverstatus.globalLock.%s.%s' % (queue, metric)
            value = data['globalLock'][queue][metric]
            dispatch_value(name, value)

    for metric in ['totalTime', 'lockTime']:
        name = 'serverstatus.globalLock.%s' % (metric)
        value = data['globalLock'][metric]
        dispatch_value(name, value)

    lock_ratio = data['globalLock']['lockTime'] / data['globalLock']['totalTime']
    dispatch_value('serverstatus.globalLock.lockratio', lock_ratio)

    # memory
    for metric in ['resident', 'virtual', 'mapped']:
        name = 'serverstatus.mem.%s' % (metric)
        value = data['mem'][metric] * 1024 * 1024 # normalize values to bytes
        dispatch_value(name, value)

    # connections
    for metric in ['available', 'current', 'totalCreated' ]:
        name = 'serverstatus.connections.%s' % (metric)
        value = data['connections'][metric]
        dispatch_value(name, value)

    # extra info
    # NOTE: may vary by platform
    for metric in [x for x in data['extra_info'].keys() if x != 'note']:
        name = 'serverstatus.extra_info.%s' % (metric)
        value = data['extra_info'][metric]
        dispatch_value(name, value)

    # index counters
    for metric, value in data['indexCounters'].iteritems():
        name = 'serverstatus.indexCounters.%s' % (metric)
        dispatch_value(name, value)

    # background flushing
    for metric in ['flushes', 'last_ms', 'total_ms' ]:
        name = 'serverstatus.backgroundFlushing.%s' % (metric)
        value = data['backgroundFlushing'][metric]
        dispatch_value(name, value)

    # network
    for metric, value in data['network'].iteritems():
        name = 'serverstatus.network.%s' % (metric)
        dispatch_value(name, value)

    # asserts
    for metric, value in data['asserts'].iteritems():
        name = 'serverstatus.asserts.%s' % (metric)
        dispatch_value(name, value)

    # journalling
    for metric in ['commits', 'commitsInWriteLock', 'compression', 'earlyCommits', 'journaledMB', 'writeToDataFilesMB']:
        name = 'serverstatus.dur.%s' % (metric)
        value = data['dur'][metric]
        dispatch_value(name, value)

    # opcounters
    for metric, value in data['opcounters'].iteritems():
        name = 'serverstatus.opcounters.%s' % (metric)
        dispatch_value(name, value)

    # record stats
    for metric in ['accessesNotInMemory', 'pageFaultExceptionsThrown']:
        name = 'serverstatus.recordStats.%s' % (metric)
        value = data['recordStats'][metric]
        dispatch_value(name, value)
        data['recordStats'].pop(metric)
    for db_name in data['recordStats'].keys():
        for metric, value in data['recordStats'][db_name].iteritems():
            name = 'serverstatus.recordStats.%s.%s' % (db_name, metric)
            dispatch_value(name, value)

    # documents
    for metric, value in data['metrics']['document'].iteritems():
        name = 'serverstatus.metrics.documents.%s' % (metric)
        dispatch_value(name, value)


def read_callback():
    log_verbose('Read callback called')
    fetch_info()

# register callbacks
collectd.register_config(configure_callback)
collectd.register_read(read_callback)
