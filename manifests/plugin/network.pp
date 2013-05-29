class collectd::plugin::network ($server = 'UNSET', $listen = 'UNSET', $ensure = present) {
  include collectd::params

  $conf_dir = $collectd::params::plugin_conf_dir

  file { 'network.conf':
    ensure  => $collectd::plugin::network::ensure,
    path    => "${conf_dir}/network.conf",
    mode    => '0644',
    owner   => 'root',
    group   => 'root',
    content => template('collectd/network.conf.erb'),
    notify  => Service['collectd']
  }
}
