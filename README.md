# This is a Python tool script to automate the search of a Communauto near me (Montreal)

It is linked to a Google Sheet and run through a Heroku dyno : https://communauto-search.herokuapp.com/

I made it so that it run easily on my Heroku dyno but still can be used locally if needed

#Setup 

You need to set you environment with these 3 variables :
- <code>communauto_user</code> : the username to connect to the platform
- <code>communauto_pwd</code> : the password to connect to the platform
- <code>communauto_mailto</code> : the user who will recieve the emails
If you run through Heroku, you can use instead : 
- <code>heroku config:set communauto_user=USER communauto_pwd=PASSWORD communauto_mailto=EMAIL</code>
Otherwise you can add them as environment variables in your IDE/code


There is few files that are needed amongst the code :
- A <code>slots_wanted.csv</code> file who keep the user input needs. I store in Google Sheets for easy modification
    - The Google Sheet can be replaced with a CSV called <code>slots_wanted.csv</code> file
    - The header should be in both cases : <code>StartYear,StartMonth,StartDay,StartHour,StartMinute,EndYear,EndMonth,EndDay,EndHour,EndMinute</code>
    - If you choose to store it in Google Drive, call the sheet <code>communauto-slots</code>, have the Google API credential file called <code>gdrive_client_secret.json</code> in your project folder.
- A <code>gdrive_client_secret.json</code> only if you use Google Drive of course
    - You can have the file, or an environment variable called <code>gdrive_client_secret</code> containing the json (for a public use on Heroku)

# Script phases every X minutes : 
- Loads dates and hours of need from the file (Google Sheet or local csv)
- Connect and login with the credentials from the env variables
- Do the POST form requests for each timeslot
- Scrap available cars number + place + type + km to home
- Compare results with saved results for each timeslot in the json file
- Send email if better change for each timeslot

# TODO : 
- Dynamic form filling depending the webpage shown
- Try to keep session alive to avoid login each time


