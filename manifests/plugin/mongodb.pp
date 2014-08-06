class collectd::plugin::mongodb ($ensure = present, $path = '/opt/collectd-mongodb', $connection_string, $database) {
  include collectd::params
  include collectd::plugin::python
  $conf_dir = $collectd::params::plugin_conf_dir

  package { 'python-pymongo':
    ensure => installed,
    notify => Service['collectd'];
  }

  file { 'collectd-mongodb':
    ensure  => $collectd::plugin::mongodb::ensure,
    path    => $path,
    mode    => '0644',
    owner   => 'root',
    group   => 'root',
    purge   => true,
    recurse => true,
    force   => true,
    ignore  => ['*.pyc'],
    source  => 'puppet:///modules/collectd/mongodb',
    notify  => Service['collectd']
  }

  concat::fragment { 'collectd.mongodb.conf':
    target  => "${conf_dir}/python.conf",
    content => template("collectd/mongodb.conf.erb"),
    order   => 5,
    require => File["collectd-mongodb"]
  }
}
