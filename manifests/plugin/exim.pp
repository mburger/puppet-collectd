class collectd::plugin::exim (
  $ensure         = present
) {
  include collectd::params

  $conf_dir = $collectd::params::plugin_conf_dir

  file { 'collectd.exim.conf':
    ensure    => $collectd::plugin::exim::ensure,
    path      => "${conf_dir}/exim.conf",
    mode      => '0644',
    owner     => 'root',
    group     => 'root',
    content   => template('collectd/exim.conf.erb'),
    notify    => Service['collectd']
  }

}
