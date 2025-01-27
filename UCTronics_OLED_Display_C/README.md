# UCTRONICS OLED Display

### NB This is my first HomeAssistant Add-on so use at own risk

Enables the OLED display for UCTRONICS Pi 5 Rack Module.

This addon will utilise code from Adam Outler, [GitHub adamoutler](https://github.com/adamoutler/HassOSConfigurator/tree/main/Pi4EnableI2C) to first enable the I2C interface, you will need to reboot twice as per his documentation. After I2C is enabled then the display will finally show.

Special thanks to [DC Walter](https://github.com/dcwalter) for fixing the code to support C unit for temperature, and also fixing CPU usage, and adding the HA Logo.

## Install Guide

### First Step
1. Install
1. Disable "Protection mode"
1. Start the addon, this will allow Adam's script to enable I2C interface.
1. Reboot Twice! 

### Second Step.
1. Re-enable "Protection mode"
1. Start the addon
1. Check the "Log" and see if there are any error.
1. Your OLED should be displaying.
