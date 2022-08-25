''' Current function definition being used in main API script '''
import json
import meraki
from prettytable import PrettyTable
from dateutil.parser import parse
from rich.console import Console


def iniciate_dashboard(api_key):
    dashboard = meraki.DashboardAPI(api_key, log_path="logs", suppress_logging=True)
    return dashboard

def get_licensing(api_key,org_id):
    '''
    This module will retrieve all the licensing details
    '''
    response = {}
    response.update(status= "N/A")
    response.update(expirationDate= "N/A")
    response.update(licensedDeviceCounts= "N/A")
    dashboard = meraki.DashboardAPI(api_key, log_path='logs', suppress_logging=True)
    organization_id = org_id
    try:
        response = dashboard.organizations.getOrganizationLicensesOverview(organization_id)
    except:
        pass
    return response

def lic_date(date):
    '''
    This funtion will replace date to numbers.
    Licensing date is not sortable from API source.
    '''
    if date != "N/A":
        date_formatted = parse(date.replace(" UTC", "")).strftime('%Y-%m-%d')
        return date_formatted
    else:
        return date

def table_svg(table, filename):
    '''
    This funtion will replace date to numbers.
    Licensing date is not sortable from API source.
    '''
    console = Console(record=True)
    console.print(table, justify="center")
    console.save_svg(f"outputs/{filename}.svg", title=filename)

def progress_bar(progress, total):
    '''
    Progress bars are needed when API calls are required or while building output files
    '''
    percent = 100 * (progress / total)
    prog_bar = '#' * int(percent) + '-' *(100 - int(percent))
    if percent == 100:
        print(f"\r|{prog_bar}| {percent:.2f}%", end="\n\n")
    else:
        print(f"\r|{prog_bar}| {percent:.2f}%", end="\r")

def get_orgid_outputs(dashboard, org_id):
    '''
    Creation of multiple files for a particular OrgID
    '''
    try:
        device_list = dashboard.organizations.getOrganizationDevicesAvailabilities(org_id, total_pages='all')
        # TODO: Get device status and sort by: Appliances, switches, APs and others
        ### CLI pretty Table
        devicesTable = PrettyTable()
        devicesTable.field_names = ["Org ID",
                            "device type",
                            "device name",
                            "status"]
        devicesTable.align = "r"
        devicesTable.sortby = "device type"
        devicesTable.hrules = True
        # print placed for debuggin purposes issue#2
        print(type(device_list))
        try:
            print(json.loads(device_list))
        except:
            print(device_list)
        for device in device_list:
            if device['status'] == 'online':
                match device['productType']:
                    case 'appliance':
                        devicesTable.add_row([str(org_id), device['productType'], device['name'], device['status']])
                    case 'wireless':
                        devicesTable.add_row([str(org_id), device['productType'], device['name'], device['status']])
                    case 'switch':
                        devicesTable.add_row([str(org_id), device['productType'], device['name'], device['status']])
                    case default:
                        devicesTable.add_row([str(org_id), "others", device['name'], device['status']])
        # print(devicesTable)
        table_svg(devicesTable, "org_id_" + org_id + "_status")
        ### Gather original json file for investigation 
        # print(json.dumps(device_list[0], indent=4))

        # TODO: Create table which will be used for .md, SVG and markmap
    except:
        print(f'[ERROR]: Check Organization {org_id} API status or licensing status since there was an error retrieving data.\n')
