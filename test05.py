from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def getGitlablastversion():
    versions = None
    lastVersion = None
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
            lastVersion = versions[0]
        else:
            print("No versions found in the provided HTML.")

    finally:
        # Quit the browser
        driver.quit()
    #print("last version is: " + lastVersion)
    return (lastVersion)

print("momo debug last gitlab version is: " + getGitlablastversion())