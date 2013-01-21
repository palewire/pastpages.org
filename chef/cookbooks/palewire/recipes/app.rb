directory "/apps/" do
    owner node[:app_user]
    group node[:app_group]
    mode 0775
end

virtualenv "/apps/#{node[:app_name]}" do
    owner node[:app_user]
    group node[:app_group]
    mode 0775
end

directory "/apps/#{node[:app_name]}/repo" do
    owner node[:app_user]
    group node[:app_group]
    mode 0775
end

git "/apps/#{node[:app_name]}/repo"  do
  repository node[:app_repo]
  reference "HEAD"
  branch node[:app_branch]
  user node[:app_user]
  group node[:app_group]
  action :sync
end

# Install the virtualenv requirements
script "Install Requirements" do
  interpreter "bash"
  user node[:apps_user]
  group node[:apps_group]
  code "/apps/#{node[:app_name]}/bin/pip install -r /apps/#{node[:app_name]}/repo/requirements.txt"
end

# Create the database user
script "Create database user" do
  interpreter "bash"
  user "postgres"
  code <<-EOH
     psql -c "CREATE USER #{node[:db_user]} WITH INHERIT SUPERUSER CREATEDB PASSWORD '#{node[:db_password]}'";
  EOH
  ignore_failure true
end

