import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def restart_browser():
    if browser:
        browser.quit()
    time.sleep(5)  # Adding a delay before restarting the browser
    browser = webdriver.Firefox(options=geoAllowed)
    return browser

# Set up Firefox options for geolocation
geoAllowed = webdriver.FirefoxOptions()
geoAllowed.set_preference("geo.enabled", False)  # Disable geolocation prompt

timeout_threshold = 60  # Timeout threshold in seconds

browser = None  # Initialize browser instance

while True:  # Loop to restart the script if there's a TimeoutException
    try:
        start_time = time.time()  # Record the start time

        # Start the WebDriver with the configured Firefox options if browser is not initialized
        if not browser:
            browser = webdriver.Firefox(options=geoAllowed)

        # Navigate to the website requiring location permissions
        browser.get("https://app.prizepicks.com/")

        # Click the initial button to dismiss pop-up
        initial_button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[3]/div/div/div[2]/button")))
        initial_button.click()

        time.sleep(2)  # Adding a delay after clicking the initial button

        # Find and click the button to scroll the page
        scroll_button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[3]/div[1]/div/main/div/nav[1]/button[2]")))
        for _ in range(2):  # Click the scroll button twice
            scroll_button.click()
            time.sleep(0.1)  # Wait for 0.1 seconds after clicking

        # Click the specified element after clicking the scroll button twice
        specified_element = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[3]/div[1]/div/main/div/nav[1]/div/div[16]/div")))
        specified_element.click()

        # Adding a delay to ensure navigation is completed
        time.sleep(2)

        # Wait for the new page to load
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div[3]/div[1]/div/main/div/nav[2]/div")))

        # Check if the URL is "https://app.prizepicks.com/error"
        if browser.current_url == "https://app.prizepicks.com/error":
            raise ValueError("URL Error")

        # Find the container element
        container = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div[1]/div/main/div/nav[2]/div")

        # Find all the desired elements within the container
        desired_elements = container.find_elements(By.XPATH, ".//div[@role='button']")

        # Scrape and print the text from each desired element
        for index, element in enumerate(desired_elements, start=1):
            element_text = element.text
            print(f"{index}. {element_text}")

        # Prompt the player for text input
        player_input = input("Enter your selection (number): ")
        try:
            selection_index = int(player_input)
            if 1 <= selection_index <= len(desired_elements):
                desired_elements[selection_index - 1].click()
                print("Clicked the selected element.")
                time.sleep(2)  # Adding a delay after clicking the desired element for navigation

                # Scraping player names and kill numbers
                player_names = browser.find_elements(By.XPATH, "//*[@id='test-player-name']")
                kill_numbers = browser.find_elements(By.XPATH, "/html/body/div[1]/div/div[3]/div[1]/div/main/div/div/div[1]/div[3]/ul/li/div[3]/div/div/div/div[1]")
                print("Player Name | Kill Number")
                for name, number in zip(player_names, kill_numbers):
                    print(f"{name.text} | {number.text}")

        except ValueError:
            print("Invalid input. Please enter a number.")

        # Check for the presence of the return button on the error page and click if found
        error_button = None
        while True:
            try:
                error_button = browser.find_element(By.CSS_SELECTOR, "button.return-button.css-t43oye")
                if error_button.is_displayed():
                    print("Return button element is visible on the screen.")
                    error_button.click()
                    print("Clicked the return button.")
                    break  # Exit the loop if return button is found and clicked
            except NoSuchElementException:
                pass  # Continue the loop if return button is not found

        # Calculate the elapsed time
        elapsed_time = time.time() - start_time

        # Check if no output is printed within the timeout threshold
        if elapsed_time > timeout_threshold:
            raise TimeoutException("No output within the timeout threshold")

    except TimeoutException:
        print("Timeout Exception occurred. Restarting script...")
        if browser:
            browser.quit()
            browser = None  # Reset browser instance
        continue  # Restart the loop if TimeoutException occurs

    except NoSuchElementException:
        print("Element not found. Restarting script...")
        if browser:
            browser.quit()
            browser = None  # Reset browser instance
        continue  # Restart the loop if NoSuchElementException occurs

    except Exception as e:
        print("An error occurred:", e)
        break  # Exit the loop if any other exception occurs
