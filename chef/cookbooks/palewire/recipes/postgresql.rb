include_recipe "postgresql::postgis"

postgresql_user node[:db_user] do
  password node[:db_password]
  privileges :superuser => true, :createdb => true, :inherit => true, :login => true
end

postgresql_database node[:db_name] do
  user node[:db_user]
  owner "postgres"
  languages [ "plpgsql" ]
  action :create
end


