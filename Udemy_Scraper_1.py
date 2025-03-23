import csv
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from concurrent.futures import ThreadPoolExecutor

# Define a list of user agents to avoid detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
]

def initialize_driver():
    """Initialize the WebDriver with anti-detection options."""
    user_agent = random.choice(USER_AGENTS)  # Select a random user agent
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")  # Headless mode for efficiency
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")  # Bypass detection
    return driver

def extract_types(url):
    """Extract MainType and SubType from Udemy URL structure."""
    parts = url.split("/courses/")[-1].split("/")
    return (parts[0] if len(parts) > 0 else "Unknown"), (parts[1] if len(parts) > 1 else "Unknown")

def scrape_udemy_page(driver, page_url, page_number):
    """Scrape Udemy courses from a given page number."""
    main_type, sub_type = extract_types(page_url)
    url = f"{page_url}?p={page_number}"
    
    driver.get(url)
    
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'course-card_main-content__aceQ0')]"))
        )
    except TimeoutException:
        print(f"Timeout while loading page {url}")
        return []

    course_cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'course-card_main-content__aceQ0')]")
    courses_data = []

    for card in course_cards:
        try:
            url_element = card.find_element(By.XPATH, ".//a[contains(@href, '/course/')]")
            title_element = card.find_element(By.XPATH, ".//h3[contains(@class, 'course-card-title_course-title')]//a")
            rating_element = card.find_element(By.XPATH, ".//span[contains(@class, 'star-rating_rating-number')]")
            reviews_element = card.find_element(By.XPATH, ".//span[@aria-label]")
            duration_element = card.find_element(By.XPATH, ".//span[contains(@class, 'course-card-details_row')]")
            instructor_element = card.find_element(By.XPATH, ".//div[contains(@class, 'course-card-instructors_instructor-list')]")

            course_info = {
                'Title': title_element.text.split("\n")[0],
                'URL': url_element.get_attribute("href"),
                'Rating': rating_element.text.strip() if rating_element else "N/A",
                'Reviews': reviews_element.text.strip() if reviews_element else "N/A",
                'Duration': duration_element.text.strip() if duration_element else "N/A",
                'Instructor': instructor_element.text.strip() if instructor_element else "N/A",
                'MainType': main_type,
                'Subtype': sub_type
            }
            courses_data.append(course_info)

        except NoSuchElementException:
            continue  # Skip if any element is missing

    return courses_data

def scrape_category(category_url):
    """Scrape multiple pages from a single Udemy category."""
    driver = initialize_driver()
    all_courses = []
    
    for page in range(1, 6):  # Scrape first 5 pages per category
        courses = scrape_udemy_page(driver, category_url, page)
        if not courses:
            break  # Stop if no courses are found
        all_courses.extend(courses)
        time.sleep(random.uniform(2, 4))  # Randomized wait to prevent blocking

    driver.quit()
    save_to_csv(all_courses)

def save_to_csv(data, filename='udemy_courses.csv'):
    """Save scraped course data to a CSV file."""
    fieldnames = ['Title', 'URL', 'Rating', 'Reviews', 'Duration', 'Instructor', 'MainType', 'Subtype']

    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:  # Write header only if file is empty
            writer.writeheader()
        writer.writerows(data)

