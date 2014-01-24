#
# generate stuff for development of specializers
# currently only supported command is create
#

if test -z "$*"
then
    echo "Usage $0: create <specializer_name>"
fi

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# echo "Dir is $DIR"

if test "$1" = "create"
then
  if test -n "$2"
  then
    python $script_dir/asp_tools/generators/create.py $2
  else
    echo "Usage: $0 create <specializer_name>"
    exit 1
  fi
elif test "$1" = "platform"
then
  python $script_dir/asp/platform/list.py
fi

