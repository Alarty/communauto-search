# Python tool script to automate the search of a communauto near me

You need to set you environment with these 3 variables :
- <code>communauto_user</code> : the username to connect to the platform
- <code>communauto_pwd</code> : the password to connect to the platform
- <code>communauto_mailto</code> : the user who will recieve the emails

If you run through Heroku, you can use : 
- <code>heroku config:set communauto_user=USER communauto_pwd=PASSWORD communauto_mailto=EMAIL</code>
Otherwise you can add these lines at the beginning of the file : 
os.environ['communauto_user'] = USER
os.environ['communauto_pwd'] = PASSWORD
os.environ['communauto_mailto'] = EMAIL

# Script phases : 
- Choose dates and hours of need in txt file
- Script every X minutes
- Do the POST form requests for each timeslot
- Scrap available cars number + place + type + km to home
- Compare results with saved results for each timeslot in another txt file
- Send email if better change for each timeslot

# TODO : 
- Save the book URL for quicker access to booking in mail
- Dynamic form filling depending the webpage shown
- Try to keep session alive to avoid login each time
- Scrap best 5 cars instead of 3

# Useful URLs

##List Stations
https://www.reservauto.net/Scripts/Ajax/Stations/ListStations.asp

