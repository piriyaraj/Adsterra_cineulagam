@echo off
REM Docker Hub deployment script for Cineulagam Publisher (Windows)
REM Make sure you're logged in to Docker Hub: docker login

REM Configuration
set DOCKER_USERNAME=piriyaraj1998
set IMAGE_NAME=cineulagam-publisher
set TAG=latest
set FULL_IMAGE_NAME=%DOCKER_USERNAME%/%IMAGE_NAME%:%TAG%

echo Building Docker image: %FULL_IMAGE_NAME%

REM Build the image
docker build -t %FULL_IMAGE_NAME% .

if %errorlevel% equ 0 (
    echo Build successful! Pushing to Docker Hub...
    
    REM Push to Docker Hub
    docker push %FULL_IMAGE_NAME%
    
    if %errorlevel% equ 0 (
        echo Successfully pushed %FULL_IMAGE_NAME% to Docker Hub!
        echo You can now pull and run with:
        echo docker run -p 5000:5000 %FULL_IMAGE_NAME%
    ) else (
        echo Failed to push to Docker Hub. Make sure you're logged in with 'docker login'
        exit /b 1
    )
) else (
    echo Build failed!
    exit /b 1
)
