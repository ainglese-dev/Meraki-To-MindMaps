'''
Main script to gather organizations and their corresponding devices and
licencing status associated with expiration date
'''
import os
import json
import logging
import sys
import time
import meraki
from dotenv import load_dotenv
from prettytable import PrettyTable
from mdutils.mdutils import MdUtils
from meraki_functions import get_licensing, lic_date, table_svg, progress_bar

# defining logging system

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s\n",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
# Defining your API key as a variable in source code is not recommended,
# define a regular.env file to load variables

logging.info('Loading API_KEY to system.')
load_dotenv()
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    API_KEY = '6bec40cf957de430a6f1f2baa056b99a4fac9ea0'  ### Meraki Always-On API KEY by default
    logging.warning("Using default Meraki Always-On API KEY, create .env file for private key.")
# Instead, use an environment variable as shown under the Usage section
# @ https://github.com/meraki/dashboard-api-python/

# Defining connectivity to Meraki (suppress logging since it works, Duh!)

dashboard = meraki.DashboardAPI(API_KEY, log_path="logs", suppress_logging=True)

# Gathering Org information list
logging.info('Gathering Organizations from Meraki via API')
response = dashboard.organizations.getOrganizations()
### MD File creation
logging.info('Initializing md file under outputs folder')
mdFile = MdUtils(file_name='outputs/meraki_licensing.md')
mdFile.new_header(level=1, title="Meraki Licensing Details")

### CLI pretty Table
pTable = PrettyTable()
pTable.field_names = ["Org ID",
                    "Client Name",
                    "Licensing Status",
                    "Expiration date",
                    "licensed Devices"]

# Adapting each Org per row
total_progress = len(response)
logging.info(f'Collecting licensing via API per {total_progress} company(ies)')

for company in response:
    licensing = get_licensing(API_KEY,company["id"])
    equipments = json.dumps(licensing["licensedDeviceCounts"]).replace(",", "\n").replace("{", "").replace("}", "")
    pTable.add_row([company["id"],
                    company["name"],
                    licensing["status"],
                    lic_date(licensing["expirationDate"]),
                    equipments])
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
    time.sleep(1)
    progress_bar(response.index(company), total_progress -1)

# Structure the current Org table

pTable.align = "r"
pTable.sortby = "Expiration date"
pTable.hrules = True

# Providing SVG file in the outputs folder
logging.info('Creating SVG file from collected data')
table_svg(pTable)

# Providing markdown file in the outputs folder
logging.info('Creating md file from collected data')
mdFile.create_md_file()

# Providing html markmap file in the outputs folder
logging.info('Creating Markmap file from md file')
os.system(f'markmap --no-open outputs/meraki_licensing.md --output outputs/licensing_MindMap.html')

desired_OrgID = input(" >>>> Please, select desired Org ID to create SVG and markmap from table above: ")
print('\n')
logging.info(f'Creating .md , SVG and markmap file for requested Org ID: {desired_OrgID}.')
# Getting output files for specific OrgID
get_orgid_outputs(desired_OrgID)
