package "munin" do
    :upgrade
end

package "munin-node" do
    :upgrade
end

package "munin-plugins-extra" do
    :upgrade
end

cookbook_file "/etc/munin/munin.conf" do
  source "munin.conf"
  mode "777"
  owner "root"
  group "root"
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

script "Install pgstats for PyMunin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    pip install psycopg2 --use-mirrors
    echo "[pgstats]
    user #{node[:db_user]}
    env.database #{node[:db_name]}
    env.include_db #{node[:db_name]}" > /etc/munin/plugin-conf.d/pgstats
    ln -s /usr/share/munin/plugins/pgstats /etc/munin/plugins/pgstats
  EOH
end

script "Install memcachedstats for PyMunin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    ln -s /usr/share/munin/plugins/memcachedstats /etc/munin/plugins/memcachedstats
  EOH
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

script "Restart Munin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    service munin-node restart
    service apache2 restart
  EOH
end
