
import meraki
from dateutil.parser import parse
from rich.console import Console
from rich.table import Table
import os
import webbrowser

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

def table_svg(table):
    '''
    This funtion will replace date to numbers.
    Licensing date is not sortable from API source.
    '''
    console = Console(record=True)
    console.print(table, justify="center")
    console.save_svg("outputs/table.svg", title="save_table_svg.py")
   # webbrowser.open(f"file://{os.path.abspath('table.svg')}")

