class collectd::plugin::opentsdb (
  $server,
  $port,
  $path = '/opt/collectd-opentsdb',
  $ensure = present) {
  include collectd::params

  $conf_dir = $collectd::params::plugin_conf_dir

  file { 'collectd-opentsdb':
    ensure  => $collectd::plugin::opentsdb::ensure,
    path    => $path,
    mode    => '0644',
    owner   => 'root',
    group   => 'root',
    purge   => true,
    recurse => true,
    source  => 'puppet:///modules/collectd/opentsdb',
    notify  => Service['collectd']
  }

  concat::fragment { 'collectd.opentsdb.conf':
    target  => "${conf_dir}/java.conf",
    content => template("collectd/opentsdb.conf.erb"),
    order   => 5,
    require => File["collectd-opentsdb"]
  }
}
