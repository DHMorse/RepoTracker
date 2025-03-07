@echo off
REM filepath: .\run.bat
SETLOCAL EnableDelayedExpansion

REM Display header
echo ====================================
echo Running the application...
echo ====================================

REM Check if environment file exists and load it
if exist .env (
    echo Loading environment variables...
    for /F "tokens=*" %%i in (.env) do set %%i
)

REM Check for build directory, create if it doesn't exist
if not exist build\ (
    echo Creating build directory...
    mkdir build
)

REM Build the application (adjust based on your actual build process)
echo Building application...
if exist pom.xml (
    call mvn clean package
) else if exist package.json (
    call npm install
    call npm run build
) else if exist CMakeLists.txt (
    cd build
    cmake ..
    cmake --build .
    cd ..
)

REM Run tests if applicable
echo Running tests...
if exist pom.xml (
    call mvn test
) else if exist package.json (
    call npm test
) else if exist CMakeLists.txt (
    cd build
    ctest
    cd ..
)

REM Execute the application (adjust based on your actual run command)
echo Starting application...
if exist build\app.exe (
    build\app.exe %*
) else if exist target\app.jar (
    java -jar target\app.jar %*
) else if exist dist\index.js (
    node dist\index.js %*
)

echo ====================================
echo Done!
echo ====================================

ENDLOCAL