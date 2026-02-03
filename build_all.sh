#!/bin/bash
#
# Builds cpip for distribution
# Ref: https://packaging.python.org/tutorials/packaging-projects/
#
# Other references:
# https://kvz.io/bash-best-practices.html
# https://bertvv.github.io/cheat-sheets/Bash.html

set -o errexit  # abort on nonzero exitstatus
set -o nounset  # abort on unbound variable
set -o pipefail # don't hide errors within pipes

PYTHON_VERSIONS=('3.9' '3.10' '3.11' '3.12' '3.13')
PYTHON_VENV_ROOT="${HOME}/pyenvs"
# Used for venvs
PROJECT_NAME="cpip"

#printf "%-8s %8s %10s %10s %12s\n" "Ext" "Files" "Lines" "Words" "Bytes"

deactivate_virtual_environment() {
  # https://stackoverflow.com/questions/42997258/virtualenv-activate-script-wont-run-in-bash-script-with-set-euo
  set +u
  if command -v deactivate &>/dev/null; then
    deactivate
  fi
  set -u
}

create_virtual_environments() {
  deactivate_virtual_environment
  for version in ${PYTHON_VERSIONS[*]}; do
    echo "---> Create virtual environment for Python version ${version}"
    venv_path="${PYTHON_VENV_ROOT}/${PROJECT_NAME}_${version}"
    if [ ! -d "${venv_path}" ]; then
      # Control will enter here if directory not exists.
      echo "---> Creating virtual environment at: ${venv_path}"
      "python${version}" -m venv "${venv_path}"
    fi
  done
}

remove_virtual_environments() {
  deactivate_virtual_environment
  for version in ${PYTHON_VERSIONS[*]}; do
    echo "---> For Python version ${version}"
    venv_path="${PYTHON_VENV_ROOT}/${PROJECT_NAME}_${version}"
    if [ -d "${venv_path}" ]; then
      # Control will enter here if directory exists.
      echo "---> Removing virtual environment at: ${venv_path}"
      #rm --recursive --force -- "${venv_path}"
      rm -rf -- "${venv_path}"
    fi
  done
}

run_demonstration_code_in_documentation_tree() {
  # This runs all the demo code in the documentation tree to check that it does not error.
  echo "---> run_demonstration_code_in_documentation_tree..."
  echo "---> cpip_00.py"
  python docs/doc_src/tutorial/demo/cpip_00.py docs/doc_src/tutorial/demo/proj/src/main.c
  echo "---> cpip_01.py"
  python docs/doc_src/tutorial/demo/cpip_01.py docs/doc_src/tutorial/demo/proj/src/main.c
  echo "---> cpip_02.py"
  python docs/doc_src/tutorial/demo/cpip_02.py docs/doc_src/tutorial/demo/proj/src/main.c
  echo "---> cpip_03.py"
  python docs/doc_src/tutorial/demo/cpip_03.py docs/doc_src/tutorial/demo/proj/src/main.c
  echo "---> cpip_04.py"
  python docs/doc_src/tutorial/demo/cpip_04.py docs/doc_src/tutorial/demo/proj/src/main.c
  echo "---> cpip_05.py"
  python docs/doc_src/tutorial/demo/cpip_05.py docs/doc_src/tutorial/demo/proj/src/main.c
  echo "---> cpip_06.py"
  python docs/doc_src/tutorial/demo/cpip_06.py docs/doc_src/tutorial/demo/proj/src/main.c
  echo "---> cpip_14.py"
  python docs/doc_src/tutorial/demo/cpip_14.py docs/doc_src/tutorial/demo/proj/src/main.c
  echo "---> cpip_15.py"
  python docs/doc_src/tutorial/demo/cpip_15.py docs/doc_src/tutorial/demo/proj/src/main.c
  echo "---> cpip_17.py"
  python docs/doc_src/tutorial/demo/cpip_17.py docs/doc_src/tutorial/demo/proj/src/main.c
  echo "---> cpip_18.py"
  python docs/doc_src/tutorial/demo/cpip_18.py docs/doc_src/tutorial/demo/proj/src/main.c
  echo "---> cpip_19.py"
  python docs/doc_src/tutorial/demo/cpip_19.py docs/doc_src/tutorial/demo/proj/src/main.c
  echo "---> cpip_30.py"
  python docs/doc_src/tutorial/demo/cpip_30.py docs/doc_src/tutorial/demo/proj/src/main.c
  echo "---> run_demonstration_code_in_documentation_tree DONE"
}

create_bdist_wheel() {
  echo "---> Creating bdist_wheel for all versions..."
  for version in ${PYTHON_VERSIONS[*]}; do
    echo "---> For Python version ${version}"
    deactivate_virtual_environment
    venv_path="${PYTHON_VENV_ROOT}/${PROJECT_NAME}_${version}"
    if [ ! -d "${venv_path}" ]; then
      # Control will enter here if directory doesn't exist.
      echo "---> Creating virtual environment at: ${venv_path}"
      "python${version}" -m venv "${venv_path}"
    fi
    # https://stackoverflow.com/questions/42997258/virtualenv-activate-script-wont-run-in-bash-script-with-set-euo
    set +u
    source "${venv_path}/bin/activate"
    set -u
    echo "---> Python version:"
    python -VV
    echo "---> Installing everything via pip:"
    pip install -U pip setuptools wheel
#    pip install -r requirements_dev.txt
    pip install -r requirements_min.txt
    echo "---> Result of pip install:"
    pip list
    echo "---> Running python setup.py develop:"
    MACOSX_DEPLOYMENT_TARGET=10.9 CC=clang CXX=clang++ python setup.py develop
    echo "---> Running tests:"
    # Fail fast with -x
    pytest -x tests
    echo "---> All tests pass for Python version ${version}"
    run_demonstration_code_in_documentation_tree
    echo "---> Running setup for bdist_wheel:"
    python setup.py bdist_wheel
  done
}

create_sdist() {
  echo "---> Running setup for sdist:"
  python setup.py sdist
}

report_all_versions_and_setups() {
  echo "---> Reporting all versions..."
  for version in ${PYTHON_VERSIONS[*]}; do
    echo "---> For Python version ${version}"
    deactivate_virtual_environment
    venv_path="${PYTHON_VENV_ROOT}/${PROJECT_NAME}_${version}"
    if [ ! -d "${venv_path}" ]; then
      # Control will enter here if directory doesn't exist.
      echo "---> Creating virtual environment at: ${venv_path}"
      "python${version}" -m venv "${venv_path}"
    fi
      echo "---> Virtual environment at: ${venv_path}"
    # https://stackoverflow.com/questions/42997258/virtualenv-activate-script-wont-run-in-bash-script-with-set-euo
    set +u
    source "${venv_path}/bin/activate"
    set -u
    echo "---> Python version:"
    python -VV
    echo "---> pip list:"
    pip list
  done
}

show_results_of_dist() {
  echo "---> dist/:"
  ls -l "dist"
  echo "---> twine check dist/*:"
  twine check dist/*
  # Test from Test PyPi
  # pip install -i https://test.pypi.org/simple/orderedstructs
  echo "---> Ready for upload to test PyPi:"
  echo "---> pip install twine"
  echo "---> twine upload --repository testpypi dist/*"
  echo "---> Or PyPi:"
  echo "---> twine upload dist/*"
}

echo "===> Removing build/ and dist/"
#rm --recursive --force -- "build" "dist"
rm -rf -- "build" "dist"
remove_virtual_environments
create_virtual_environments
create_bdist_wheel
create_sdist
report_all_versions_and_setups
pip install twine
show_results_of_dist
echo "===> All done"
