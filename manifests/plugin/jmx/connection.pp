define collectd::plugin::jmx::connection (
  $host = 'localhost',
  $service_url,
  $username =  undef,
  $password = undef,
  $instance_prefix = $name,
) {

  include collectd::plugin::jmx
  include collectd::params

  $conf_dir = $collectd::params::plugin_conf_dir

  concat::fragment { "collectd.jmx.connection.${name}.conf":
    target  => "${conf_dir}/java.conf",
    content => template("collectd/jmx.connection.conf.erb"),
    order   => 3,
  }
}
