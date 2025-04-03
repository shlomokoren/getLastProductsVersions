import requests
import json


def fetch_bitbucket_vulnerabilities():
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    params = {
        "keywordSearch": "Bitbucket Data Center",
        "resultsPerPage": 100,
        "startIndex": 0
    }

    all_vulnerabilities = []

    while True:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            break

        data = response.json()
        vulnerabilities = data.get("vulnerabilities", [])
        all_vulnerabilities.extend(vulnerabilities)

        total_results = data.get("totalResults", 0)
        params["startIndex"] += params["resultsPerPage"]

        if params["startIndex"] >= total_results:
            break

    return all_vulnerabilities


if __name__ == "__main__":
    vulnerabilities = fetch_bitbucket_vulnerabilities()
    print(json.dumps(vulnerabilities, indent=2))
