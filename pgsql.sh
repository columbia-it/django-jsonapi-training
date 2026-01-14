#!/bin/sh
# use a local postgresql server
export PGSQL_HOST=localhost
export PGSQL_DB=$USER
export PGSQL_USER=$USER
$*
