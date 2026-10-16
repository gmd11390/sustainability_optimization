import sqlite3
import meraki
import config

# Meraki API key and initialization
API_KEY = config.API_KEY
dashboard = meraki.DashboardAPI(API_KEY) if API_KEY else None
org_id = config.ORG_ID
network_id = config.NETWORK_ID
serial_numbers = config.SERIAL_NUMBERS

def update_port_schedules(network_id, serial_numbers):
    try:
        # Get existing schedules
        schedules = dashboard.switch.getNetworkSwitchPortSchedules(network_id)
        sustainability_schedule_id = None
        for schedule in schedules:
            if schedule['name'] == "Sustainability":
                sustainability_schedule_id = schedule['id']
                break

        # Remove Sustainability schedule from ports 1-8 on each switch
        for serial in serial_numbers:
            ports = dashboard.switch.getDeviceSwitchPorts(serial)[:8]
            for port in ports:
                if 'ap' in port['tags'] and port.get('portScheduleId') == sustainability_schedule_id:
                    dashboard.switch.updateDeviceSwitchPort(serial, portId=port['portId'], portScheduleId=None)

        # Define new schedules for each zone
        new_schedules = {
            "zoneID_1 Sustainability": {
                "portSchedules": [{
                    "ports": [2, 3, 4],
                    "portSchedule": {
                        "enabled": True,
                        "schedules": {
                            "mon": [{"start": "12:00", "end": "20:00"}],
                            "tue": [{"start": "18:00", "end": "20:00"}],
                            "wed": [{"start": "18:00", "end": "20:00"}],
                            "thu": [{"start": "18:00", "end": "20:00"}],
                            "fri": [{"start": "18:00", "end": "20:00"}],
                            "sat": [{"start": "00:00", "end": "23:59"}],
                            "sun": [{"start": "00:00", "end": "23:59"}]
                        }
                    }
                }]
            },
            "zoneID_2 Sustainability": {
                "portSchedules": [{
                    "ports": [5, 6],
                    "portSchedule": {
                        "enabled": True,
                        "schedules": {
                            "mon": [{"start": "02:00", "end": "24:00"}],
                            "tue": [{"start": "02:00", "end": "24:00"}],
                            "wed": [{"start": "02:00", "end": "24:00"}],
                            "thu": [{"start": "02:00", "end": "24:00"}],
                            "fri": [{"start": "02:00", "end": "24:00"}],
                            "sat": [{"start": "00:00", "end": "04:00"}],
                            "sun": [{"start": "00:00", "end": "04:00"}]
                        }
                    }
                }]
            },
            "zoneID_3 Sustainability": {
                "portSchedules": [{
                    "ports": [2, 3, 4],
                    "portSchedule": {
                        "enabled": True,
                        "schedules": {
                            "mon": [{"start": "16:00", "end": "24:00"}],
                            "tue": [{"start": "16:00", "end": "24:00"}],
                            "wed": [{"start": "16:00", "end": "24:00"}],
                            "thu": [{"start": "16:00", "end": "24:00"}],
                            "fri": [{"start": "18:00", "end": "24:00"}],
                            "sat": [{"start": "00:00", "end": "04:00"}],
                            "sun": [{"start": "00:00", "end": "04:00"}]
                        }
                    }
                }]
            },
            "zoneID_4 Sustainability": {
                "portSchedules": [{
                    "ports": [5, 6],
                    "portSchedule": {
                        "enabled": True,
                        "schedules": {
                            "mon": [{"start": "16:00", "end": "24:00"}],
                            "tue": [{"start": "16:00", "end": "24:00"}],
                            "wed": [{"start": "14:00", "end": "24:00"}],
                            "thu": [{"start": "14:00", "end": "24:00"}],
                            "fri": [{"start": "18:00", "end": "24:00"}],
                            "sat": [{"start": "20:00", "end": "24:00"}],
                            "sun": [{"start": "20:00", "end": "24:00"}]
                        }
                    }
                }]
            }
        }

        # Create new schedules
        for schedule_name, schedule_body in new_schedules.items():
            response = dashboard.switch.createNetworkSwitchPortSchedule(network_id, name=schedule_name, portSchedule=schedule_body)
            new_schedule_id = response['id']

            # Apply the new schedule to the corresponding ports
            for serial in serial_numbers:
                ports = dashboard.switch.getDeviceSwitchPorts(serial)[:8]
                for port in ports:
                    if schedule_name.startswith(port['tags'][1]):
                        dashboard.switch.updateDeviceSwitchPort(serial, portId=port['portId'], portScheduleId=new_schedule_id)

        print("Schedules updated successfully.")
    except meraki.APIError as e:
        print(f"Error updating schedules: {e}")

if __name__ == "__main__":
    import os
    if os.getenv('ENABLE_LIVE_MERAKI') != 'true':
        raise SystemExit('Live changes disabled: set ENABLE_LIVE_MERAKI=true in an authorized lab')
    update_port_schedules(network_id, serial_numbers)