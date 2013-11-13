class collectd::plugin::icinga (
  $user           = 'nagios',
  $ensure         = present
) {
  include collectd::params

  $conf_dir = $collectd::params::plugin_conf_dir

  $ensure_directory = $ensure ? {
    present => directory,
    absent  => absent,
  }

  file { 'collectd.exec.dir':
    ensure    => $collectd::plugin::icinga::ensure_directory,
    path      => "${collectd::params::collectd_dir}/bin",
    mode      => '0644',
    owner     => 'root',
    group     => 'root',
    require   => Package['collectd'],
  }

  file { 'collectd.check_icingastats':
    ensure    => $collectd::plugin::icinga::ensure,
    path      => "${collectd::params::collectd_dir}/bin/check_icingastats",
    mode      => '0755',
    owner     => 'root',
    group     => 'root',
    source    => 'puppet:///modules/collectd/icinga/check_icingastats',
    require   => File['collectd.exec.dir'],
    notify    => Service['collectd']
  }

  file { 'collectd.icinga.conf':
    ensure    => $collectd::plugin::icinga::ensure,
    path      => "${conf_dir}/icinga.conf",
    mode      => '0644',
    owner     => 'root',
    group     => 'root',
    content   => template('collectd/icinga.conf.erb'),
    notify    => Service['collectd']
  }

}
