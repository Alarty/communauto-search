# Python tool script to automate the search of a communauto near me

# Script phases : 
- Choose dates and hours of need in txt file
- Script every X minutes
- Do the POST form requests for each timeslot
- Scrap available cars number + place + type + km to home
- Compare results with saved results for each timeslot in another txt file
- Send email if better change for each timeslot


# Useful URLs

##List Stations
https://www.reservauto.net/Scripts/Ajax/Stations/ListStations.asp

## Local
https://www.reservauto.net/Scripts/client/ReservationDisponibility.asp?CurrentLanguageID=1&IgnoreError=False&StartYear=2020&StartMonth=7&StartDay=6&StartHour=13&StartMinute=0&EndYear=2020&EndMonth=7&EndDay=7&EndHour=13&EndMinute=0&CityID=59&StationID=C&CustomerLocalizationID=&OrderBy=2&Accessories=0&Brand=&ShowGrid=False&ShowMap=False&DestinationID=&FeeType=80

## Longue distance : Québec
https://www.reservauto.net/Scripts/client/ReservationDisponibility.asp?CurrentLanguageID=1&IgnoreError=False&StartYear=2020&StartMonth=7&StartDay=6&StartHour=13&StartMinute=0&EndYear=2020&EndMonth=7&EndDay=7&EndHour=13&EndMinute=0&CityID=59&StationID=C&CustomerLocalizationID=&OrderBy=2&Accessories=0&Brand=&ShowGrid=False&ShowMap=False&DestinationID=1&FeeType=81

## Login form needs : 
{'action': '/account/login', 'method': 'post', 'inputs': [{'type': 'hidden', 'name': 'ReturnUrl', 'value': '/connect/authorize/callback?client_id=CommunautoLegacyCustomerClient&response_type=code%20id_token&scope=openid%20profile%20communautorestapi%20reservautofrontofficerestapi%20offline_access&redirect_uri=https%3A%2F%2Fwww.reservauto.net%2FScripts%2Fclient%2Flogin.aspx&state=6SN4aaRsYprVOxa134jiUKY14cJr3J0iQlJ5JDOZdQ03XQTKITTfIstZX4vyax98F_n9jCfVn7j4yFEzKqlOUU1EnDHdjjJp405VTXL_2td5y8kwaDB4yKcIlwqlhZJAZCZkDYNSOWigGid8wxJZ6YPw7tLkl9MA0wBw8IYLdmPXl-ErzMqUrfM75bQi4ZfNFfP71q7rOJfBaIMzJKfru27d6CVHyjUgkvgjMdM3mLcYDaNzLKQLU7sAkfuM71xu0&nonce=Y37jJuc2Sc5vtQeoJcGfrUFz_wF1S2UqVuGfjUtV4_E&acr_values=tenant%3A1&response_mode=form_post&ui_locales=fr-CA&branch_id=1'}, {'type': 'hidden', 'name': 'ClientId', 'value': 'CommunautoLegacyCustomerClient'}, {'type': 'hidden', 'name': 'BranchId', 'value': 'Communauto_Quebec'}, {'type': 'text', 'name': 'Username', 'value': ''}, {'type': 'password', 'name': 'Password', 'value': ''}, {'type': 'hidden', 'name': 'RecaptchaResponse', 'value': ''}, {'type': 'hidden', 'name': '__RequestVerificationToken', 'value': 'CfDJ8GsX7Bz-zQZHvTh_7ii65-s57PcY7_-8ZvrqboXhfcFdsXvhrHBABzX6pWvVTQ3AdfsFBEnaqe-NPZwnNYBEbC58mbQypfDMylii3KdpSOQlwVo-F7PJnTkpsaEGdYAgGzPOBAclh66mM5_yEZcI8U4'}]}
