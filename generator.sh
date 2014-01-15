#
#
#

if test -z "$*"
then
    echo "Usage $0:"
fi

if test "$1" = "create"
then
  if test -n "$2"
  then
    python generators/create.py $2
  else
    echo "Usage: $0 create <specializer_name>"
    exit 1
  fi
fi