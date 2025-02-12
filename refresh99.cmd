cls
@echo Refreshing all files.  Please wait.
CD %HOMEPATH%
RMDIR /Q /S %USERPROFILE%\Games\Backup\GameOf99.bak
XCOPY %USERPROFILE%\Games\GameOf99 %USERPROFILE%\Games\Backup\GameOf99.bak /B /I /W
XCOPY %USERPROFILE%\Games\Source\GameOf99 %USERPROFILE%\Games\GameOf99 /B /I /W
CD %HOMEPATH%\Games\GameOf99
cls
@echo Finished refreshing files.  Press any key to proceed to game.
pause
Game99.cmd