# This is a Python tool script to automate the search of a Communauto near me (Montreal)

It is linked to a Google Sheet, Sendgrid API and run through a Heroku dyno

I imagined it so that it run easily on my Heroku dyno but still can be used locally if needed

#Setup 
You need a Sendgrid (Free) account with a registered email address on it 

You need to set you environment with these variables :
- <code>communauto_user</code> : the username to connect to the platform
- <code>communauto_pwd</code> : the password to connect to the platform
- <code>communauto_mailto</code> : the address who will recieve the emails (or python list of addresses)
- <code>communauto_from</code> : the Sendgrid registered sender email

If you run through Heroku, you can use instead : 
- <code>heroku config:set communauto_user=USER communauto_pwd=PASSWORD communauto_mailto=EMAIL communauto_from=FROM</code>
Otherwise you can add them as environment variables in your IDE or your code

There is few files that are needed amongst the code :
- A <code>communauto-slots.csv</code> Google Sheet file who keep the user input needs
    - The Google Sheet can be replaced with a CSV called <code>communauto-slots.csv</code> file
    - The header should be in both cases : <code>StartYear,StartMonth,StartDay,StartHour,StartMinute,EndYear,EndMonth,EndDay,EndHour,EndMinute</code>
    - You have to grant access to you Google API to your file. Follow this tutorial : https://developers.google.com/identity/protocols/oauth2/service-account
    - If you choose to store it in Google Drive, call the sheet <code>communauto-slots</code>
- A <code>gdrive_client_secret.json</code> only if you use Google Drive of course
    - You can have the file locally, or an environment variable called <code>gdrive_client_secret</code> containing the json (for a public usecase on Heroku)
- A <code>results.json</code> file will be created and modified to store new results. To compare old/new results and send mail for new ones.
    - If you run locally, everything is fine, it you run on Heroku, you should add a env var <code>gdrive_results</code> to 1 so that it create/look for <code>results</code> file on Gdrive. 

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


