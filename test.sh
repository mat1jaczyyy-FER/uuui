#!/bin/bash

if uname -o | grep -q "Msys"; then
	python3="py"
else
	python3="python3"
fi

rm -rf autograder/solutions/*
mkdir autograder/solutions/0036524568
zip -r autograder/solutions/0036524568/0036524568.zip $1

(cd autograder; $python3 autograder.py ${1//py/})
code autograder/solutions/0036524568/autograder.log
