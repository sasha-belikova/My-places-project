from datetime import datetime
from pathlib import Path
import subprocess
import sys
import time

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


# Main website and text which means there are no appointments
URL = "https://appointment.bmeia.gv.at/"
NO_APPOINTMENTS_TEXT = (
    "For your selection there are unfortunately no appointments available"
)

# How many weeks the script checks after the first available week
WEEKS_TO_CHECK = 12

# Delay between offices because the website can block fast repeated visits
REQUEST_DELAY_SECONDS = 15

# True means the browser works in the background
HEADLESS = True

# Offices and document buttons which we need to check
OFFICES = [
    {"name": "Москва", "value": "MOSKAU", "calendar_id": "40044915"},
    {"name": "Астана", "value": "ASTANA", "calendar_id": "20213868"},
]


def wait_page(page):
    # Wait until the page is loaded enough to continue
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except PlaywrightTimeoutError:
        page.wait_for_timeout(1000)


def click_next(page):
    # Click only the real Next button, not the language Change button
    page.locator('input[name="Command"][value="Next"], button[value="Next"]').first.click(
        no_wait_after=True
    )
    page.wait_for_timeout(1000)
    wait_page(page)


def click_next_week(page):
    # Move to the next week on the appointments page
    page.locator('input[name="Command"][value="Next week"]').first.click(no_wait_after=True)
    page.wait_for_timeout(1000)
    wait_page(page)


def select_first_available_calendar(page, calendar_id=None):
    # Select the exact document button if we know its CalendarId
    calendar = page.locator("select#CalendarId")
    if calendar.count() == 0:
        return None

    options = calendar.locator("option").evaluate_all(
        """options => options
            .map(option => ({
                value: option.value,
                text: option.textContent.trim()
            }))
            .filter(option => option.value)
        """
    )
    if not options:
        return None

    selected = next((option for option in options if option["value"] == calendar_id), None)
    if selected is None:
        if calendar_id is not None:
            return None
        selected = options[0]

    calendar.select_option(selected["value"])
    return selected


def select_one_person(page):
    # The user said the number of persons is always 1
    for selector in ("select#PersonCount", 'select[name="PersonCount"]'):
        person_count = page.locator(selector)
        if person_count.count() > 0:
            person_count.select_option("1")
            return True

    return False


def collect_visible_slots(page):
    # Appointment times are radio buttons with name="Start"
    return page.locator('input[name="Start"]').evaluate_all(
        """
        inputs => inputs
            .map(input => input.value)
            .filter(Boolean)
        """
    )


def collect_available_slots(page):
    # Collect slots from the current week and then from the next weeks
    slots = set()
    for _ in range(WEEKS_TO_CHECK):
        slots.update(collect_visible_slots(page))

        if page.locator('input[name="Command"][value="Next week"]').count() == 0:
            break

        click_next_week(page)

    return sorted(slots, key=parse_slot)


def parse_slot(slot):
    # Site format example: 6/2/2026 8:30:00 AM
    return datetime.strptime(slot, "%m/%d/%Y %I:%M:%S %p")


def format_slot(slot):
    return parse_slot(slot).strftime("%d.%m.%Y %H:%M")


def is_final_page(page):
    # Final page has either no appointments text or appointment slots
    body_text = page.locator("body").inner_text()
    return (
        NO_APPOINTMENTS_TEXT in body_text
        or page.locator('input[name="Start"]').count() > 0
        or page.locator('input[name="Command"][value="Next week"]').count() > 0
    )


def go_to_final_page(page):
    # Some offices have extra information pages before the slots page
    for _ in range(5):
        if select_one_person(page):
            click_next(page)
            continue

        if is_final_page(page):
            return

        if page.locator('input[name="Command"][value="Next"]').count() == 0:
            return

        click_next(page)


def open_start_page(page):
    # Open the appointment system start page
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    wait_page(page)


def check_office(page, office, load_url=True):
    # Full check for one office: office -> document -> person -> slots
    if load_url:
        open_start_page(page)

    page.locator("select#Office").select_option(office["value"])
    click_next(page)

    calendar = select_first_available_calendar(page, office["calendar_id"])
    if calendar is None:
        return {
            "office": office["name"],
            "calendar": None,
            "dates": [],
            "error": "Не нашел список CalendarId после выбора офиса.",
        }

    click_next(page)
    go_to_final_page(page)

    body_text = page.locator("body").inner_text()
    if NO_APPOINTMENTS_TEXT in body_text:
        return {
            "office": office["name"],
            "calendar": calendar["text"],
            "dates": [],
            "error": None,
        }

    if page.locator('input[name="Start"]').count() == 0:
        return {
            "office": office["name"],
            "calendar": calendar["text"],
            "dates": [],
            "error": "Сообщения об отсутствии терминов нет, но слоты не найдены.",
        }

    slots = collect_available_slots(page)
    if not slots:
        return {
            "office": office["name"],
            "calendar": calendar["text"],
            "dates": [],
            "error": "Страница со слотами найдена, но даты не прочитаны.",
        }

    return {
        "office": office["name"],
        "calendar": calendar["text"],
        "dates": slots,
        "error": None,
    }


def print_result(result):
    # Print the result in a readable format
    if result["error"]:
        print(f"{result['office']}: {result['error']}", flush=True)
    elif result["dates"]:
        print(f"{result['office']}: есть термины", flush=True)
        print(f"Календарь: {result['calendar']}", flush=True)
        print("Даты: " + ", ".join(format_slot(date) for date in result["dates"]), flush=True)
    else:
        print(f"{result['office']}: терминов нет", flush=True)
        print(f"Календарь: {result['calendar']}", flush=True)
        print(NO_APPOINTMENTS_TEXT, flush=True)


def run_single_office(office):
    # Run one office in one browser
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page()
        try:
            result = check_office(page, office)
            print_result(result)
        except PlaywrightError as error:
            print(f"{office['name']}: ошибка при проверке: {error}", flush=True)
        finally:
            browser.close()


def main():
    # Internal mode: used when the script starts itself for one office
    if len(sys.argv) == 3 and sys.argv[1] == "--office":
        office = next((item for item in OFFICES if item["value"] == sys.argv[2]), None)
        if office is None:
            print(f"Неизвестный офис: {sys.argv[2]}", flush=True)
            sys.exit(1)

        run_single_office(office)
        return

    script_path = Path(__file__).resolve()
    exit_code = 0
    for index, office in enumerate(OFFICES):
        # Start each office as a separate process to avoid website hangs
        if index > 0:
            time.sleep(REQUEST_DELAY_SECONDS)

        result = subprocess.run([sys.executable, str(script_path), "--office", office["value"]])
        if result.returncode != 0:
            exit_code = result.returncode

    sys.exit(exit_code)

if __name__ == "__main__":
    main()


