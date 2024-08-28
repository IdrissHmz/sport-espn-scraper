#!/bin/bash

# Define the folder containing the files
FOLDER="../sport-espn-scraper"

# Define commit timestamps
DATES=("2024-08-26T13:59:00" "2024-08-28T06:52:00" "2024-08-29T19:15:00" 
       "2024-09-02T04:51:00" "2024-09-05T05:32:00" "2024-09-06T05:07:00" 
       "2024-09-11T02:30:00" "2024-09-12T04:36:00" "2024-10-12T15:57:00" 
       "2024-11-03T22:27:00" "2024-11-04T00:45:00" "2024-11-05T02:30:00" 
       "2024-11-06T04:36:00" "2024-11-06T15:57:00" "2024-11-12T22:27:00")

# Get all files in the folder
FILES=($(ls "$FOLDER"))

# Ensure the number of files matches the number of dates
# if [ ${#FILES[@]} -gt ${#DATES[@]} ]; then
#     echo "Not enough commit timestamps for all files. Add more dates."
#     exit 1
# fi

# Iterate over each file and commit with its name
for i in "${!FILES[@]}"
do
    FILE="${FILES[i]}"
    DATE="${DATES[i]}"
    COMMIT_MSG="Creating ${FILE%.*}"  # Remove file extension for commit message
    git add file.txt
    git add "$FILE"
    GIT_AUTHOR_DATE="$DATE" GIT_COMMITTER_DATE="$DATE" git commit -m "$COMMIT_MSG"


    for j in {1..2}
    do
        DATE="${DATES[i+j]}"
        COMMIT_MSG="Updating ${FILE%.*}"  # Remove file extension for commit message
        git add file.txt
        git add "$FILE"
        GIT_AUTHOR_DATE="$DATE" GIT_COMMITTER_DATE="$DATE" git commit -m "$COMMIT_MSG"
    done
done