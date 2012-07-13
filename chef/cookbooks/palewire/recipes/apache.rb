package "apache2" do
    :upgrade
end

package "libapache2-mod-wsgi" do
    :upgrade
end

service "apache2" do
  enabled true
  running true
  supports :status => true, :restart => true, :start => true, :stop => true
  action [:restart,]
end

cookbook_file "/etc/apache2/sites-enabled/" + node[:app_name] do
  source "apache/" + node[:app_name] 
  mode 0640
  owner "root"
  group "root"
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
  code "rm /etc/apache2/sites-enabled/000-default"
  ignore_failure true
end

