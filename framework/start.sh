#!/usr/bin/env bash
current_dir=$("pwd")
data_path=$current_dir/data/
echo $data_path
# export PYTHON#='/anaconda3/envs/py35/bin/python'   # not useful in linux ubuntu
/application/python3/bin/pyhton3 $current_dir/framework/Entry.py -d $data_path -m -1