## PreRelease-6 (March 14, 2024)
This will probably be the last pre-release before v1.0.0, unless any major bugs are found. I will be testing it over a few days to make sure, but this pre-release is essentially the feature-complete version of the program.

### Additions
 - Added a button that shows a diagram of which monitor corresponds to which name
 - Each game's icon is now displayed beside its name in the settings window
 - The program can now be configured to launch at startup in the settings window
 - The default monitor can now be changed in the settings window

### Changes
 - Window can now be resized
 - Small user interface improvements
 - Slightly improve algorithm to determine a game's name

### Fixes
 - Fixed preferred monitor for a game not updating until the program restarted
 - Fixed Light appearance mode not being entirely light
 - Rewrote Tooltip code to fix various issues such as not disappearing
 - Fixed only 2 monitors showing up in window selection dropdowns

## PreRelease-5 (March 11, 2024)

### Additions
 - The primary monitor can now be switch manually from the start tray icon
 - "launch-game" command line argument for games that don't DPI scale properly

### Changes
 - Completed README
 - Enabled automatic DPI awareness so the window scales properly on different DPIs

### Fixes
 - Fixed program not working if not started from the executable's directory

## PreRelease-4 (Feb 25, 2024)

### Additions
 - Delay games from executing to allow Windows to switch the primary display. This should stop quick-loading games from appearing on the wrong monitor.

### Changes
 - Changed from pyinstaller to nuikta to compile the executable. This should stop windows defender from flagging the program as a virus

### Fixes
 - Fixed a bug where the process listener would crash after a game was closed
 - Fixed a bug where when closing some games, the primary monitor would switch back to default then back to the game's preferred monitor.

## PreRelease-3 (Feb 11, 2024)

### Fixes
 - Changed from 'pythoncom' to 'comtypes' library to avoid process listener terminating

## PreRelease-2 (Feb 9, 2024)

### Additions
- Added build.bat file to compile python scripts
- Added CHANGELOG

### Fixes
- Added missing url to download icon so the program doesn't crash