# Python tool script to automate the search of a communauto near me

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

