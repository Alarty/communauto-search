# This is a Python tool script to automate the search of a Communauto near me (Montreal)

It is linked to a Google Sheet, Sendgrid API and run through a Heroku dyno

I imagined it so that it run easily on my Heroku dyno but still can be used locally if needed

# Setup

You need a [Sendgrid](https://sendgrid.com/) (Free) account with a registered email address on it 

You need to set you environment with these variables :
- `communauto_user` : the username to connect to the platform
- `communauto_pwd` : the password to connect to the platform
- `communauto_mailto` : the address who will recieve the emails (or python list of addresses)
- `communauto_from` : the Sendgrid registered sender email

If you run through Heroku, you can use instead : 
- `heroku config:set communauto_user=USER communauto_pwd=PASSWORD communauto_mailto=EMAIL communauto_from=FROM`  
Otherwise you can add them as environment variables in your IDE or your code

There are few files that are needed amongst the code :
- A `communauto-slots.csv` Google Sheet file who keep the user input needs
    - The Google Sheet can be replaced with a CSV called `communauto-slots.csv` file
    - The header should be in both cases : `StartYear,StartMonth,StartDay,StartHour,StartMinute,EndYear,EndMonth,EndDay,EndHour,EndMinute`
    - You have to grant access to you Google API to your file. Follow this tutorial : https://developers.google.com/identity/protocols/oauth2/service-account
    - If you choose to store it in Google Drive, call the sheet `communauto-slots`
- A `gdrive_client_secret.json` only if you use Google Drive of course
    - You can have the file locally, or an environment variable called `gdrive_client_secret` containing the json (for a public usecase on Heroku)
- A `results.json` file will be created and modified to store new results. To compare old/new results and send mail for new ones.
    - If you run locally, everything is fine, if you run on Heroku, you should add an env var `gdrive_results` to 1 so that it create/look for `results` file on Gdrive. 

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


