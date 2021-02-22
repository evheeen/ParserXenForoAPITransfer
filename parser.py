import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/88.0.4324.150 Safari/537.36 '
}
API = []
APIKey = 'Example Key'


def parseAndTransfer(url):
    print('Authentication...\n')
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    option.add_argument('--ignore-certificate-errors')
    option.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(options=option)
    
    # Authentication
    driver.get('https://example.com/login/')
    assert "Title" in driver.title
    login = driver.find_element_by_name('login')
    password = driver.find_element_by_name('password')
    login.send_keys("LOGIN")
    password.send_keys("PASSWORD")
    password.send_keys(Keys.ENTER)
    
    # Search for the number of pages
    driver.get(url)
    links = []
    pages = driver.find_element_by_class_name('pageNavHeader').text[13:]
    if str.isascii(pages[0]):
        pages = int(driver.find_element_by_class_name('pageNavHeader').text[14:])
    elif str.isascii(pages[1]):
        pages = int(driver.find_element_by_class_name('pageNavHeader').text[15:])
    elif str.isascii(pages[2]):
        pages = int(driver.find_element_by_class_name('pageNavHeader').text[16:])
    print('Found', pages, 'pages in node')
    
    # Copy links to topics
    print('Copy links to threads')
    for page in range(pages):
        print('Page', page + 1, 'of', pages)
        getLinks = driver.find_elements_by_class_name('PreviewTooltip')
        for l in getLinks:
            links.append(l.get_attribute('href'))
        nextPage = driver.find_element_by_xpath("//*[contains(text(),'Next')]")
        nextPage.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
        nextPage.click()
        time.sleep(0.5)
        driver.refresh()
    
    # Parsing
    print('Total threads:', len(links))
    
    # API config print
    configAPI()
    
    print('Parsing and transferring each thread:\n')
    for l in links:
        driver.get(l)
        title = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div[2]/h1').text[8:]
        description = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/form[1]/ol/li/div[2]/div[1]').text
        descriptionHTML = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/form[1]/ol/li/div[2]/div[1]')
        img = "[IMG]"+driver.find_element_by_class_name('bbCodeImage').get_attribute('src')+"[/IMG]"
        tagB = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/form[1]/ol/li/div[2]/div[1]')

        allHref = []
        href = driver.find_elements_by_class_name('quote')
        for hre in href:
            hre = hre.find_elements_by_class_name('externalLink')
            for h in hre:
                allHref.append(h.get_attribute('href'))

        # Formatting/removing
        if len(allHref) > 1:
            description = str.replace(description, allHref[1],
                                      "[THANKS][CLUB][URL=" + allHref[1] + "]Clickable[/URL][/CLUB][/THANKS]")
            description = str.replace(description, 'DOWNLOAD',
                                      "[THANKS][CLUB][URL=" + allHref[1] + "]Clickable[/URL][/CLUB][/THANKS]")
            description = str.replace(description, 'Another clickable text',
                                      "[THANKS][CLUB][URL=" + allHref[1] + "]Clickable[/URL][/CLUB][/THANKS]")
            description = str.replace(description, 'Another clickable text',
                                      "[THANKS][CLUB][URL=" + allHref[1] + "]Clickable[/URL][/CLUB][/THANKS]")
        if len(allHref) > 0:
            description = str.replace(description, allHref[0],
                                      "[CLUB][URL=" + allHref[0] + "]Clickable[/URL][/CLUB]")
            description = str.replace(description, 'DOWNLOAD',
                                      "[CLUB][URL=" + allHref[0] + "]Clickable[/URL][/CLUB]")
            description = str.replace(description, 'Another clickable text',
                                      "[CLUB][URL=" + allHref[0] + "]Clickable[/URL][/CLUB]")
        
        description = str.replace(description, 'Some text', '')
        description = str.replace(description, 'Some text:', '[B]SOME TEXT[/B]')
        description = str.replace(description, 'HIDDEN CONTENT', '')
        description = str.replace(description, '\n\n', '\n' + img + '\n', 1)
        
        descriptionHTML = descriptionHTML.get_attribute('innerHTML')
        descriptionHTML = descriptionHTML.split('\n')
        for element in descriptionHTML:
            if '<li>' in element:
                element = str.replace(element, '<li>', '')
                element = str.replace(element, '</li>', '')
                description = str.replace(description, element, "[LIST]"+element+"[/LIST]")
        
        tagB = tagB.find_elements_by_tag_name('b')
        for tag in tagB:
            tag = tag.text
            description = str.replace(description, tag, "[B]" + tag + "[/B]")
        
        time.sleep(5)

        # Creating thread on your forum via api
        print('Transferring thread', l)
        createThreadAPI(title, description)
        time.sleep(5)


def parsing():
    threadURL = input('Enter a link to the section: ')
    parseAndTransfer(threadURL)
    print('Parsing completed')


def configAPI():
    apiURL = 'https://example.application.com/api/'
    apiKey = APIKey
    
    print('URL to your API:', apiURL)
    print('API key:', apiKey)
    nodeId = int(input('Input node ID(number): '))
    prefixId = int(input('List of prefixes can be seen at the link '
                         'https://example.application.com/admin.php?thread-prefixes/. ID should be valid.\nInput '
                         'prefix ID(number):'))
    
    r = requests.post(apiURL, headers={'XF-Api-Key': apiKey})
    if r.json()['errors'][0]['code'] == 'api_key_not_found':
        print('Invalid API key\n')
    else:
        print('API key is valid\n')
        global API
        API = [apiURL, apiKey, nodeId, prefixId]


def createThreadAPI(title, message):
    head = {'XF-Api-Key': API[1]}
    params = {
        "node_id": API[2],
        "title": title,
        "message": message,
        "prefix_id": API[3]
    }
    r = requests.post(API[0] + "threads/", data=params, headers=head)
    if r.status_code == 200:
        print("Status: Okey")
    else:
        print('Error. Status code:', r.status_code)
        

if __name__ == '__main__':
    parsing()
