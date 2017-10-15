directory "/var/log/celery/" do
    owner node[:app_user]
    group node[:app_group]
    mode 0775
end


directory "/var/run/celery/" do
    owner node[:app_user]
    group node[:app_group]
    mode 0775
end


directory "/etc/conf.d/" do
    owner node[:app_user]
    group node[:app_group]
    mode 0775
end


template "/etc/conf.d/celery" do
  source "celery/env"
  mode 0640
  owner "root"
  group "root"
  variables({
     :app_name => node[:app_name]
  })
end


template "/etc/systemd/system/celery.service" do
  source "celery/celery.service"
  mode 0640
  owner "root"
  group "root"
  variables({
     :app_name => node[:app_name],
     :app_user => node[:app_user],
     :app_group => node[:app_group]
  })
end


script "Reload systemd configuration" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    systemctl daemon-reload
  EOH
end


script "Restart celery" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    systemctl start celery
  EOH
end
