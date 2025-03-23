# List of courses to search
course_list = ["Machine Learning", "Data Science", "Python Programming", "Power BI"]

# Udemy base search URL
base_url = "https://www.udemy.com/courses/search/?q="

# Generate URLs
search_urls = [base_url + course.replace(" ", "%20") for course in course_list]

# Save URLs to a text file
with open("udemy_search_urls.txt", "w") as file:
    for url in search_urls:
        file.write(url + "\n")

# Print generated URLs
for url in search_urls:
    print(url)

print("\nAll URLs have been saved in 'udemy_search_urls.txt'.")
