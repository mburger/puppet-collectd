define collectd::plugin::jolokia::connection (
  $url,
  $instance
) {

  include collectd::plugin::jolokia

  $conf_dir = $collectd::params::plugin_conf_dir

  concat::fragment { "collectd.jolokia.conf_${name}":
    target  => "${conf_dir}/python.conf",
    content => template("collectd/jolokia.connection.conf.erb"),
    order   => 7,
    require => File["collectd-jolokia"]
  }
}
