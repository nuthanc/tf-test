import requests
import re

#variables

# target URL to scrap
url = input("Enter url to scrape tc: ") 

# headers
headers = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
}

# send request to download the data
response = requests.request("GET", url, headers=headers)

tc_list = [] # Stores all the testcases
loc_list = [] # Stores the location of testcases

def construct_fully_qualified_test_name(test_case, test_case_with_class, loc):
    # import pdb;pdb.set_trace()
    loc_dot_separated = loc.split('contrail-test/')[1].replace('/', '.').split('.py')[0]
    test_case_with_class = test_case_with_class.split('[')[0]
    fq_name_tc = loc_dot_separated + "." + test_case_with_class
    print("Fully qualified test name:", fq_name_tc)

# parse the downloaded data
def parse_data():
    try:
        from bs4 import BeautifulSoup
    except Exception:
        import os
        os.system('pip3 install bs4')
        from bs4 import BeautifulSoup
    data = BeautifulSoup(response.text, 'html.parser')
    # print(data.find("tr",{"class":"Error"}).prettify()) 
    error_class_html = data.find_all("tr", {"class": "Error"})
    with open('log.html','w') as f:
        f.write(str(error_class_html))
    print(len(error_class_html))
    for error in error_class_html:
        case = (error.find_all('td'))
        test_case_with_class = case[0].text
        test_case = case[0].text.split("[")[0].split(".")[1]
        # import pdb;pdb.set_trace()
        if test_case.startswith('test'):
            loc = re.findall(r'/contrail-test/s.*?py', case[2].text)[0]
            tc_list.append(test_case)
            loc_list.append(loc)
            construct_fully_qualified_test_name(test_case, test_case_with_class, loc)
        else:
            loc = re.findall(r'/contrail-test/.*?py', case[2].text)[0]

        print(test_case)
        print("Test case with class:", test_case_with_class)
        print("Location of test case:",loc)
        print()


if __name__ == "__main__":
    parse_data()