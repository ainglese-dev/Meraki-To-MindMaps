
import meraki

def get_licensing(local_API_KEY,org_id):
    '''
    This module will retrieve all the licensing details
    '''
    response = {}
    response.update(status= "N/A")
    response.update(expirationDate= "N/A")
    response.update(licensedDeviceCounts= "N/A")
    dashboard = meraki.DashboardAPI(local_API_KEY, log_path='logs_meraki/', suppress_logging=True)
    organization_id = org_id
    try:
        response = dashboard.organizations.getOrganizationLicensesOverview(organization_id)
    except:
        pass
    return response
    