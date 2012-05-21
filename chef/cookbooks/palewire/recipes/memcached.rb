package "memcached" do
    :upgrade
end

service "memcached" do
  enabled true
  running true
  supports :status => true, :restart => true
  action [:enable, :start]
end

cookbook_file "/etc/memcached.conf" do
  source "memcached.conf"
  mode 0640
  owner "root"
  group "root"
  notifies :restart, resources(:service => "memcached")
end

script "Start memcached" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    /usr/bin/memcached -d -l 127.0.0.1 -p 11211 -u nobody -m 512 -c 1250 -P /var/run/memcached/memcached.pid
  EOH
end