# List of Udemy categories to scrape
udemy_urls = [
    "https://www.udemy.com/courses/development/web-development/",
"https://www.udemy.com/courses/development/data-science/",
"https://www.udemy.com/courses/development/mobile-apps/",
"https://www.udemy.com/courses/development/programming-languages/",
"https://www.udemy.com/courses/development/game-development/",
"https://www.udemy.com/courses/development/databases/",
"https://www.udemy.com/courses/development/software-testing/",
"https://www.udemy.com/courses/development/software-engineering/",
"https://www.udemy.com/courses/development/development-tools/",
"https://www.udemy.com/courses/development/no-code-development/",
"https://www.udemy.com/courses/business/entrepreneurship/",
"https://www.udemy.com/courses/business/communications/",
"https://www.udemy.com/courses/business/management/",
"https://www.udemy.com/courses/business/sales/",
"https://www.udemy.com/courses/business/strategy/",
"https://www.udemy.com/courses/business/operations/",
"https://www.udemy.com/courses/business/project-management/",
"https://www.udemy.com/courses/business/business-law/",
"https://www.udemy.com/courses/business/analytics-and-intelligence/",
"https://www.udemy.com/courses/business/human-resources/",
"https://www.udemy.com/courses/business/industry/",
"https://www.udemy.com/courses/business/e-commerce/",
"https://www.udemy.com/courses/business/media/",
"https://www.udemy.com/courses/business/real-estate/",
"https://www.udemy.com/courses/business/other-business/",
"https://www.udemy.com/courses/finance-and-accounting/accounting-bookkeeping/",
"https://www.udemy.com/courses/finance-and-accounting/compliance/",
"https://www.udemy.com/courses/finance-and-accounting/cryptocurrency-and-blockchain/",
"https://www.udemy.com/courses/finance-and-accounting/economics/",
"https://www.udemy.com/courses/finance-and-accounting/finance-management/",
"https://www.udemy.com/courses/finance-and-accounting/finance-certification-and-exam-prep/",
"https://www.udemy.com/courses/finance-and-accounting/financial-modeling-and-analysis/",
"https://www.udemy.com/courses/finance-and-accounting/investing-and-trading/",
"https://www.udemy.com/courses/finance-and-accounting/money-management-tools/",
"https://www.udemy.com/courses/finance-and-accounting/taxes/",
"https://www.udemy.com/courses/finance-and-accounting/other-finance-and-accounting/",
"https://www.udemy.com/courses/it-and-software/it-certification/",
"https://www.udemy.com/courses/it-and-software/network-and-security/",
"https://www.udemy.com/courses/it-and-software/hardware/",
"https://www.udemy.com/courses/it-and-software/operating-systems/",
"https://www.udemy.com/courses/it-and-software/other-it-and-software/",
"https://www.udemy.com/courses/office-productivity/microsoft/",
"https://www.udemy.com/courses/office-productivity/apple/",
"https://www.udemy.com/courses/office-productivity/google/",
"https://www.udemy.com/courses/office-productivity/sap/",
"https://www.udemy.com/courses/office-productivity/oracle/",
"https://www.udemy.com/courses/office-productivity/other-productivity/",
"https://www.udemy.com/courses/personal-development/personal-transformation/",
"https://www.udemy.com/courses/personal-development/productivity/",
"https://www.udemy.com/courses/personal-development/leadership/",
"https://www.udemy.com/courses/personal-development/career-development/",
"https://www.udemy.com/courses/personal-development/parenting-and-relationships/",
"https://www.udemy.com/courses/personal-development/happiness/",
"https://www.udemy.com/courses/lifestyle/esoteric-practices/",
"https://www.udemy.com/courses/personal-development/religion-and-spirituality/",
"https://www.udemy.com/courses/personal-development/personal-brand-building/",
"https://www.udemy.com/courses/personal-development/creativity/",
"https://www.udemy.com/courses/personal-development/influence/",
"https://www.udemy.com/courses/personal-development/self-esteem-and-confidence/",
"https://www.udemy.com/courses/personal-development/stress-management/",
"https://www.udemy.com/courses/personal-development/memory/",
"https://www.udemy.com/courses/personal-development/motivation/",
"https://www.udemy.com/courses/personal-development/other-personal-development/",
"https://www.udemy.com/courses/design/web-design/",
"https://www.udemy.com/courses/design/graphic-design-and-illustration/",
"https://www.udemy.com/courses/design/design-tools/",
"https://www.udemy.com/courses/design/user-experience/",
"https://www.udemy.com/courses/design/game-design/",
"https://www.udemy.com/courses/design/3d-and-animation/",
"https://www.udemy.com/courses/design/fashion/",
"https://www.udemy.com/courses/design/architectural-design/",
"https://www.udemy.com/courses/design/interior-design/",
"https://www.udemy.com/courses/design/other-design/",
"https://www.udemy.com/courses/marketing/digital-marketing/",
"https://www.udemy.com/courses/marketing/search-engine-optimization/",
"https://www.udemy.com/courses/marketing/social-media-marketing/",
"https://www.udemy.com/courses/marketing/branding/",
"https://www.udemy.com/courses/marketing/marketing-fundamentals/",
"https://www.udemy.com/courses/marketing/analytics-and-automation/",
"https://www.udemy.com/courses/marketing/public-relations/",
"https://www.udemy.com/courses/marketing/advertising/",
"https://www.udemy.com/courses/marketing/video-and-mobile-marketing/",
"https://www.udemy.com/courses/marketing/content-marketing/",
"https://www.udemy.com/courses/marketing/growth-hacking/",
"https://www.udemy.com/courses/marketing/affiliate-marketing/",
"https://www.udemy.com/courses/marketing/product-marketing/",
"https://www.udemy.com/courses/marketing/other-marketing/",
"https://www.udemy.com/courses/lifestyle/arts-and-crafts/",
"https://www.udemy.com/courses/lifestyle/beauty-and-makeup/",
"https://www.udemy.com/courses/lifestyle/esoteric-practices/",
"https://www.udemy.com/courses/lifestyle/food-and-beverage/",
"https://www.udemy.com/courses/lifestyle/gaming/",
"https://www.udemy.com/courses/lifestyle/home-improvement/",
"https://www.udemy.com/courses/lifestyle/pet-care-and-training/",
"https://www.udemy.com/courses/lifestyle/travel/",
"https://www.udemy.com/courses/lifestyle/other-lifestyle/",
"https://www.udemy.com/courses/photography-and-video/digital-photography/",
"https://www.udemy.com/courses/photography-and-video/photography-fundamentals/",
"https://www.udemy.com/courses/photography-and-video/portraits/",
"https://www.udemy.com/courses/photography-and-video/photography-tools/",
"https://www.udemy.com/courses/photography-and-video/commercial-photography/",
"https://www.udemy.com/courses/photography-and-video/video-design/",
"https://www.udemy.com/courses/photography-and-video/other-photography-and-video/",
"https://www.udemy.com/courses/health-and-fitness/fitness/",
"https://www.udemy.com/courses/health-and-fitness/general-health/",
"https://www.udemy.com/courses/health-and-fitness/sports/",
"https://www.udemy.com/courses/health-and-fitness/nutrition/",
"https://www.udemy.com/courses/health-and-fitness/yoga/",
"https://www.udemy.com/courses/health-and-fitness/mental-health/",
"https://www.udemy.com/courses/health-and-fitness/self-defense/",
"https://www.udemy.com/courses/health-and-fitness/safety-and-first-aid/",
"https://www.udemy.com/courses/health-and-fitness/dance/",
"https://www.udemy.com/courses/health-and-fitness/meditation/",
"https://www.udemy.com/courses/health-and-fitness/other-health-and-fitness/",
"https://www.udemy.com/courses/music/instruments/",
"https://www.udemy.com/courses/music/production/",
"https://www.udemy.com/courses/music/music-fundamentals/",
"https://www.udemy.com/courses/music/vocal/",
"https://www.udemy.com/courses/music/music-techniques/",
"https://www.udemy.com/courses/music/music-software/",
"https://www.udemy.com/courses/music/other-music/",
"https://www.udemy.com/courses/teaching-and-academics/engineering/",
"https://www.udemy.com/courses/teaching-and-academics/humanities/",
"https://www.udemy.com/courses/teaching-and-academics/math/",
"https://www.udemy.com/courses/teaching-and-academics/science/",
"https://www.udemy.com/courses/teaching-and-academics/online-education/",
"https://www.udemy.com/courses/teaching-and-academics/social-science/",
"https://www.udemy.com/courses/teaching-and-academics/language/",
"https://www.udemy.com/courses/teaching-and-academics/teacher-training/",
"https://www.udemy.com/courses/teaching-and-academics/test-prep/",
"https://www.udemy.com/courses/teaching-and-academics/other-teaching-academics/"
]

# Run the scraper in parallel using threading
with ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(scrape_category, udemy_urls)

print("Scraping completed successfully!")
