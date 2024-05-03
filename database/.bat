@echo off
setlocal enabledelayedexpansion

rem Set the directory where the images are located
set "directory=C:\Users\anson\Documents\GitHub\SCU_ML\SCU_MSIS2653-GenAI\Project\fashion_assist\database\Givenchy\bottom"

rem Set the starting index
set "index=1"

rem Loop through the files in the directory
for %%F in ("%directory%\*.png") do (
    rem Get the current file name without extension
    set "filename=%%~nF"

    rem Add leading zero if index is less than 10
    if !index! lss 10 (
        set "newname=0!index!.png"
    ) else (
        set "newname=!index!.png"
    )

    rem Rename the file to the new name
    ren "%%F" "!newname!"

    rem Increment the index for the next file
    set /a "index+=1"
)

echo Files renamed successfully.
