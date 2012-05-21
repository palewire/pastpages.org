script "Install Selenium" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    mkdir /usr/lib/selenium/
    cd /usr/lib/selenium/
    wget http://selenium.googlecode.com/files/selenium-server-standalone-2.21.0.jar
    mkdir -p /var/log/selenium/
    chmod a+w /var/log/selenium/
  EOH
end

cookbook_file "/etc/init.d/selenium" do
  source "selenium"
  mode "777"
  owner "root"
  group "root"
end

script "Start Selenium" do
  interpreter "bash"
  user "root"
  group "root"
  code <<-EOH
    /etc/init.d/selenium start
    update-rc.d selenium defaults
  EOH
end
