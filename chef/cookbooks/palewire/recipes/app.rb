directory "/apps/" do
    owner node[:app_user]
    group node[:app_group]
    mode 0775
end

virtualenv "/apps/" + node[:app_name] do
    owner node[:app_user]
    group node[:app_group]
    mode 0775
end

directory "/apps/" + node[:app_name] + "/repo" do
    owner node[:app_user]
    group node[:app_group]
    mode 0775
end

git "/apps/" + node[:app_name] + "/repo"  do
  repository node[:app_repo]
  reference "HEAD"
  user node[:app_user]
  group node[:app_group]
  action :sync
end

script "Install Requirements" do
  interpreter "bash"
  user node[:app_user]
  group node[:app_group]
  code "/apps/" + node[:app_name] + "/bin/pip install -r /apps/" + node[:app_name] + "/repo/requirements.txt"
end


