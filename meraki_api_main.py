import os
import json
import meraki
from dotenv import load_dotenv
from prettytable import PrettyTable
from mdutils.mdutils import MdUtils
from meraki_info import get_licensing, lic_date, table_svg
import logging 
import sys

# defining logging system

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
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
    logging.warning("Using default Meraki Always-On API KEY, please, create .env file if applying private API key.")
# Instead, use an environment variable as shown under the Usage section
# @ https://github.com/meraki/dashboard-api-python/

# Defining connectivity to Meraki (suppress logging since it works, Duh!)

dashboard = meraki.DashboardAPI(API_KEY, log_path="logs", suppress_logging=True)

# Gathering Org information list
logging.info('Gathering Organizations from Meraki via API')
response = dashboard.organizations.getOrganizations()

### MD File creation
logging.info('Creating md file under outputs folder')
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

# Structure the current Org table

pTable.align = "r"
pTable.sortby = "Expiration date"
pTable.hrules = True

# Providing SVG file in the outputs folder
logging.info('Creating SVG file from table')
table_svg(pTable)

# Providing markdown file in the outputs folder
logging.info('Creating md file from table')
mdFile.create_md_file()

# Providing html markmap file in the outputs folder
logging.info('Creating Markmap file from md file')
os.system(f'markmap --no-open outputs/meraki_licensing.md --output outputs/licensing_MindMap.html')
