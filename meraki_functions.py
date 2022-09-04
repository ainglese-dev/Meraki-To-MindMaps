''' Current function definition being used in main API script '''
import meraki
from prettytable import PrettyTable
from dateutil.parser import parse
from rich.console import Console


def iniciate_dashboard(api_key):
    """
    Function to initiate dashboard session
    """
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
    except: # pylint: disable=bare-except
        print(f'\n >> ERROR: Error getting data via API for OrgID: {organization_id}.\n')
    return response

def lic_date(date):
    '''
    This funtion will replace date to numbers.
    Licensing date is not sortable from API source.
    '''
    if date != "N/A":
        date_formatted = parse(date.replace(" UTC", "")).strftime('%Y-%m-%d')
        return date_formatted
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
        device_list = dashboard.organizations.getOrganizationDevicesAvailabilities(org_id,\
             total_pages='all')
        ### CLI pretty Table
        dev_table = PrettyTable()
        dev_table.field_names = ["Org ID",
                            "device type",
                            "device name",
                            "status"]
        dev_table.align = "r"
        dev_table.sortby = "device type"
        dev_table.hrules = True
        for device in device_list:
            if device['status'] == 'online':
                match device['productType']:
                    case 'appliance':
                        dev_table.add_row([str(org_id), device['productType'], \
                            device['name'], device['status']])
                    case 'wireless':
                        dev_table.add_row([str(org_id), device['productType'], \
                            device['name'], device['status']])
                    case 'switch':
                        dev_table.add_row([str(org_id), device['productType'], \
                            device['name'], device['status']])
                    case _:
                        dev_table.add_row([str(org_id), "others", device['name'],\
                             device['status']])
        # print(dev_table)
        table_svg(dev_table, "org_id_" + org_id + "_status")
        ### Gather original json file for investigation
        # print(json.dumps(device_list[0], indent=4))

    except: # pylint: disable=bare-except
        print(f'[ERROR]: Check Organization {org_id} API status or \
            licensing status since there was an error retrieving data.\n')
