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