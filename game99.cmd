copy refresh99.cmd %HOMEPATH%\Games
python game99.py
if ERRORLEVEL 1 %HOMEPATH%\refresh99.cmd
