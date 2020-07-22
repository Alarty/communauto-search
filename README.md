# This is a Python tool script to automate the search of a communauto near me
## It is linked to a Google Sheet and run through a Heroku dyno : https://communauto-search.herokuapp.com/

The Google Sheet can be replaced with a CSV called <code>slots_wanted.csv</code> file with this header :
<code>StartYear,StartMonth,StartDay,StartHour,StartMinute,EndYear,EndMonth,EndDay,EndHour,EndMinute</code>

If you choose to store it in Google Drive, call the sheet <code>communauto-slots</code>, have the Google API credential file called <code>gdrive_client_secret.json</code> in your project folder.

You need to set you environment with these 3 variables :
- <code>communauto_user</code> : the username to connect to the platform
- <code>communauto_pwd</code> : the password to connect to the platform
- <code>communauto_mailto</code> : the user who will recieve the emails

If you run through Heroku, you can use instead : 
- <code>heroku config:set communauto_user=USER communauto_pwd=PASSWORD communauto_mailto=EMAIL</code>

Otherwise you can add them as environment variables in your IDE/code

# Script phases : 
- Choose dates and hours of need in txt file
- Script every X minutes
- Do the POST form requests for each timeslot
- Scrap available cars number + place + type + km to home
- Compare results with saved results for each timeslot in another txt file
- Send email if better change for each timeslot

# TODO : 
- Dynamic form filling depending the webpage shown
- Try to keep session alive to avoid login each time

# Useful URLs

##List Stations
https://www.reservauto.net/Scripts/Ajax/Stations/ListStations.asp

