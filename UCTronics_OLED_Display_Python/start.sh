#!/usr/bin/with-contenv bashio
set -e

CONFIG_PATH=/data/options.json

DISABLE_AUTO_START="$(bashio::config 'Stop_Auto_Run')"

bashio::log.info "Starting UCTronics LCD App..."
bashio::log.info "Disable Auto Start = ${DISABLE_AUTO_START}"


if [ "$DISABLE_AUTO_START" = false ]; then

    if ls /dev/i2c-1; then 
        bashio::log.info "Found i2c access!";
        bashio::log.info "Display Info to OLED"
		
        cd /UCTronics_OLED/
        python3 display.py
    else
        bashio::log.info "Attempting to set up i2c access!";
        exec run.sh
    fi 

else
    bashio::log.info "No Auto Run"
    sleep 99999;
fi