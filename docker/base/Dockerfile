FROM centos:7.4.1708

# Setup Chrome Repo
COPY google-chrome.repo /etc/yum.repos.d/google-chrome.repo

# back up mirrors before overwriting
RUN cp -r /etc/yum.repos.d /etc/yum.repos.d.orig

# prepare custom mirrors
COPY *.repo Dockerfile /etc/yum.repos.d/

# pip install python packages
COPY *requirements*.txt entrypoint.sh /
COPY pip.conf /etc/

# 1. install most packages from pypi and only then python-Fabric
# 2. google-chrome-stable is located is in very unstable repo and yum may fail on it
#    do manual download with retries and install it locally
RUN \
    yum repolist | grep epel || yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
    curl --retry 3 --retry-delay 10 https://bootstrap.pypa.io/2.7/get-pip.py | python2 - 'pip==20.1' && \
    yum install -y unzip vim tcpdump ant git ipmitool gcc python-devel \
      patch sshpass bzip2 wget sudo pexpect ant-junit libXpm libXrender \
      gtk2 nss GConf2 firefox openssl \
      python3 python3-devel && \
    url=$(yumdownloader --urls google-chrome-stable | grep "^http.*google-chrome-stable" | head -1) && \
    wget -nv -c --tries=10 -O google-chrome-stable.rpm $url && \
    yum install -y ./google-chrome-stable.rpm && \
    pip install -r /indirect_requirements.txt -r /requirements.txt && \
    pip3 install -r /indirect_requirements3.txt -r /requirements3.txt && \
    yum clean all -y && \
    rm -rf /var/cache/yum && \
    rm -rf /etc/yum.repos.d && \
    mv /etc/yum.repos.d.orig /etc/yum.repos.d && \
    wget -nv -c --tries=3 http://chromedriver.storage.googleapis.com/2.34/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && cp ./chromedriver /usr/bin/ && \
    chmod ugo+rx /usr/bin/chromedriver
