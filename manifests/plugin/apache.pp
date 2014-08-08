class collectd::plugin::apache (
  $ensure         = present,
  $instance_name  = $::fqdn,
  $url            = 'http://localhost/mod-status?auto',
  $verify_peer    = false,
  $verify_host    = false
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
