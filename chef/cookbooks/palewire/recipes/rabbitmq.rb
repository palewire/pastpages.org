include_recipe "rabbitmq::default"

rabbitmq_user "guest" do
  action :delete
end

rabbitmq_user node[:app_user] do
  password node[:rabbitmq_password]
  action :add
end

rabbitmq_vhost "/" + node[:app_user] do
  action :add
end

rabbitmq_user node[:app_user] do
  vhost "/" + node[:app_user]
  permissions "\".*\" \".*\" \".*\""
  action :set_permissions
end

cookbook_file "/etc/init.d/celeryd" do
  source "celeryd"
  mode "777"
  owner "root"
  group "root"
end
