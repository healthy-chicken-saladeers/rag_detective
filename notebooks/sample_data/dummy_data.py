import xml.etree.ElementTree as ET

def extract_urls_from_sitemap(sitemap_file):
    # Parse the XML file
    tree = ET.parse(sitemap_file)
    root = tree.getroot()

    # Find all URL elements
    urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')

    # Count the total number of URLs
    total_urls = len(urls)

    # Create a list with formatted strings
    formatted_urls = [f'"{i + 1} of {total_urls}: {url.text}",' for i, url in enumerate(urls)]

    return formatted_urls

# File path for the sitemap
sitemap_file_path = 'sitemap.xml'

# Extract and print URLs
try:
    urls_list = extract_urls_from_sitemap(sitemap_file_path)
    for url in urls_list:
        print(url)
except FileNotFoundError:
    print("The file 'sitemap.xml' was not found.")
except ET.ParseError:
    print("There was an error parsing the XML file.")
