#!/bin/bash

wd=`pwd`
root_dir=`realpath "$wd/../"`

echo $wd
echo $root_dir

function benchmark_branch {
	cd $root_dir
	git checkout $1
	head=`git rev-parse --short HEAD`
	pip install .
	cd $wd
	taskset -c 0 python benchmark.py -o result-$1-$head.pkl
}

sleep 5
benchmark_branch $1
sleep 5
benchmark_branch $2

