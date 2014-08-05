class collectd::plugin::python {
  include collectd::params

  $conf_dir = $collectd::params::plugin_conf_dir

  concat { "${conf_dir}/python.conf":
    owner  => root,
    group  => root,
    mode   => 644,
    notify => Service['collectd']
  }

  concat::fragment { 'collectd.python.header.conf':
    target  => "${conf_dir}/python.conf",
    content => template("collectd/python.header.conf.erb"),
    order   => 1,
  }

  concat::fragment { 'collectd.python.footer.conf':
    target  => "${conf_dir}/python.conf",
    content => template("collectd/python.footer.conf.erb"),
    order   => 8,
  }

  package { 'python-requests':
    ensure => installed,
    notify => Service['collectd'];
  }
}
