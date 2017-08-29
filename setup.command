#!/bin/bash
program_installed() {
	if which "$1" > /dev/null; then
		return 0
	else
		return 1
	fi
}

current_dir=$(pwd)
place_dir=~/

if program_installed "brew"; then 
	echo 'Brew is already installed.'
else
	eval '/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"'
	eval 'brew update'
fi


if program_installed "Python3.6"; then
	if program_installed "pip3.6"; then
		eval 'pip3.6 install virtualenv'
	fi
else
	eval 'cp ${current_dir}/python3.6.pkg ${place_dir}'
	eval 'pkgutil --expand "python3.6.pkg"'
	eval 'pip3.6 install virtualenv'
fi


