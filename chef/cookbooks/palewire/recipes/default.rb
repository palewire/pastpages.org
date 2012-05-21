# Fix the locale
execute "create-locale" do
  command %Q{
    locale-gen en_US.UTF-8
  }
end

execute "set-locale" do
  command %Q{
    update-locale LANG=en_US.UTF-8
  }
end

script "Add to hosts file" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    echo '127.0.0.1    pastpages-anderson' >> /etc/hosts
  EOH
end

# Load any base system wide packages
node[:base_packages].each do |pkg|
    package pkg do
        :upgrade
    end
end

# Loop through the user list, create the user, load the authorized_keys
# and mint a bash_profile
node[:users].each_pair do |username, info|
    group username do
       gid info[:id] 
    end

    user username do 
        comment info[:full_name]
        uid info[:id]
        gid info[:id]
        shell info[:disabled] ? "/sbin/nologin" : "/bin/bash"
        supports :manage_home => true
        home "/home/#{username}"
    end

    directory "/home/#{username}/.ssh" do
        owner username
        group username
        mode 0700
    end

    cookbook_file "/home/#{username}/.ssh/authorized_keys" do
      source "authorized_keys"
      mode 0640
      owner username
      group username
    end

    cookbook_file "/home/#{username}/.ssh/known_hosts" do
      source "known_hosts"
      mode 0640
      owner username
      group username
    end

    cookbook_file "/home/" + username + "/.ssh/id_rsa" do
      source "id_rsa"
      mode 0600
      owner username
      group username
    end

    cookbook_file "/home/" + username + "/.ssh/id_rsa.pub" do
      source "id_rsa.pub"
      mode 0644
      owner node[:apps_user]
      group node[:apps_group]
    end

    cookbook_file "/home/#{username}/.bash_profile" do
        source "bash_profile"
        owner username
        group username
        mode 0755
    end

end

# Set the user groups
node[:groups].each_pair do |name, info|
    group name do
        gid info[:gid]
        members info[:members]
    end
end

# Load the authorized keys for the root user
directory "/root/.ssh" do
    owner "root"
    group "root"
    mode 0700
end

cookbook_file "/root/.ssh/authorized_keys" do
  source "authorized_keys"
  mode 0640
  owner "root"
  group "root"
end


