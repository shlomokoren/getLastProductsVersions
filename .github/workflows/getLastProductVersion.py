import requests
import re
import json
from datetime import datetime
import time
from bs4 import BeautifulSoup

__version__ = "1.0.1"

def get_versions(api_url):
    versions = []
    page = 1
    per_page = 100  # Adjust this value based on your needs

    try:
        readRecords = 0  #records that alrady read
        while True:
            params = {"page": page, "page_size": per_page}
            response = requests.get(api_url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()  # Parse response as JSON
            totalRecords = 0
            try:
                pageCont = int(data["count"] / per_page) + 1
                if page == 1 :
                    totalRecords = data["count"]
                    print(f"    count is {totalRecords}  pageCont is {pageCont}  in {api_url} ")
            except:
                print("pageCont error")

            results = data["results"]
            if not results:  # Stop if no more results are returned
                break
            versions.extend(tag["name"] for tag in results)
            readRecords = readRecords + per_page
            if readRecords < totalRecords:
                page += 1
                time.sleep(2)
            else:
                break
    except requests.RequestException as e:
        print(f"Request Error: {e}")
        return None

    return versions

def getlastVersion(versions,product):
    lastversion = ""
    pattern = r'\b\d{1,3}\.\d{1,3}(?:\.\d{1,3})?\b$'
    if(product == "library/sonarqube"):
        pattern = r'\b\d{1,3}\.\d{1,3}(?:\.\d{1,3})?-enterprise\b$'
    elif (product == "gitlab/gitlab-ee"):
        pattern = r'\b\d{1,3}\.\d{1,3}(?:\.\d{1,3})?-ee.0\b$'
    # Check each element in the list against the pattern
    matches = [element for element in versions if re.match(pattern, element)]
#    print(matches)
    if len(matches)> 0:
        sorted_versions = sorted(matches, key=lambda x: [int(num) if num.isdigit() else num for num in
                                                         x.split('-')[0].split('.')])
        lastversionx = sorted_versions[-1]
        lastversion = str(lastversionx).split("-")[0]
    return lastversion

def getProductLastVersionruleGithub(product):
    data = {"product": product, "lastVersion": "0", "reportDate": current_date_string}
    url="https://api.github.com/repos/"+product+"/tags"
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to load page: {response.status_code}")
        return None
    data = response.json()
    pattern = r"^v\d+\.\d+\.\d+$"
    versionx = None
    for item in data:
        if re.match(pattern, item['name']):
            versionx = item['name']
            break
    lastversion = versionx[1:]
    print(product + "  "+lastversion)
    data = {"product": product, "lastVersion": lastversion, "reportDate": current_date_string}
    return data

def getProductLastVersionrule1(product):
    lastProductVersion = None
    data={"name":product,"lastversion":"","reportDate":current_date_string}
    api_url = "https://hub.docker.com/v2/repositories/"+product+"/tags/"
    versions = None
    try:
        versions = get_versions(api_url)
        if not versions:
            print("Failed to fetch versions.")
            return None
    except:
        print("Failed to fetch versions.")
        return None

    lastProductVersion = getlastVersion(versions,product)
    data = {"product":product,"lastVersion": lastProductVersion,"reportDate":current_date_string}
    print(product +" last version is " + lastProductVersion)
    return data

def getProductLastVersionrule2(product):
    lastProductVersion = None
    products = product.split("/")
    data={"name":product,"lastversion":"","reportDate":current_date_string}
    api_url = "https://hub.docker.com/v2/namespaces/" + products[0] + "/repositories/"+products[1]+"/tags?page_size=100"
    versions = None
    try:
        versions = get_versions(api_url)
        if not versions:
            print("Failed to fetch versions.")
            return None
    except:
        print("Failed to fetch versions.")
        return None
    lastProductVersion = getlastVersion(versions,product)
    data = {"product":product,"lastVersion": lastProductVersion,"reportDate":current_date_string}
    print(product +" last version is " + lastProductVersion)
    return data



from datetime import datetime

import requests
from bs4 import BeautifulSoup


def get_latest_artifactory_version(url,product):
    data={"name":product,"lastversion":"","reportDate":current_date_string}
    # Send a GET request to the provided URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to load page: {response.status_code}")
        return None
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the element containing the Artifactory version information
    h2_element = soup.find('h2', class_='text-font-stack font-weight-bold')

    if not h2_element:
        raise Exception("Artifactory version element not found on the page.")
        return None
    # Ensure that the product name is "Artifactory"
    product_name = h2_element.find('span', class_='productName')
    if product_name and product_name.text.strip() == 'Artifactory':
        # Extract the version number from the <span> with class 'version'
        version_element = h2_element.find('span', class_='version')
        if version_element:
            version_text = version_element.text.strip()
            data = {"product": product, "lastVersion": version_text, "reportDate": current_date_string}
            return data

    raise Exception("Artifactory version information is not structured as expected.")
    return None


def json_to_html_table(json_str):
    try:
        data = json.loads(json_str)
        if not isinstance(data, list):
            raise ValueError("Input JSON must be a list")
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>products versions</title>
        </head>
        <body>
        """
        html += "<H1>Products Versions Report for "+current_date_string+"</H1>"

        html += """
               <table border='1' style='text-align:left; border-collapse: collapse;'>
                <tr style='background-color:#f2f2f2;'><th style='background-color:#ddd;'>Product Name</th><th style='background-color:#ddd;'>Product Last Version</th></tr>
        """  # Header row with background color
#        html = "<table border='1' style='text-align:left; border-collapse: collapse;'>\n"  # Added border-collapse for better borders
#        html += "<tr style='background-color:#f2f2f2;'><th style='background-color:#ddd;'>Product Name</th><th style='background-color:#ddd;'>Product Last Version</th></tr>\n"  # Header row with background color

        # Alternate row colors for better readability
        for i, entry in enumerate(data):
            product = entry.get("product", "")
            last_version = entry.get("lastVersion", "")
            bgcolor = "#ffffff" if i % 2 == 0 else "#f2f2f2"
            html += f"<tr style='background-color:{bgcolor};'><td>{product}</td><td>{last_version}</td></tr>\n"

 #       html += "</table>"
        html += """
             </table>
         </body>
         </html>
         """
        return html
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
    except Exception as e:
        print("An error occurred:", e)



# start
if __name__ == "__main__":
    json_array = []
    current_datetime = datetime.now()
    global current_date_string
    current_date_string = current_datetime.strftime("%d-%m-%Y")  # Format as "YYYY-MM-DD"
    print("current_date_string is " + current_date_string)

    #rul to read last version from github
    json_array.append(getProductLastVersionruleGithub("mattermost/mattermost"))
    json_array.append(getProductLastVersionrule2("grafana/grafana"))
    product = "artifactory"
    url = "https://jfrog.com/download-legacy/"
    json_array.append(get_latest_artifactory_version(url,product))

    json_array.append(getProductLastVersionrule1("gitlab/gitlab-ee"))
    json_array.append(getProductLastVersionrule1("atlassian/jira-software"))
    json_array.append(getProductLastVersionrule1("atlassian/jira-servicemanagement"))
    json_array.append(getProductLastVersionrule1("atlassian/bitbucket"))
    json_array.append(getProductLastVersionrule1("atlassian/confluence"))
    json_array.append(getProductLastVersionrule1("jenkins/jenkins"))
    json_array.append(getProductLastVersionrule1("library/nginx"))
    json_array.append(getProductLastVersionrule1("library/sonarqube"))
    json_array.append(getProductLastVersionrule1("airbyte/airbyte-api-server"))
    json_array.append(getProductLastVersionrule1("airbyte/server"))
    json_array.append(getProductLastVersionrule1("dynatrace/dynatrace-operator"))
    json_array.append(getProductLastVersionrule1("grafana/grafana-enterprise"))
    json_array.append(getProductLastVersionrule1("selenium/hub"))
    json_array.append(getProductLastVersionrule1("bitnami/argo-cd"))


    # Convert the list to a JSON array
    json_string = json.dumps(json_array)

    # Write the JSON array to a file
    with open("products_versions.json", "w") as json_file:
         result = json_file.write(json_string)

    # Convert JSON to HTML table
    html_table = json_to_html_table(json_string)

    # Write HTML table to a file
    with open("products_versions.html", "w") as f:
        f.write(html_table)
        print("HTML table has been written to products_versions.html")



