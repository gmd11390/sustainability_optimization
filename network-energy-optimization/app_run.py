import sqlite3
import os
from pathlib import Path
import random
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
import meraki
import config
import pandas as pd

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'local-development-only')

# Meraki API key and initialization
API_KEY = config.API_KEY
dashboard = meraki.DashboardAPI(API_KEY) if API_KEY else None
org_id = config.ORG_ID

def write_config(network_id, serial_numbers):
    """Save runtime selection outside version-controlled source code."""
    import json
    Path('runtime_state.json').write_text(json.dumps({'network_id': network_id, 'serial_numbers': serial_numbers}))


@app.before_request
def guard_live_operations():
    from flask import abort
    if request.method != 'GET' and os.getenv('ENABLE_LIVE_MERAKI') != 'true':
        abort(403, description='Live network changes are disabled by default. Set ENABLE_LIVE_MERAKI=true only in an authorized lab.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_network', methods=['POST'])
def create_network():
    network_name = request.form['network_name']
    network_location = request.form['network_location']
    serial_numbers = request.form['serial_numbers'].replace('\r', '').split('\n')

    try:
        # Create the network
        response = dashboard.organizations.createOrganizationNetwork(
            org_id, network_name, productTypes=["appliance", "switch", "wireless"], tags=[network_location]
        )
        network_id = response['id']

        # Claim devices into the network
        response = dashboard.networks.claimNetworkDevices(
            network_id, serials=serial_numbers
        )

        # Update config with the new network ID and serial numbers
        write_config(network_id, serial_numbers)

        # Redirect to confirmation page with network_id
        return redirect(url_for('confirmation', network_id=network_id))
    except meraki.APIError as e:
        error_message = f"Error creating network: {e}"
        app.logger.error(error_message)
        flash(error_message)
        return redirect(url_for('index'))

@app.route('/confirmation/<network_id>')
def confirmation(network_id):
    try:
        devices = dashboard.networks.getNetworkDevices(network_id)
        if devices:
            device_serial = devices[0]['serial']
            dashboard_url = f"https://n109.meraki.com/o/{org_id}/manage/nodes/{device_serial}"
        else:
            dashboard_url = "#"
    except Exception as e:
        app.logger.error(f"Error fetching devices: {e}")
        dashboard_url = "#"
    return render_template('confirmation.html', network_id=network_id, dashboard_url=dashboard_url)

def rename_ports_and_apply_schedule(network_id, serial_numbers):
    for index, serial in enumerate(serial_numbers):
        floor_number = f"{index + 1}FL"
        try:
            # Rename the switch
            dashboard.devices.updateDevice(serial, name=f"{floor_number} Switch")

            # Get the list of ports
            ports = dashboard.switch.getDeviceSwitchPorts(serial)

            # Only process the first 8 ports
            ports = ports[:8]

            # Create port schedule if it doesn't exist
            schedules = dashboard.switch.getNetworkSwitchPortSchedules(network_id)
            schedule_id = None
            for schedule in schedules:
                if schedule['name'] == "Sustainability":
                    schedule_id = schedule['id']
                    break

            if not schedule_id:
                response = dashboard.switch.createNetworkSwitchPortSchedule(
                    network_id, name="Sustainability", portSchedule={
                        "portSchedules": [{
                            "ports": [2, 3, 4, 5, 6],
                            "portSchedule": {
                                "enabled": True,
                                "schedules": {
                                    "mon": [{"start": "00:00", "end": "04:00"}],
                                    "tue": [{"start": "00:00", "end": "04:00"}],
                                    "wed": [{"start": "00:00", "end": "04:00"}],
                                    "thu": [{"start": "00:00", "end": "04:00"}],
                                    "fri": [{"start": "00:00", "end": "04:00"}],
                                    "sat": [{"start": "00:00", "end": "24:00"}],
                                    "sun": [{"start": "00:00", "end": "24:00"}]
                                }
                            }
                        }]
                    }
                )
                schedule_id = response['id']

            # Rename the ports and apply tags
            for port in ports:
                port_id = int(port['portId'])  # Ensure portId is treated as an integer
                port_update = {
                    "portId": port_id,
                    "enabled": True,
                    "poeEnabled": True,
                }
                if port_id == 1:
                    port_update["name"] = "uplink"
                elif 2 <= port_id <= 4:
                    port_update["name"] = f"{floor_number}-AP{port_id-1}"
                    port_update["tags"] = ["ap", f"zoneID_{(index * 2) + 1}"]
                    port_update["portScheduleId"] = schedule_id
                elif 5 <= port_id <= 6:
                    port_update["name"] = f"{floor_number}-AP{port_id-1}"
                    port_update["tags"] = ["ap", f"zoneID_{(index * 2) + 2}"]
                    port_update["portScheduleId"] = schedule_id

                dashboard.switch.updateDeviceSwitchPort(serial, **port_update)
                app.logger.info(f"Updated port {port_id} on {serial} with settings: {port_update}")

        except meraki.APIError as e:
            app.logger.error(f"Error renaming ports and applying tags: {e}")

