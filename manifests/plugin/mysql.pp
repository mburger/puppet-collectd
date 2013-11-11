class collectd::plugin::mysql (
  $database = params_lookup('databases'),
  $host     = 'localhost',
  $username = 'collectd',
  $password = fqdn_rand(100000000000),
  $port     = '3306',
  $ensure   = present
) {
  include collectd::params

  $conf_dir = $collectd::params::plugin_conf_dir

  file { 'mysql.conf':
    ensure  => $collectd::plugin::mysql::ensure,
    path    => "${conf_dir}/mysql.conf",
    mode    => '0644',
    owner   => 'root',
    group   => 'root',
    content => template('collectd/mysql.conf.erb'),
    notify  => Service['collectd'],
  }

  ::mysql::grant { 'collectd':
    mysql_user      => $collectd::plugin::mysql::username,
    mysql_password  => $collectd::plugin::mysql::password,
    mysql_db        => '*',
    mysql_create_db => false,
  }
}
