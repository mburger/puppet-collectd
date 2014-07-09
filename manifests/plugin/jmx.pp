class collectd::plugin::jmx ( ) {

  include collectd::params

  $conf_dir = $collectd::params::plugin_conf_dir

  concat { "${conf_dir}/jmx.conf":
    owner   => root,
    group   => root,
    mode    => 644,
    notify  => Service['collectd']
  }

  concat::fragment { 'collectd.jmx.header.conf':
    target  => "${conf_dir}/jmx.conf",
    content => template("collectd/jmx.header.conf.erb"),
    order   => 1,
  }

  concat::fragment { 'collectd.jmx.footer.conf':
    target  => "${conf_dir}/jmx.conf",
    content => template("collectd/jmx.footer.conf.erb"),
    order   => 3,
  }
}
