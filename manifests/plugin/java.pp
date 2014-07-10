class collectd::plugin::java (
  $classpath = '-Djava.class.path=/usr/share/collectd/java/collectd-api.jar:/usr/share/collectd/java/generic-jmx.jar'
) {

  include collectd::params

  $conf_dir = $collectd::params::plugin_conf_dir

  concat { "${conf_dir}/java.conf":
    owner   => root,
    group   => root,
    mode    => 644,
    notify  => Service['collectd']
  }

  concat::fragment { 'collectd.java.header.conf':
    target  => "${conf_dir}/java.conf",
    content => template("collectd/java.header.conf.erb"),
    order   => 1,
  }

  concat::fragment { 'collectd.java.footer.conf':
    target  => "${conf_dir}/java.conf",
    content => template("collectd/java.footer.conf.erb"),
    order   => 8,
  }
}
