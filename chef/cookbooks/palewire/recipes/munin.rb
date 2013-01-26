package "munin" do
    :upgrade
end

package "munin-node" do
    :upgrade
end

package "munin-plugins-extra" do
    :upgrade
end

# Do the basic config for the node
template "/etc/munin/munin.conf" do
  source "munin/munin.conf.erb"
  mode "777"
  owner "root"
  group "root"
  variables({
     :name => node[:munin_name]
  })
end

script "Zero out munin apache.conf" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    echo "#nothing to see here" > /etc/munin/apache.conf
  EOH
end

script "Install PyMunin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    pip install PyMunin --use-mirrors
  EOH
end

# A postgresql plugin, first the conf...
template "/etc/munin/plugin-conf.d/pgstats" do
  source "munin/pgstats.erb"
  owner "root"
  group "root"
  variables({
     :munin_db_user => node[:db_user],
     :munin_db_name => node[:db_name],
     :munin_include_db_list => node[:db_name]
  })
end

# A postgresql plugin
script "Install postgresql adaptor for python" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    pip install psycopg2 --use-mirrors;
  EOH
end

script "Install pgstats for PyMunin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    ln -s /usr/share/munin/plugins/pgstats /etc/munin/plugins/pgstats
  EOH
  not_if do
    File.exists?("/etc/munin/plugins/pgstats")
  end
end

# A memcached plugin
script "Install memcachedstats for PyMunin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    ln -s /usr/share/munin/plugins/memcachedstats /etc/munin/plugins/memcachedstats
  EOH
  not_if do
    File.exists?("/etc/munin/plugins/memcachedstats")
  end
end

cookbook_file "/usr/share/munin/plugins/rackspacestats.py" do
  source "rackspacestats.py"
  mode "777"
  owner "root"
  group "root"
end

cookbook_file "/usr/share/munin/plugins/rackspaceinfo.py" do
  source "rackspaceinfo.py"
  mode "777"
  owner "root"
  group "root"
end

script "Install rackspacestats for PyMunin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    echo "[rackspacestats]
    env.username #{node[:rackspace_user]}
    env.api_key #{node[:rackspace_apikey]}
    env.container #{node[:rackspace_container]}" > /etc/munin/plugin-conf.d/rackspacestats
    ln -s /usr/share/munin/plugins/rackspacestats.py /etc/munin/plugins/rackspacestats
    chmod 0755 /etc/munin/plugins/rackspacestats
  EOH
end

# Varnish plugin
script "Install varnishstats for PyMunin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    ln -s /usr/share/munin/plugins/varnishstats /etc/munin/plugins/varnishstats
  EOH
  not_if do
    File.exists?("/etc/munin/plugins/varnishstats")
  end
end

script "Restart Munin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    service munin-node restart
    service apache2 restart
  EOH
end
