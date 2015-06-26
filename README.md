# Cricket Score Indicator
Displays live scores from ESPN website in your indicator panel

## Motivation
After being fed up with opening the ESPN Cricinfo website for checking the scores while working I along with my friend wrote the script for this appindicator.

## Working
Uses the unofficial JSON from [ESPN Website](http://www.espncricinfo.com/) to get the summary and scorecard for currently active matches.

## Screenshots
Shows the live scores in panel

![](./screenshots/panel_image.png "Label gets updated with latest score")

Menu displays the current matches from the ESPN Cricinfo website.
![](./screenshots/mainmenu_image.png "Listing all the matches")

The icon in the menu and indicator displays the run scored on the last delivery.
If match is finished (won) it will show a trophy icon.

Submenu shows scorecard 
![](./screenshots/submenu_image.png "Click 'Set as label' to display the scores from this match as the label text in panel")


If the match has not been started, then submenu will show the information regarding that match
![](./screenshots/submenu_info.png "The submenu showing information regarding the match that hasnt been started")
