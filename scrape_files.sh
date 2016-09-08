#!/bin/bash
UPDATE_SERVER_ROOT=/usr/share/plugin_repository
#sudo chown www-data:www-data -R ${UPDATE_SERVER_ROOT}
#sudo chmod g+rwX -R ${UPDATE_SERVER_ROOT}

cd ${UPDATE_SERVER_ROOT}
DJANGO_SETTINGS_MODULE=settings python application/scripts/scrape_app_dir.py
DJANGO_SETTINGS_MODULE=settings python plugins/scripts/scrape_plugins_dir.py directory plugin_data
