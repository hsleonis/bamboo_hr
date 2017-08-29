#!/bin/bash
if [ -L $0 ] ; then
    current_dir=$(dirname $(readlink -f $0)) ;
else
    current_dir=$(dirname $0) ;
fi ;

place_dir=~/
cd $place_dir

eval 'sudo rm requirements.txt'
eval 'sudo rm -R bamboo_hr'
eval 'sudo rm -R bamboohrvenv'
eval 'cp ${current_dir}/requirements.txt ${place_dir}'
eval 'cp -R ${current_dir}/bamboo_hr ${place_dir}'

virtualenv bamboohrvenv
source bamboohrvenv/bin/activate
eval 'pip install -r requirements.txt'

cd ./bamboo_hr
eval 'sudo rm -R tmp'
mkdir tmp

python manage.py migrate
python manage.py runserver

