@echo off
echo Copying to Anki addons...
copy /Y anki_mc_quiz\__init__.py "%APPDATA%\Anki2\addons21\anki_mc_quiz\__init__.py"
echo Done! Restart Anki to apply changes.
pause