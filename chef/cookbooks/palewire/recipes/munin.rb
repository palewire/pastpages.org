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
  notifies :restart, resources(:service => "munin-node")
end
