class collectd (
  $fqdnlookup   = true,
  $interval     = 10,
  $threads      = 5,
  $timeout      = 2,
  $purge        = undef,
  $recurse      = undef,
  $purge_config = false,
  $listen       = 'UNSET',
  $server       = 'UNSET',
  $manage_package = true) {
  include collectd::params

  $plugin_conf_dir = $collectd::params::plugin_conf_dir
  $require_package = $manage_package ? {
    true  => Package['collectd'],
    false => undef,
  }

  if $manage_package {
    package { 'collectd':
      ensure   => installed,
      name     => $collectd::params::package,
      provider => $collectd::params::provider,
      before   => File['collectd.conf', 'collectd.d'],
    }
  }

  file { 'collectd.d':
    ensure  => directory,
    path    => $collectd::params::plugin_conf_dir,
    mode    => '0644',
    owner   => 'root',
    group   => 'root',
    purge   => $purge,
    recurse => $recurse,
  }

  $conf_content = $purge_config ? {
    true    => template('collectd/collectd.conf.erb'),
    default => undef,
  }

  file { 'collectd.conf':
    path    => $collectd::params::config_file,
    content => $conf_content,
    notify  => Service['collectd'],
  }

  if $purge_config != true {
    # Include conf_d directory
    file_line { 'include_conf_d':
      line   => "Include \"${collectd::params::plugin_conf_dir}/\"",
      path   => $collectd::params::config_file,
      notify => Service['collectd'],
    }
  }

  if $listen != 'UNSET' or $server != 'UNSET' {
    class { 'collectd::plugin::network':
      listen => $listen,
      server => $server;
    }
  }

  service { 'collectd':
    ensure  => running,
    name    => $collectd::params::service_name,
    enable  => true,
    require => $require_package,
  }
}
