import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import queue
import argparse
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_all_links(url, base_url):
    try:
        response = requests.get(url, verify=False)  # Disable SSL verification
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return set()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = set()
    for link in soup.find_all('a', href=True):
        full_url = urljoin(base_url, link['href'])
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            links.add(full_url)
    
    return links

def crawl_website(start_url):
    base_url = "{0.scheme}://{0.netloc}".format(urlparse(start_url))
    visited = set()
    to_visit = queue.Queue()
    to_visit.put(start_url)
    all_links = set()
    
    while not to_visit.empty():
        current_url = to_visit.get()
        if current_url not in visited:
            visited.add(current_url)
            links = get_all_links(current_url, base_url)
            all_links.update(links)
            for link in links:
                if link not in visited:
                    to_visit.put(link)
                    logging.info(f"Found link: {link}")
    
    return all_links

def save_links_to_file(links, filename="output.txt"):
    with open(filename, "w") as file:
        for link in links:
            file.write(link + "\n")

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Website Crawler")
    parser.add_argument("url", help="The URL of the website to crawl")
    parser.add_argument("-o", "--output", help="The output file to save the links", default="output.txt")
    
    args = parser.parse_args()
    
    logging.info(f"Starting to crawl the website: {args.url}")
    links = crawl_website(args.url)
    
    logging.info(f"Found {len(links)} links. Saving to {args.output}...")
    save_links_to_file(links, args.output)
    logging.info("Links saved successfully.")

if __name__ == "__main__":
    main()
