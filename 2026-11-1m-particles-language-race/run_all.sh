#!/usr/bin/env bash
# Builds every version, prints the machine specs, then runs each one 3 times on 1,000,000 particles.
set -e
cd "$(dirname "$0")"
mkdir -p bin
g++ -O3 -march=native gravity.cpp -o bin/gravity_cpp
g++ -O3 -march=native -fopenmp gravity.cpp -o bin/gravity_cpp_mt
gcc -O3 -march=native gravity.c -o bin/gravity_c -lm
rustc -C opt-level=3 -C target-cpu=native gravity.rs -o bin/gravity_rs
go build -o bin/gravity_go gravity.go
javac -d bin Gravity.java

{
echo "== machine"
grep -m1 "model name" /proc/cpuinfo | sed 's/.*: //'
echo "cores: $(nproc)"
free -h | awk '/Mem:/{print "ram: "$2}'
grep PRETTY_NAME /etc/os-release | cut -d'"' -f2
echo "kernel: $(uname -r)"
echo "== toolchains"
python3 --version
python3 -c "import numpy; print('numpy', numpy.__version__)"
echo "node $(node --version)"
echo "bun $(bun --version)"
java -version 2>&1 | grep -E '^openjdk'
go version
rustc --version
g++ --version | head -1
gcc --version | head -1
} 2>&1 | grep -v Picked | tee results/specs.txt

N=${N:-1000000}
run() { for r in 1 2 3; do "$@" "$N" 2>&1 | grep -v Picked; done; }
{
run python3 gravity.py 3
run python3 gravity_numpy.py 30
run node gravity.js 50
run bun gravity.js 50
run java -cp bin Gravity 50
run bin/gravity_go 50
run bin/gravity_rs 50
run bin/gravity_c 50
run bin/gravity_cpp 50
run bin/gravity_cpp_mt 50
} | tee results/raw.txt
