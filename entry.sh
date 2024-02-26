#!/bin/bash

# Define the folder containing the files
FOLDER="./scrapers"

# Define commit timestamps and messages
DATES=("2024-02-26T13:59:00" "2024-03-28T06:52:00" "2024-04-02T19:15:00" "2024-04-02T20:37:00" "2024-04-02T23:36:00"
       "2024-04-20T04:51:00" "2024-04-20T05:32:00" "2024-05-30T05:07:00" "2024-06-10T17:45:00" "2024-06-29T14:53:00"
       "2024-06-30T02:30:00" "2024-06-30T04:36:00" "2024-07-03T15:57:00" "2024-07-03T22:27:00" "2024-07-04T00:45:00"
       "2024-08-12T03:18:00" "2024-08-12T04:23:00" "2024-08-12T17:27:00" "2024-08-20T21:01:00" "2024-09-30T11:46:00"
       "2024-10-01T05:24:00" "2024-11-01T14:53:00" "2024-11-30T04:24:00" "2024-12-24T22:53:00")

MESSAGES=("Initializing web scraper" "Adding proxy support" "Implementing headless browsing"
          "Optimizing request headers" "Parsing HTML content"
          "Extracting data using BeautifulSoup" "Adding pagination support" 
          "Enhancing logging for debugging" "Storing scraped data in MongoDB"
          "Exporting scraped data to CSV" "Improving scraper efficiency"
          "Adding error handling for failed requests")

# Iterate over each commit date and message
((i=1))
for DATE in "${DATES[@]}"
do
  echo "Commit on ${DATE}" > file.txt
  git add file.txt
  GIT_AUTHOR_DATE="${DATE}" GIT_COMMITTER_DATE="${DATE}" git commit -m "${MESSAGES[i]}"
  ((i++))
done