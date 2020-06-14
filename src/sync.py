# adapted from https://www.bryanklein.com/blog/hugo-python-gsheets-oh-my/

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
import os
import json
import re

# Get JSON_DATA from the build environment.
jsondict = json.loads(os.environ['JSON_DATA'])

# Use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(jsondict, scope)
client = gspread.authorize(creds)
workbook = client.open_by_key("1KNfIhyV8oSNOmzZQCOGY1Zhc-2n_e4Uk0iD3rxf0oTg")

sheets = [("ontario", "ON Organizing", "Ontario"),
          ("british-columbia", "BC Organizing", "BC"),
          ("alberta", "AB Organizing", "Alberta"),
          ("saskatchewan", "SK Organizing", "Saskatchewan"),
          ("manitoba", "MB Organizing", "Manitoba"),
          ("quebec", "QC Organizing", "Québec"),
          ("maritimes", "Maritime Organizing", "Maritimes"),
          ("territories", "Territories Organizing", "Territories")]

for (province, sheetname, title) in sheets:
  output_path = Path("content/organizations/" + province + "/")
  [ os.remove(output_path / f) for f in os.listdir(output_path) if not f.startswith("_") and f.endswith(".md") ]

  indexfile = output_path / "_index.md"
  index_yaml = open(indexfile, 'w')
  index_yaml.write("---\ntitle: " + title + "\n---")
  index_yaml.close()

  claimsheet = workbook.worksheet(sheetname)

  # Extract all of the records for each row.
  records = claimsheet.get_all_records()

  # Set location to write new files to.

  # Loop through each row...
  for row in records:
    if True: #row.get("Approved") == "yes":
      # Open a new file with filename based on the first column
      filename = row.get("Organization Name").lower().replace(" ", "-")
      filename = re.sub(r'[^a-z0-9-]',"", filename) + '.md'
      outputfile = output_path / filename
      new_yaml = open(outputfile, 'w')

      # Empty string that we will fill with YAML formatted text based on data extracted from our CSV.
      yaml_text = ""
      yaml_text += "---\n"
      #_yaml_text += "draft: false\n"
      yaml_text += "title: \"" + row.get("Organization Name").replace('"', '\\"') + "\"\n"
      yaml_text += "region: " + province + "\n"
      yaml_text += "admin_include: true\n"
      yaml_text += "website: " + row.get("Website") + "\n"
      yaml_text += "email: " + row.get("Email") + "\n"
      yaml_text += "location: " + row.get("Location") + "\n"
      yaml_text += "phone: " + row.get("Phone | Contact Name (if applicable") + "\n"

      social_media = row.get("Social Media")
      if social_media:
        social_medias = ["\n - " + s for s in social_media.splitlines() if s]
        yaml_text += "social_media: " + "".join(social_medias) + "\n"

      # Write our YAML string to the new text file and close it.
      new_yaml.write(yaml_text + "---\n\n")
      new_yaml.write("## Mission\n\n")
      new_yaml.write(row.get("Mission"))
      new_yaml.write("\n\n")

      if row.get("Member Activities"):
        new_yaml.write("## Member Activities\n\n")
        new_yaml.write(row.get("Member Activities"))
        new_yaml.write("\n\n")

      new_yaml.close()
