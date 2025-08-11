# Nablazy

Video Download Application

## Overview

Nablazy is a web application that allows you to download videos from YouTube, X (formerly Twitter), and TikTok to your local environment.  
It runs within Docker containers, ensuring safe usage without polluting your host environment.

## Main Features

- **Video Download**: Download videos from YouTube, X (Twitter), and TikTok
- **Audio Conversion**: Extract audio (mp3) from videos

## System Requirements

- Docker & Docker Compose
- Web Browser

## Installation & Setup

1. **Start the Application**
   ```sh
   docker compose up -d
   ```

2. **Access the Web Interface**
   
   Open your browser and navigate to `http://localhost:8080`.

3. **Stop the Application**
   ```sh
   docker compose down
   ```

## Usage

1. Access the download page in your browser
2. Enter the video URL (YouTube, X/Twitter, or TikTok)
3. Select the save format (video or audio)
4. Click the download button
5. The browser's download dialog will appear, and the file will be saved locally.

## File Formats

- **Video Download**: Extension depends on the original video format
- **Audio Download**: Saved in mp3 format
