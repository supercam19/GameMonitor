# <img src="icon.ico" alt="icon" width="25"> Game Monitor 

Enables you to play fullscreen games on your second monitor.

## Overview
This program works by switching your primary monitor when it detects a game has opened. The preffered monitor for each game has to be manually set up for the program to take effect. 

Note that this program works for Windows only. Additionally, this program is still in beta stages and issues may be encountered, please feel free to report any bugs or feature suggestions in the [issues](https://www.github.com/supercam19/GameMonitor/issues) section.

## Usage
1. Download this program from the [releases page](https://www.github.com/supercam19/GameMonitor/releases/latest) by dropping down the "Assets" section and clicking "GameMonitor.exe".

2. Once downloaded, launch the executable file, and use the "+" button in the top right to add a rule.

3. Once you have added a game, return to the program window, and you will see that game added to the list, use the dropdown menu to the right of the game's name to set the monitor you wish it to launch on.

## Extra Features
Some games will not scale their window properly when using this program to change the monitor they appear on if your two monitors have different screen scaling. The solution is to launch the game through GameMonitor in order to switch your primary monitor before the game starts. To do this, you will run this command when in the GameMonitor executable's directory:<br>
`GameMonitor.exe --launch-game <game_name>`<br>
or<br>
`GameMonitor.exe --launch-game <path_to_game>` <br>
If you use the game name option, it has to match the name of one of the games in your list. Example: <br>
`GameMonitor.exe --launch-game GeometryDash`

### Through Steam
To have this done automatically when launching a game through Steam, navigate to your game and click on "Properties". Find the "Launch Options" textbox and paste in the following, replacing <game> with the game you are launching, and replacing path/to with the actual path to the GameMonitor executable.<br>
`path/to/GameMonitor.exe --launch-game <game>`

### Switching primary monitor
This program also allows you to easily switch your primary monitor by right-clicking the icon in the system tray, and selecting "Set Primary"

## For developers
The build.bat file is provided to build the project from source, but make sure to replace "include-data" argument with your path to the customtkinter library.
