import os
import platform
import subprocess
import sys
import time
import zipfile

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def install_selenium():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])


def install_google_chrome():
    print("Google Chrome is not installed. Proceeding to install Google Chrome...")

    if platform.system() == "Linux":
        subprocess.check_call(["apt-get", "update"])
        subprocess.check_call(["apt-get", "install", "-y", "google-chrome-stable"])
    elif platform.system() == "Darwin":
        subprocess.check_call(["brew", "cask", "install", "google-chrome"])
    elif platform.system() == "Windows":
        print("Please manually install Google Chrome for Windows.")
        sys.exit(1)
    else:
        print("Unsupported operating system. Please manually install Google Chrome.")
        sys.exit(1)


def get_chrome_version():
    try:
        process = subprocess.Popen(["google-chrome-stable", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = process.communicate()
        version = stdout.decode("utf-8").strip().split(" ")[2]
        return version
    except Exception as e:
        print(f"Failed to get Chrome version: {e}")
    return None


def download_chromedriver(version):
    chrome_version_major = version.split(".")[0]
    driver_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_version_major}"

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(driver_url)

    latest_release = driver.find_element(By.TAG_NAME, "pre").text
    driver.quit()

    if platform.system() == "Linux":
        driver_url = f"https://chromedriver.storage.googleapis.com/{latest_release}/chromedriver_linux64.zip"
    elif platform.system() == "Darwin":
        driver_url = f"https://chromedriver.storage.googleapis.com/{latest_release}/chromedriver_mac64.zip"
    elif platform.system() == "Windows":
        print("Please manually download and install ChromeDriver for Windows.")
        sys.exit(1)
    else:
        print("Unsupported operating system. Please manually download and install ChromeDriver.")
        sys.exit(1)

    driver_path = f"chromedriver_{latest_release}"
    download_path = f"{driver_path}.zip"

    subprocess.check_call(["curl", "-o", download_path, driver_url])

    with zipfile.ZipFile(download_path, "r") as zip_ref:
        zip_ref.extractall(driver_path)

    os.remove(download_path)

    if platform.system() != "Windows":
        subprocess.check_call(["chmod", "+x", f"{driver_path}/chromedriver"])

    return driver_path


def main():
    install_selenium()

    if platform.system() != "Linux":
        print("This code is intended for Linux operating systems only. Exiting...")
        sys.exit(1)

    chrome_version = get_chrome_version()

    if chrome_version is None:
        install_google_chrome()
        chrome_version = get_chrome_version()

        if chrome_version is None:
            print("Failed to install Google Chrome. Exiting...")
            sys.exit(1)

    print(f"Detected Chrome version: {chrome_version}")

    login_url = input("Enter the login URL: ")
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    driver_path = download_chromedriver(chrome_version)
    print(f"Downloaded ChromeDriver: {driver_path}")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    driver.get(login_url)

    # Perform login using appropriate selectors based on the website's attribute names
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")

    username_field.send_keys(username)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)

    time.sleep(5)

    # Perform actions on the logged-in page

    driver.quit()


if __name__ == "__main__":
    main()
