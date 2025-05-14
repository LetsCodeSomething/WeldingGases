from bs4 import BeautifulSoup as bs
import os
import sys
import requests
import time
import shutil

st_accept = "text/html"
st_useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"
headers = {
   "Accept": st_accept,
   "User-Agent": st_useragent
}

NIIKM_BASE_LINK = "https://www.niikm.ru/"
NIIKM_LINKS = ["products/azot/", "products/argon/", "products/acetylene/", "products/hydrogen/", "products/helium/",
               "products/carbon_dioxide/", "products/oxygen/", "products/krypton/", "products/xenon/",
               "products/methane/", "products/neon/", "products/spbt/"]
REQUEST_DELAY = 3
OUTPUT_FOLDER = "niikm_data/"

def parse_url(url):
    print("Parsing html from \"" + url + "\".")

    req = requests.get(url, headers)

    if req.status_code != 200:
        print("    ERROR: The request status code is " + str(req.status_code) + ".")
        return

    soup = bs(req.text, 'lxml')
    
    page_title = soup.find("div", attrs={"class":"title-page"})
    if page_title == None:
        print("    ERROR: Could not find page title.")
        return

    f = open(OUTPUT_FOLDER + "niikm_" + page_title.text.lstrip().rstrip().replace("\n","") + ".txt", 'w', encoding="utf-8")
    f.write("НАЗВАНИЕ: " + page_title.text.lstrip().rstrip().replace("\n","") + "\n")

    #Required for distinguishing articles and product pages.
    is_product_page = True
    product_description = soup.find("div", attrs={"class":"product-card-dbl__col product-card-dbl__description-product"})
    product_card = soup.find("div", attrs={"class":"product-card"})
    if product_description == None and product_card == None:
        is_product_page = False

    if is_product_page:
        print("    INFO: The page is a product page.")

        #Parse the state standard.
        product_keywords = soup.find("p", attrs={"class":"keywords"})
        if product_keywords == None:
            print("    INFO: Could not find the state standard.")
        else:
            print("    Found the state standard: " + product_keywords.text)
            f.write("ГОСТ / НОРМАТИВНЫЙ ДОКУМЕНТ: " + product_keywords.text + "\n")

        #Parse the product composition.
        product_composition_table = soup.find("table", attrs={"class":"data-text"})
        if product_composition_table == None:
            product_composition_table = soup.find("div", attrs={"class":"category__grid-wrap category__table-wrap"})

            if product_composition_table == None:
                print("    INFO: Could not find the product composition table.")
            else:
                f.write("ТРЕБОВАНИЯ К ПРОДУКТУ ПО ГОСТ:\n")

                table_column_count = 0
                table_column_index = 0
                for i in product_composition_table.find_all("div"):
                    if i["class"][0] == "category__head-cell":
                        f.write(i.text.strip() + "        ")
                        table_column_count += 1
                    else:
                        if table_column_index == 0:
                            f.write("\n")

                        f.write(i.text.strip() + "        ")
                        table_column_index += 1
                        if table_column_index > table_column_count - 1:
                            table_column_index = 0
                f.write("\n\n")
        else:
            print("    Parsing the product composition table...")
            f.write("ТРЕБОВАНИЯ К ПРОДУКТУ ПО ГОСТ:\n")

            #Parse the table head.
            for i in product_composition_table.find("thead").find("tr").children:
                f.write(i.text.strip() + "        ")
            f.write("\n")

            #Parse the table content.
            
            #For some reason BeautifulSoup can just randomly remove tags
            #from the received page, so we need to check if the table has
            #tbody.
            table_body = product_composition_table.find("tbody")
            if table_body == None:
                #Congratulations, the table does not have tbody!
                for i in product_composition_table.children:
                    if i.name == "tr":
                        for j in i.children:
                            f.write(j.text.strip() + "        ")
                        f.write("\n")
                f.write("\n")
            else:
                #Parse in the normal way.
                table_content = table_body.find_all("tr")
                for i in table_content:
                    for j in i.children:
                        f.write(j.text.strip() + "        ")
                f.write("\n\n")

        #Parse the textual description.
        if product_description == None:
            print("    INFO: Could not find the product description.")
        else:
            print("    Parsing the product description...")
            for i in product_description.children:
                if i.name == "p":
                    f.write(i.text.lstrip().rstrip().replace("Мы предлагаем:","") + "\n")
            print("        Done.")

        #Parse the detailed chemical description.
        if product_card == None:
            print("    INFO: Could not find the product card.")
        else:
            print("    Parsing the product card...")

            tabs = soup.find("div", attrs={"class":"product-card__tabs-content-wrap"}).find_all("div")
            properties_tab = None
            for i in range(len(tabs)):
                if str(tabs[i]).find("Физико-химические свойства") != -1:
                    properties_tab = tabs[i]
                    break

            if properties_tab == None:
                print("        INFO: Could not find the tab with the properties.")
            else:
                f.write("ОСНОВНЫЕ СВОЙСТВА:\n")
                for i in properties_tab.children:
                    if i.name == "ul":
                        for j in i.children:
                            if j.name == "li":
                                spans = j.find_all("span")
                                f.write(spans[0].text + ": " + spans[1].text + "\n")
                    elif i.name == "p":
                        f.write(i.text + ":\n")
            print("        Done.")

        #Check if the page contains references to other pages. If it does, then
        #traverse them recursively.
        product_assortment = soup.find("div", attrs={"class":"product-card-dbl__product-range-wrap"})
        if product_assortment == None:
            print("    INFO: The page does not contain references to the product subtypes.")
        else:
            print("    Starting the recursive traversal of the product subtypes...\n")
            for i in product_assortment:
                time.sleep(REQUEST_DELAY)

                if i.name == "a":
                    if i["href"][0] == '/':
                        parse_url(NIIKM_BASE_LINK[:-1] + i["href"])
                    else:
                        parse_url(NIIKM_BASE_LINK + i["href"])
            print("\n        Done.")
    else:
        #TODO: add code for articles.
        print("    INFO: The page is an article page. Skipping.")
        pass

    f.close()
    print("    Done.")

