class collectd::plugin::opentsdb (
  $server,
  $port,
  $path   = '/opt/collectd-opentsdb',
  $ensure = present,
  $ca     = inline_template("<%= Puppet[:localcacert] %>"),
  $cert   = inline_template("<%= Puppet[:certdir] %>/${::fqdn}.pem"),
  $key    = inline_template("<%= Puppet[:privatekeydir] %>/${::fqdn}.pem")) {
  include collectd::params
  include collectd::plugin::python

  $conf_dir = $collectd::params::plugin_conf_dir

  package { 'python-requests':
    ensure => installed,
    notify => Service['collectd'];
  }

  file { 'collectd-opentsdb':
    ensure  => $collectd::plugin::opentsdb::ensure,
    path    => $path,
    mode    => '0644',
    owner   => 'root',
    group   => 'root',
    purge   => true,
    recurse => true,
    force   => true,
    ignore  => ['*.pyc'],
    source  => 'puppet:///modules/collectd/opentsdb',
    notify  => Service['collectd']
  }

  concat::fragment { 'collectd.opentsdb.conf':
    target  => "${conf_dir}/python.conf",
    content => template("collectd/opentsdb.conf.erb"),
    order   => 5,
    require => File["collectd-opentsdb"]
  }
}
