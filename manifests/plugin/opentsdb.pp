class collectd::plugin::opentsdb ($server, $port, $jvm_args = 'UNSET', $ensure = present) {
  include collectd::params

  $conf_dir = $collectd::params::plugin_conf_dir

  file { 'collectd-opentsdb':
    ensure  => $collectd::plugin::opentsdb::ensure,
    path    => "/srv/collectd-opentsdb",
    mode    => '0644',
    owner   => 'root',
    group   => 'root',
    purge   => true,
    recurse => true,
    source  => 'puppet:///modules/collectd/opentsdb',
    notify  => Service['collectd']
  }

  file { 'opentsdb.conf':
    ensure  => $collectd::plugin::opentsdb::ensure,
    path    => "${conf_dir}/opentsdb.conf",
    mode    => '0644',
    owner   => 'root',
    group   => 'root',
    content => template('collectd/opentsdb.conf.erb'),
    notify  => Service['collectd'],
    require => File["collectd-opentsdb"]
  }
}
