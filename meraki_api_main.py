import os
import meraki
import json
from dotenv import load_dotenv
from prettytable import PrettyTable
from meraki_info import get_licensing
from dateutil.parser import parse
from mdutils.mdutils import MdUtils

def lic_date(date):
    if date != "N/A":
        date_formatted = parse(date.replace(" UTC", "")).strftime('%Y-%m-%d')
        return date_formatted
    else:
        return date      

# Defining your API key as a variable in source code is not recommended, define a regular.env file to load variables
load_dotenv()
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    API_KEY = '6bec40cf957de430a6f1f2baa056b99a4fac9ea0'  ### Meraki Always-On API KEY by default
    print("    >>> WARN: Using default Meraki Always-On API KEY\n\n")
# Instead, use an environment variable as shown under the Usage section
# @ https://github.com/meraki/dashboard-api-python/

dashboard = meraki.DashboardAPI(API_KEY, log_path='logs_meraki/', suppress_logging=True)
response = dashboard.organizations.getOrganizations()

### MD File creation from json to md
mdFile = MdUtils(file_name='meraki_licensing.md')
mdFile.new_header(level=1, title="Meraki Licensing Details")

### CLI pretty Table
pTable = PrettyTable()
pTable.field_names = ["Org ID", "Client Name", "Licensing Status", "Expiration date", "licensed Devices"]
for company in response:
    licensing = get_licensing(API_KEY,company["id"])
    equipments = json.dumps(licensing["licensedDeviceCounts"]).replace(",", "\n").replace("{", "").replace("}", "")
    pTable.add_row([company["id"], company["name"], licensing["status"], lic_date(licensing["expirationDate"]), equipments])
    company_title = f"[{company['name']}]({company['url']})"
    mdFile.new_header(level=2, title=company_title)
    mdFile.new_line("- Expiration Date: " + lic_date(licensing["expirationDate"]))
    mdFile.new_header(level=3, title="Allowed Devices")
    if licensing["licensedDeviceCounts"] != "N/A":
        for device, count in licensing["licensedDeviceCounts"].items():
            title = device + ": " + str(count)
            mdFile.new_header(level=4, title=title)
    else:
        mdFile.new_header(level=4, title=licensing["licensedDeviceCounts"])
pTable.align = "r"
pTable.sortby = "Expiration date"
pTable.hrules = True
print(pTable)

mdFile.create_md_file()