class collectd::plugin::elasticsearch (
  $ensure   = present,
  $path     = '/opt/collectd-elasticsearch',
  $cluster  = 'elasticsearch',
  $verbose  = false,
  $version  = '1.0',
  $host     = 'localhost',
  $port     = 9200
  ) {
  include collectd::params
  include collectd::plugin::python
  $conf_dir = $collectd::params::plugin_conf_dir

  file { 'collectd-elasticsearch':
    ensure  => $collectd::plugin::elasticsearch::ensure,
    path    => $path,
    mode    => '0644',
    owner   => 'root',
    group   => 'root',
    purge   => true,
    recurse => true,
    force   => true,
    ignore  => ['*.pyc'],
    source  => 'puppet:///modules/collectd/elasticsearch',
    notify  => Service['collectd']
  }

  concat::fragment { 'collectd.elasticsearch.conf':
    target  => "${conf_dir}/python.conf",
    content => template("collectd/elasticsearch.conf.erb"),
    order   => 5,
    require => File["collectd-elasticsearch"]
  }
}
