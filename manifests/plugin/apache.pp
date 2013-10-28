class collectd::plugin::apache (
  $ensure         = present
) {
  include collectd::params

  $conf_dir = $collectd::params::plugin_conf_dir

  file { 'collectd.apache.conf':
    ensure    => $collectd::plugin::apache::ensure,
    path      => "${conf_dir}/apache.conf",
    mode      => '0644',
    owner     => 'root',
    group     => 'root',
    content   => template('collectd/apache.conf.erb'),
    notify    => Service['collectd']
  }

}
