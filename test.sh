#!/usr/bin/env bash
set -e

pushd examples/airflow || exit
   ./generate.sh
popd || exit

pushd examples/gcp || exit
   ./generate.sh
popd || exit

pushd examples/yabai || exit
   ./generate.sh
popd || exit

pushd examples/github || exit
   ./generate.sh
popd || exit

pushd examples/json || exit
   ./generate.sh
popd || exit