@app.route('/optimize', methods=['POST'])
def optimize():
    network_id = request.form['network_id']
    # Retrieve the serial numbers of the devices in the network
    devices = dashboard.networks.getNetworkDevices(network_id)
    serial_numbers = [device['serial'] for device in devices]

    # Call optimization functions here
    rename_ports_and_apply_schedule(network_id, serial_numbers)

    return redirect(url_for('optimization_complete', network_id=network_id))

@app.route('/optimization_complete/<network_id>')
def optimization_complete(network_id):
    try:
        devices = dashboard.networks.getNetworkDevices(network_id)
        if devices:
            device_serial = devices[0]['serial']
            dashboard_url = f"https://n109.meraki.com/o/{org_id}/manage/nodes/{device_serial}"
        else:
            dashboard_url = "#"
    except Exception as e:
        app.logger.error(f"Error fetching devices: {e}")
        dashboard_url = "#"
    return render_template('optimization_complete.html', network_id=network_id, dashboard_url=dashboard_url)
    
@app.route('/reset', methods=['POST'])
def reset_network():
    network_id = request.form['network_id']
    try:
        # Get list of devices in the network
        devices = dashboard.networks.getNetworkDevices(network_id)
        serial_numbers = [device['serial'] for device in devices]

        # Remove devices from network
        for serial in serial_numbers:
            dashboard.networks.removeNetworkDevices(network_id, serial)

        # Delete the network
        response = dashboard.networks.deleteNetwork(network_id)

        flash('Network has been reset and deleted successfully.')
    except Exception as e:
        app.logger.error(f"Error resetting network: {e}")
        flash('There was an error resetting the network. Please check the logs for more details.')

    return redirect(url_for('index'))

@app.route('/motion_alert', methods=['POST'])
def motion_alert():
    data = request.get_json()
    network_id = data['networkId']
    zones = data['zones']
    
    conn = sqlite3.connect('databases/network_data.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    for zone in zones:
        zone_id = zone['zoneId']
        motion = zone['motion']

        cursor.execute("INSERT INTO motion_events (network_id, zone_id, motion, timestamp) VALUES (?, ?, ?, ?)",
                       (network_id, zone_id, motion, datetime.datetime.now()))
        conn.commit()

        if motion == 1:  # Only update ports for zones with motion detected
            devices = dashboard.networks.getNetworkDevices(network_id)
            for device in devices:
                ports = dashboard.switch.getDeviceSwitchPorts(device['serial'])
                for port in ports[:8]:
                    if f"zoneID_{zone_id}" in port['tags']:
                        dashboard.switch.updateDeviceSwitchPort(
                            device['serial'], port['portId'],
                            portScheduleId=None  # Remove existing schedule
                        )

    conn.close()
    return "Motion alert processed", 200

if __name__ == "__main__":
    app.run(debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')