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

script "Restart Munin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    echo "#nothing to see here" > /etc/munin/apache.conf
    service munin-node restart
    service apache2 restart
  EOH
end
