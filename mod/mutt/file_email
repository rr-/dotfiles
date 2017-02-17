#!/usr/bin/env bash
# Save piped email to "$1/YYMMDD SUBJECT.eml"

# Don't overwrite existing file
set -o noclobber

message=$(cat)

mail_date=$(<<<"$message" grep -oPm 1 '^Date: ?\K.*')
formatted_date=$(date -d"$mail_date" +%y%m%d)
# Get the first line of the subject, and change / to ∕ so it's not a subdirectory
subject=$(<<<"$message" grep -oPm 1 '^Subject: ?\K.*' | sed 's,/,∕,g')

if [[ $formatted_date == '' ]]; then
  echo Error: no date parsed
  exit 1
elif [[ $subject == '' ]]; then
  echo Warning: no subject found
fi

echo "${message}" > "$1/$formatted_date $subject.eml" && echo Email saved to "$1/$formatted_date $subject.eml"
