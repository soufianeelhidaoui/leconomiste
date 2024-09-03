import os

# Spécifiez directement le chemin vers chromedriver
chromedriver_path = 'c:/Users/chaym/Downloads/chromedriver-win64/chromedriver.exe'

if not os.path.exists(chromedriver_path):
    raise FileNotFoundError(f"Chromedriver non trouvé à l'emplacement spécifié: {chromedriver_path}")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
driver.get("http://example.com")
print(driver.title)
driver.quit()
