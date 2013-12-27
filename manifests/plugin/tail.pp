class collectd::plugin::tail ( ) {
  include collectd::params

  $conf_dir = $collectd::params::plugin_conf_dir

  concat { "${conf_dir}/tail.conf":
    owner   => root,
    group   => root,
    mode    => 644,
    notify  => Service['collectd']
  }

  concat::fragment { 'collectd.tail.header.conf':
    target  => "${conf_dir}/tail.conf",
    content => template("collectd/tail.header.conf.erb"),
    order   => 1,
  }

  concat::fragment { 'collectd.tail.footer.conf':
    target  => "${conf_dir}/tail.conf",
    content => "</Plugin>",
    order   => 3,
  }
}
