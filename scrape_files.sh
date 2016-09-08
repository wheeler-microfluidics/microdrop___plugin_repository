#!/bin/bash

# Resolve parent directory of script.  See [here][1].
#
# [1]: http://stackoverflow.com/questions/59895/can-a-bash-script-tell-which-directory-it-is-stored-in#246128
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
PARENT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

UPDATE_SERVER_ROOT=${PARENT_DIR}

cd ${UPDATE_SERVER_ROOT}
echo "[$(date)] Scraping apps: ${UPDATE_SERVER_ROOT}/app_data..."
DJANGO_SETTINGS_MODULE=settings python application/scripts/scrape_app_dir.py
echo "[$(date)] DONE"
echo "[$(date)] Scraping plugins: ${UPDATE_SERVER_ROOT}/plugin_data..."
DJANGO_SETTINGS_MODULE=settings python plugins/scripts/scrape_plugins_dir.py directory plugin_data
echo "[$(date)] DONE"
