# Install apache
package "apache2" do
    :upgrade
end

# Install mod-wsgi so apache can talk to Django
package "libapache2-mod-wsgi" do
    :upgrade
end

# Restart apache
service "apache2" do
  enabled true
  running true
  supports :status => true, :restart => true, :start => true, :stop => true
  action [:restart,]
end

# Set the port for Apache since Varnish will be on :80
template "/etc/apache2/ports.conf" do
  source "apache/ports.conf.erb"
  mode 0640
  owner "root"
  group "root"
  variables({
     :apache_port => node[:apache_port]
  })
  notifies :restart, resources(:service => "apache2")
end

# Set a virtual host file
template "/etc/apache2/sites-enabled/#{node[:app_name]}" do
  source "apache/vhost.erb"
  mode 0640
  owner "root"
  group "root"
  variables({
     :apache_port => node[:apache_port],
     :server_name => node[:apache_server_name],
     :app_name => node[:app_name],
     :app_user => node[:app_user]
  })
  notifies :restart, resources(:service => "apache2")
end

cookbook_file "/etc/apache2/apache2.conf" do
  source "apache/apache2.conf"
  mode 0640
  owner "root"
  group "root"
  notifies :restart, resources(:service => "apache2")
end

bash "Remove default apache config" do
  user "root"
  group "root"
  code "rm /etc/apache2/sites-enabled/000-default.conf"
  ignore_failure true
end
