'''
Main script to gather organizations and their corresponding devices and
licencing status associated with expiration date
'''
import os
import json
import logging
import sys
import time
from dotenv import load_dotenv
from prettytable import PrettyTable
from mdutils.mdutils import MdUtils
from meraki_functions import lic_date, table_svg, progress_bar, get_orgid_outputs
from meraki_functions import iniciate_dashboard, get_licensing
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

dashboard = iniciate_dashboard(API_KEY)

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
logging.info('Collecting licensing via API per %s company(ies)', total_progress)

for company in response:
    licensing = get_licensing(API_KEY,company["id"])
    raw_equip = licensing["licensedDeviceCounts"]
    equipments = json.dumps(raw_equip).replace(",", "\n").replace("{", "").replace("}", "")
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
table_svg(pTable, "fullTable_licensing")

# Providing markdown file in the outputs folder
logging.info('Creating md file from collected data')
mdFile.create_md_file()

# Providing html markmap file in the outputs folder
logging.info('Creating Markmap file from md file')
os.system('markmap --no-open outputs/meraki_licensing.md --output outputs/licensing_MindMap.html')



# Getting output files for specific OrgID
while True:
    desired_OrgID = input("\n >>>> Please, select desired \
Org ID to create files from table above: ")
    print('\n')
    logging.info('Creating .md , SVG and markmap file for requested Org ID: %s', desired_OrgID)
    get_orgid_outputs(dashboard, desired_OrgID)
    logging.info('Created .md , SVG and markmap file for requested Org ID: %s.', desired_OrgID)
    selection = input('\n  >>>> Would you like to continue \
with another Org ID SVG creation? [yes|no]: ')
    if selection.lower() == 'yes':
        continue
    break
