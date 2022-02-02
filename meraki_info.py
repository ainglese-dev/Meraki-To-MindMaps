
import meraki

def get_licensing(API_KEY,org_id):
    response = {}
    response.update(status= "N/A")
    response.update(expirationDate= "N/A")
    response.update(licensedDeviceCounts= "N/A")
    dashboard = meraki.DashboardAPI(API_KEY, log_path='logs_meraki/', suppress_logging=True)
    organization_id = org_id
    try:
        response = dashboard.organizations.getOrganizationLicensesOverview(organization_id)
    except meraki.APIError as e:
        pass
    except Exception as e:
        pass
    return response