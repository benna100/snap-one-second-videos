# 📸 One Second Video Snapchat Compilation 🎬

Automatically create a beautiful video compilation from your Snapchat Memories. This script takes a 1.4-second snippet from one video per day, in chronological order, and stitches them together into a single memorable movie.

![Snapchat Compilation Banner](https://placehold.co/800x200/FFFC00/000000?text=Snapchat+Compilation+Magic!&font=montserrat)

## 🚀 Getting Started

Follow these steps to get your Snapchat compilation video generated.

### Prerequisites

This project relies on Python and `ffmpeg`. Here’s how to set them up:

#### 1. Installing Python 🐍

If you don't have Python installed, it's best to get the latest stable version. You can find instructions on how to download and install Python for your operating system on the [official Python website](https://www.python.org/downloads/). Please ensure you install Python 3.

#### 2. Installing `ffmpeg` 🎞️

`ffmpeg` is a powerful command-line tool for manipulating video and audio, which this script uses for all video processing tasks.

You can find download and installation instructions for `ffmpeg` on the [official ffmpeg website](https://ffmpeg.org/download.html). Make sure `ffmpeg` and `ffprobe` are added to your system's PATH.

### Project Setup

1.  **Clone or Download this Repository:**

    ```bash
    git clone https://github.com/benna100/snap-one-second-videos
    cd one-second-video-snapchat
    ```

2. **Export your Snapchat Memories**
Go to [accounts.snapchat.com](https://accounts.snapchat.com). Click `My Data`. Make sure to include the memories. Click `Submit`

3.  **Place Your Snapchat Videos:**
    - Copy all your Snapchat video files into the `videos` folder. They should have this format: `YYYY-MM-DD_some_unique_id-main.mp4`.

    Your project structure should look like this:

    ```
    one-second-video-snapchat/
    ├── videos/
    │   ├── 2023-01-15_xxxx-main.mp4
    │   ├── 2023-01-16_yyyy-main.mp4
    │   └── ... (all your other videos)
    ├── video_compiler.py
    └── README.md
    ```

### 🎬 Running the Script

1.  Open your Terminal or Command Prompt and navigate to the projects folder
2.  Run the script:
    ```bash
    python video_compiler.py
    # If that does not work, then try this
    python3 video_compiler.py
    ```
3. When done the video will be called `snap-one-second-videos.mp4`

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/yourusername/one-second-video-snapchat/issues) (replace with your actual repo URL if you host it on GitHub).

## 📜 License

This project is open source. Feel free to use, modify, and distribute. If you create something cool, a shoutout would be appreciated!

---

Made by https://benna100.github.io/portfolio/
