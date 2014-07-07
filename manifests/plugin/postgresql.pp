class collectd::plugin::postgresql (
  $databases = params_lookup('databases'),
  $username = 'collectd',
  $password = fqdn_rand(100000000000),
  $host = 'localhost',
  $port = '5432',
  $ensure = present
) {
  include collectd::params

  $conf_dir = $collectd::params::plugin_conf_dir

  file { 'collectd.postgresql.conf':
    ensure    => $collectd::plugin::postgresql::ensure,
    path      => "${conf_dir}/postgresql.conf",
    mode      => '0644',
    owner     => 'root',
    group     => 'root',
    content   => template('collectd/postgresql.conf.erb'),
    notify    => Service['collectd']
  }

  ::postgresql::hba { 'pg.hba.collectd':
    type      => 'host',
    database  => 'all',
    user      => $collectd::plugin::postgresql::username,
    address   => '127.0.0.1/32',
    method    => 'md5'
  }

  ::postgresql::role { $collectd::plugin::postgresql::username:
    login       => true,
    password    => $collectd::plugin::postgresql::password,
  }
}
