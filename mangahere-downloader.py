import requests
import os
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse

def is_valid(url):
    """
    Checks that the url is valid format
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def download(image_url, dest_path):
    """
    Downloads the first image on the page given the url and destination path to save it.
    """
    #For now, hardcode the manga name
    target = dest_path
    #Determine if path exists, else create it
    if not os.path.isdir(target):
        os.makedirs(target)
    #Set full pathname of file
    filename = os.path.join(target, image_url.split("/")[-1])
    r = requests.get(image_url, stream=True)
    if r.status_code==200:
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

def get_page_links(url):
    """
    Returns the list of URLs for all pages in that chapter
    """
    soup = bs(requests.get(url).content, "html.parser")
    #print("I'm at soup")
    urls = []
    #Find how many pages there are for this chapter
    for page in soup.find_all("option"):
        page_url = page.get("value")
        #The values don't start with https, so add it.
        page_url = urljoin("https:", page_url)
        if is_valid(page_url):
            urls.append(page_url)
            #print(page_url)

    return urls

def get_pages(urls, destination):
    """
    Returns the URL that is displayed in the pages reader div and downloads it to the destination
    """
    #print("There's just more soup!")
    page_image_urls = []
    for page in tqdm(urls, "Getting Source URLs"):
        soup = bs(requests.get(page).content, "html.parser")
        #Find the image source url
        page_image = soup.find("img")
        page_url = page_image.get("src")
        #Strip off the token and ttl from the url (everything after the "?")
        try:
            pos = page_url.index("?")
            page_url = page_url[:pos]
        except ValueError:
            pass
        #Verify the link is still valid and download
        if is_valid(page_url):
            download(page_url, destination)
            
    return page_image_urls

def main():
    manga ="vinland_saga"
    volume = "01"
    chapter = "001"
    destination = "/tmp/" + manga + "/" + volume + "/" + chapter
    url = "https://m.mangahere.cc/manga/" + manga + "/v" + volume + "/c" + chapter + "/"
    print(f"Starting scrape of: {url}")
    #Build the list of pages for the chapter
    page_urls = get_page_links(url)
    #Get the source image urls and download them
    get_pages(page_urls, destination)

main()