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

script "Start Munin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    /etc/init.d/munin-node restart
  EOH
end
