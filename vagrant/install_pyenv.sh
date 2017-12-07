#!/bin/zsh
# pyenv install for CentOS 6.5 x86_64

sudo yum install -y  gcc gcc-c++ make git patch openssl-devel zlib-devel readline-devel sqlite-devel bzip2-devel

git clone git://github.com/yyuu/pyenv.git ~/.pyenv

export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"

echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

pyenv install 2.7.6
pyenv versions

pyenv shell 2.7.6
pyenv global 2.7.6
pyenv versions
pyenv rehash