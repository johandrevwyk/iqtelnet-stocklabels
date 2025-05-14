@echo off

set SOURCE_DIR="Z:\IQEnterprise\001\Stock.*"

set DEST_DIR="%CD%\dbsys\"

if not exist %DEST_DIR% (
    echo Creating destination directory: %DEST_DIR%
    mkdir %DEST_DIR%
)

if exist %SOURCE_DIR% (
    echo Copying all Stock files to the %DEST_DIR% directory...
    copy %SOURCE_DIR% %DEST_DIR%
    echo Files copied successfully!
) else (
    echo No Stock files found in the source directory: %SOURCE_DIR%
)

pause
