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

script "Install python-munin" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    pip install git+https://github.com/samuel/python-munin.git
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
