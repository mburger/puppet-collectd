class collectd::plugin::exim ( ) {
  include collectd::params
  include collectd::plugin::tail

  $conf_dir = $collectd::params::plugin_conf_dir

  concat::fragment { 'collectd.tail.exim.conf':
    target  => "${conf_dir}/tail.conf",
    content => template('collectd/exim.conf.erb'),
    order   => 5,
  }

}
