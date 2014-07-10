class collectd::plugin::jmx ( ) {

  include collectd::params
  include collectd::plugin::java

  $conf_dir = $collectd::params::plugin_conf_dir

  concat::fragment { 'collectd.jmx.header.conf':
    target  => "${conf_dir}/java.conf",
    content => template("collectd/jmx.header.conf.erb"),
    order   => 2,
  }

  concat::fragment { 'collectd.jmx.footer.conf':
    target  => "${conf_dir}/java.conf",
    content => template("collectd/jmx.footer.conf.erb"),
    order   => 4,
  }
}
