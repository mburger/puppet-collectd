class collectd::plugin::rabbitmq (
  $ensure   = present,
  $path     = '/opt/collectd-rabbitmq',
  $verbose  = false,
  $username = 'guest',
  $password = 'guest',
  $realm    = 'RabbitMQ Management',
  $host     = '127.0.0.1',
  $port     = 15672,
  ) {
  include collectd::params
  include collectd::plugin::python
  $conf_dir = $collectd::params::plugin_conf_dir

  file { 'collectd-rabbitmq':
    ensure  => $collectd::plugin::rabbitmq::ensure,
    path    => $path,
    mode    => '0644',
    owner   => 'root',
    group   => 'root',
    purge   => true,
    recurse => true,
    force   => true,
    ignore  => ['*.pyc'],
    source  => 'puppet:///modules/collectd/rabbitmq',
    notify  => Service['collectd']
  }

  concat::fragment { 'collectd.rabbitmq.conf':
    target  => "${conf_dir}/python.conf",
    content => template("collectd/rabbitmq.conf.erb"),
    order   => 5,
    require => File["collectd-rabbitmq"]
  }
}
