import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# DESCRIPTION:
# This program is made to scrape files from sharepoint using selenium and BeautifulSoup. To authenticate accessing the
# SharePoint site, the selenium script first logs into Miscosoft using credentials. It then reads the links in 
# "sharepointUrls.txt". The scraper then grabs the content from the sharepoint site, and trims off any unecessary content
# (headers, footers, navbars, etc...). The contents of the page are sent to a .md file.

# Load environment variables (including OpenAI API key)
load_dotenv()

microsoftUsername = os.environ["MICROSOFT_USERNAME"]
microsoftPassword = os.environ["MICROSOFT_PASSWORD"]

def login(driver: webdriver.Chrome):
    # Navigate to the Microsoft login page
    driver.get("https://login.microsoftonline.com/")
    # Wait until the email input field "loginfmt" is visible (max wait time 10 seconds)
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "loginfmt"))
    )
    # Find and fill the email field
    email_input = driver.find_element(By.NAME, "loginfmt")
    email_input.send_keys(microsoftUsername)
    email_input.send_keys(Keys.RETURN)
    time.sleep(5)
    # Wait until the email input field "loginfmt" is visible (max wait time 10 seconds)
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "passwd"))
    )
    # Find and fill the email field
    email_input = driver.find_element(By.NAME, "passwd")
    email_input.send_keys(microsoftPassword)
    email_input.send_keys(Keys.RETURN)


# Function to extract content and save it as .md file
def save_page_content(driver: webdriver.Chrome, url):
    try:
        # After logging in, navigate to the target page
        driver.get(url)
        # Wait for 10 seconds to allow the page to fully load after logging in
        time.sleep(10)
        # Get the page source and pass it to BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Remove unwanted elements such as headers, footers, and sidebars
        for unwanted in soup(["header", "footer", "nav", "aside"]):
            unwanted.extract()
        # Now extract the main content
        main_content = soup.find('main') or soup.find('article') or soup.find('body') 
        # Extract text content
        body_text = ""
        if main_content:
            body_text = main_content.get_text(separator="\n", strip=True)
        # Combine the body text and the code blocks (if any)
        content = body_text
        # Get the title of the page for the filename
        page_title = driver.title
        # Create a safe filename by removing or replacing illegal characters
        filename = re.sub(r'[\\/*?:"<>|]', "", page_title) + ".md"
        # Create the 'data' folder if it doesn't exist
        if not os.path.exists("data"):
            os.makedirs("data")
        # Save the body text and code blocks to a .md file in the 'data' folder
        filepath = os.path.join("data", filename)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"Content from {url} saved to {filepath}")
    except Exception as e:
        print(f"Error processing {url}: {e}")


# Main function to iterate through URLs in a .txt file
def process_urls_from_file(file_path):
    # Set up Selenium WebDriver with Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(options=chrome_options)
    login(driver)
    # Open the .txt file containing the list of URLs
    with open(file_path, "r") as file:
        urls = file.readlines()
    # Iterate through each URL
    for url in urls:
        url = url.strip()  # Remove any leading/trailing whitespace or newlines
        if url:  # Check if the URL is not empty
            save_page_content(driver, url)
    # Close the browser after processing all URLs
    driver.quit()


if __name__ == "__main__":
    # Path to the .txt file containing the URLs (one per line)
    url_file_path = "sharepointUrls.txt"
    # Process all URLs in the file
    process_urls_from_file(url_file_path)