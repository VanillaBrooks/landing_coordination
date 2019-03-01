# landing_coordination
Predictive analysis of player landings in PU Battlegrounds 

## Backend
Previous landing information is scraped using the PUBG developer API. The data is then cleaned and stored in various MySQL tables. The landing locations of players are then found based on the player positions in the first two minutes of game time. The categorical data (based on town / geographical area / Map choice) is then fed into a basic neural network using Pytorch.

## Discord

Servers that have added pubg_bot to their server can then query the bot with `?analyze <player in game> <flight path screenshot>.` The number of players in game is applied to the probability that an individual player will be at that specific location.

When a screenshot is sent to the server, the image is first cropped to only include the game map with the current flight path. The flight path is then extracted by locating the alternating colors. The distance from each landing location is calculated and fed into the neural network. The map is then overlayed with the expected number of players that will be landing at that location and exported to discord.
  
## Example usage

Inputs and output images can be found in /needtoprocess and /finished, respectively. 

![Sample input](https://i.imgur.com/v4hdW62.jpg)

![Expected output](https://i.imgur.com/1g9wNRI.jpg)
