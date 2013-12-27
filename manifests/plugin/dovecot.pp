class collectd::plugin::dovecot ( ) {
  include collectd::params
  include collectd::plugin::tail

  $conf_dir = $collectd::params::plugin_conf_dir

  concat::fragment { 'collectd.tail.dovecot.conf':
    target  => "${conf_dir}/tail.conf",
    content => template('collectd/dovecot.conf.erb'),
  }

}
