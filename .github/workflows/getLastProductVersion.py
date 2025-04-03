import logging

import requests
import re
import json
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


__version__ = "1.0.3"

def get_versions(api_url):
    versions = []
    page = 1
    per_page = 100  # Adjust this value based on your needs
    totalRecords = 0

    try:
        readRecords = 0  #records that alrady read
        while True:
            params = {"page": page, "page_size": per_page}
            response = requests.get(api_url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()  # Parse response as JSON
            try:
                pageCont = int(data["count"] / per_page) + 1
                if page == 1 :
                    totalRecords = data["count"]
                    print(f"    count is {totalRecords}  pageCont is {pageCont}  in {api_url} ")
            except:
                print("pageCont error")
            #print("debug- page:"+str(page)+ " totalRecords:"+str(totalRecords)+ " readRecords:"+ str(readRecords))

            results = data["results"]
            if not results:  # Stop if no more results are returned
                break
            #versions.extend(tag["name"] for tag in results)
            try:
                for image in results:
                    versions.append(image["name"])
            except:
                print("Error in page "+str(page))
            readRecords = readRecords + per_page
            if readRecords < totalRecords:
                page = page + 1
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
    #pattern = r"^v\d+\.\d+\.\d+$"
    #pattern = r"^(v\d+\.\d+\.\d+|\d+\.\d+)$"
    pattern = r"^(v\d+\.\d+\.\d+|\d+\.\d+|\d+\.\d+\.\d+\.\d+)$"
    versionx = None
    for item in data:
        if re.match(pattern, item['name']):
            versionx = item['name']
            break
    lastversion = versionx
    if re.match(r"^(v\d+\.\d+\.\d+)$",lastversion):
        lastversion = versionx[1:]
    if re.match(r"^(\d+\.\d+\.\d+\.\d+)$",lastversion):
        items = lastversion.split(".")
        lastversion = items[0]+"."+ items[1]+"."+ items[2]
    print(product + "  "+lastversion)
    data = {"product": product, "lastVersion": lastversion, "reportDate": current_date_string}
    return data

def getProductLastVersionrule1(product):
    time1 = get_current_time()
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
    time2 = get_current_time()
    result = calculate_time_delta(time1, time2, format='%Y-%m-%d %H:%M:%S')
    print(result)
    print(product +" last version is " + lastProductVersion)
    return data

def getProductLastVersionrule2(product):
    time1 = get_current_time()
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
    time2 = get_current_time()
    result = calculate_time_delta(time1, time2, format='%Y-%m-%d %H:%M:%S')
    print(result)
    print(product +" last version is " + lastProductVersion)
    return data





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

def get_current_time(format='%Y-%m-%d %H:%M:%S'):
    """Get current time in specified format"""
    return datetime.now().strftime(format)

def calculate_time_delta(time1, time2, format='%Y-%m-%d %H:%M:%S'):
    """
    Calculate the time difference between two times

    Args:
        time1 (str): First time
        time2 (str): Second time
        format (str, optional): Time string format. Defaults to '%Y-%m-%d %H:%M:%S'

    Returns:
        dict: Time delta details including total seconds, days, hours, minutes, seconds
    """
    # Convert time strings to datetime objects
    dt1 = datetime.strptime(time1, format)
    dt2 = datetime.strptime(time2, format)

    # Calculate time delta
    delta = abs(dt2 - dt1)

    # Break down delta into components
    return {
        'total_seconds': delta.total_seconds(),
        'days': delta.days,
        'hours': delta.seconds // 3600,
        'minutes': (delta.seconds % 3600) // 60,
        'seconds': delta.seconds % 60
    }
def getGitlablastversion(product):
    versions = None
    lastProductVersion = None
    # URL to fetch
    url = "https://gitlab.com/gitlab-org/gitlab-runner/-/releases"
    # Configure headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")  # Required for running as root on Linux
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

    # Set up the Chrome WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Open the webpage
        driver.get(url)

        # Wait for the dynamic content to load
        time.sleep(5)  # Adjust the sleep time as needed for the page to load fully
        html_content = driver.page_source
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all <a> elements with the class 'gl-link gl-self-center gl-text-default'
        version_elements = soup.find_all('a', class_='gl-link gl-self-center gl-text-default')

        # Extract and print the versions
        versions = [element.text.strip() for element in version_elements]
        if versions:
           # print("Found Versions:")
           # for version in versions:
           #     print(version)
            lastProductVersion = versions[0].replace('v', '')
        else:
            print("No versions found in the provided HTML.")
    finally:
        # Quit the browser
        driver.quit()
    #print("last version is: " + lastVersion)
    if lastProductVersion == None:
        print(product + " last version is None")
        return (lastProductVersion)
    else:
        data = {"product": product, "lastVersion": lastProductVersion, "reportDate": current_date_string}
        print(product + " last version is " + lastProductVersion)
        return (data)

def create_atlassian_products_versions_file():
    result = 0
    url = "https://api.atlassian.com/vuln-transparency/v1/products/versions"

    headers = {
        "Accept": "application/json"
    }

    # Define the parameters
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        with open("atlassian_products_versions.json", "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, sort_keys=True)
        print("JSON data has been saved to atlassian_products_versions.json")
    else:
        print(f"Failed to download atlassian_products_versions.json ")
        logging.INFO(f"Faild to download atlassian_products_versions.json ,${response.text} , ${response.status_code}  ")
        result = response.status_code

    return result

def create_atlassian_security_vulnerability_products_file():
    result = 0
    url = "https://api.atlassian.com/vuln-transparency/v1/products"

    headers = {
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        with open("atlassian_security_vulnerability_products.json", "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, sort_keys=True)
        print("JSON data has been saved to atlassian_security_vulnerability_products.json")
    else:
        print(f"Failed to download atlassian_security_vulnerability_products.json ")
        logging.INFO(f"Faild to download atlassian_security_vulnerability_products.json ,${response.text} , ${response.status_code}  ")
        result = response.status_code

    return result

def getProductLastVersionrule_atlassian(product):
    time1 = get_current_time()
    lastProductVersion = None
    data={"name":product,"lastversion":"","reportDate":current_date_string}
    body = {}
    with open("atlassian_products_versions.json", "r", encoding="utf-8") as file:
        body = json.load(file)
    atlassianproduct=""
    if product =="atlassian/bitbucket" :
        atlassianproduct = "Bitbucket Data Center"
    elif product =="atlassian/confluence":
        atlassianproduct = "Confluence Data Center"
    elif product =="atlassian/jira-servicemanagement":
        atlassianproduct = "JIRA Service Management Data Center"
    elif product =="atlassian/jira-software":
        atlassianproduct = "JIRA Software Data Center"
    else :
        print(f"error in getProductLastVersionrule_atlassian function product ${product} is not supported")
    lastProductVersion = body[atlassianproduct][0]
    data = {"product":product,"lastVersion": lastProductVersion,"reportDate":current_date_string}
    time2 = get_current_time()
    result = calculate_time_delta(time1, time2, format='%Y-%m-%d %H:%M:%S')
    print(result)
    print(product +" last version is " + lastProductVersion)
    return data



###### start ###############################
if __name__ == "__main__":
    json_array = []
    current_datetime = datetime.now()
    global current_date_string
    current_date_string = current_datetime.strftime("%d-%m-%Y")  # Format as "YYYY-MM-DD"
    print("current_date_string is " + current_date_string)
    create_atlassian_products_versions_file()
    create_atlassian_security_vulnerability_products_file()



    json_array.append(getProductLastVersionrule_atlassian("atlassian/jira-software"))
    json_array.append(getProductLastVersionrule_atlassian("atlassian/jira-servicemanagement"))
    json_array.append(getProductLastVersionrule_atlassian("atlassian/bitbucket"))
    json_array.append(getProductLastVersionrule_atlassian("atlassian/confluence"))

    #rul to read last version from github
    json_array.append(getProductLastVersionruleGithub("mattermost/mattermost"))
    json_array.append(getProductLastVersionruleGithub("airbytehq/airbyte"))
    json_array.append(getProductLastVersionruleGithub("jenkinsci/docker"))
    json_array.append(getProductLastVersionrule2("grafana/grafana"))
    json_array.append(getProductLastVersionruleGithub("SonarSource/sonarqube"))

    product = "artifactory"
    url = "https://jfrog.com/download-legacy/"
    json_array.append(get_latest_artifactory_version(url,product))

    #json_array.append(getGitlablastversion("gitlab/gitlab-ee"))
    json_array.append(getProductLastVersionrule1("gitlab/gitlab-ee"))

#    json_array.append(getProductLastVersionrule1("atlassian/jira-software"))
#    json_array.append(getProductLastVersionrule1("atlassian/jira-servicemanagement"))
#    json_array.append(getProductLastVersionrule1("atlassian/bitbucket"))
#    json_array.append(getProductLastVersionrule1("atlassian/confluence"))
    json_array.append(getProductLastVersionrule1("jenkins/jenkins"))
    json_array.append(getProductLastVersionrule1("library/nginx"))
    json_array.append(getProductLastVersionrule1("library/sonarqube"))
    json_array.append(getProductLastVersionrule1("airbyte/airbyte-api-server"))
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