#############################

import argparse

def prepare_dir(string):
    if not os.path.isdir(string):
        os.mkdir(string)
    return string

params = argparse.ArgumentParser(description=
"""Parses https://www.niikm.ru/ web-site and saves the obtained information on welding gases in the specified directory.""",
formatter_class=argparse.RawDescriptionHelpFormatter, epilog=
"""EXAMPLE

python niikm_parser.py -d 3 -o niikm_data -z

Parse https://www.niikm.ru/ web-site and wait 3 seconds between each request to the web-site, save the obtained information on welding gases in \"niikm_data\" directory and compress it into zip archive.""")

params.add_argument("-d", "--request-delay", type=int, help="The delay in seconds between each request to https://www.niikm.ru/. The delay must be greater than or equal to 0 and lesser than or equal to 20 seconds. If the parameter is missing, the delay will default to 3 seconds.")
params.add_argument("-o", "--output-dir", type=prepare_dir, help="An output directory name. If the parameter is missing, the name will default to \"niikm_data\".")
params.add_argument("-z", "--zip", action="store_true", help="Compress the output directory into zip archive.")

params = params.parse_args()

if params.request_delay:
    if params.request_delay < 0 or params.request_delay > 20:
        sys.exit("The request delay value must be in the range [0; 20]. Exiting.")
    else:
        REQUEST_DELAY = params.request_delay

if params.output_dir:
    OUTPUT_FOLDER = params.output_dir + "/"
else:
    prepare_dir("niikm_data")

for i in NIIKM_LINKS:
    parse_url(NIIKM_BASE_LINK + i)
    time.sleep(REQUEST_DELAY)

if params.zip:
    shutil.make_archive(OUTPUT_FOLDER[:-1] + ".zip", 'zip', OUTPUT_FOLDER[:-1])