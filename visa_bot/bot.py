from playwright.sync_api import sync_playwright      # Add Playwright to the code

with sync_playwright() as p:                         # allows Playwright opening a browser and running the code inside
                                                     # p means Playwright
    browser = p.chromium.launch(headless=False)      # opens a Chrome browser, headless=False means the browser will be visible
    page = browser.new_page()                        # opens a new page in the browser
    page.goto('https://appointment.bmeia.gv.at/')    # navigates to the website of appointments for the Austrian embassy
    page.wait_for_load_state()                       # waits until the page is fully loaded
    

    page.locator('select#Office').select_option('MOSKAU') # selects the option 'MOSKAU' from the dropdown menu
    page.click('input') 
    page.locator('select#CalendarId').select_option('40044915')
    page.click('input') 
    
    input('Press Enter to close the browser')        

    browser.close()