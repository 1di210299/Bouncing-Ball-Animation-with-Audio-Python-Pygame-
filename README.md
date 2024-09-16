# README - Bouncing Ball Animation with Audio (Python & Pygame)

This project contains multiple Python scripts that simulate bouncing balls within a circle, and capture the animation along with sound effects. The generated video includes the movement of the balls, dynamic color changes, and synchronized sound effects upon collisions. 

The project also includes functionality for adding an image as a circular mask in the center of the screen, revealing portions of the image upon ball collisions. The final video is created using the `moviepy` library, which combines the captured frames and audio effects.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Python Script 1: Bouncing Balls with Sound and Video Recording](#python-script-1-bouncing-balls-with-sound-and-video-recording)
3. [Python Script 2: Bouncing Ball with Image Reveal and Music](#python-script-2-bouncing-ball-with-image-reveal-and-music)
4. [How to Run](#how-to-run)
5. [Requirements](#requirements)

---

## Project Overview

This project utilizes `Pygame` for real-time simulation of bouncing balls, with features such as:
- Gravity-affected ball movements.
- Dynamic collision handling between balls and the boundary of a central circle.
- Trail effects that follow the balls.
- Sound effects synchronized with collisions.
- A music track that plays alongside the animation.
- A masked image that reveals progressively as the balls collide with the boundary.

Once the simulation completes, the frames captured during the game are converted into a video using the `moviepy` library, and the collision sounds are added to the video.

---

## Python Script 1: Bouncing Balls with Sound and Video Recording

### Description

This script simulates multiple bouncing balls within a circular boundary. The balls move with velocity, collide with each other, and produce sound effects when they collide. The positions and movement of the balls are recorded as frames, which are later compiled into a video with synchronized sound.

### Key Features:
- **Bouncing Balls**: Balls move within a circular boundary and reflect when they hit the edges.
- **Sound Effects**: A sound effect is played every time the balls collide, with the sound changing for each collision.
- **Video Recording**: The movement of the balls is recorded as individual frames and compiled into an MP4 video with synchronized audio.

### Code Breakdown:
- **Physics Handling**: The script uses basic physics to calculate the velocity of the balls after collision with the boundary or with each other.
- **Sound Effects**: Uses `pygame.mixer` to load and play sound effects for collisions.
- **Video Capture**: Each frame is captured using `pygame.surfarray.array3d()` and stored as an image in a list. After the simulation, these frames are compiled into a video using `moviepy`.

### How to Run:

1. Install the required Python libraries:
    ```bash
    pip install pygame moviepy
    ```

2. Run the script:
    ```bash
    python bouncing_balls_with_audio.py
    ```

### Output:
- A video file named `bouncing_ball_animation_with_audio.mp4` will be created, which shows the animation of bouncing balls along with collision sound effects.

---

## Python Script 2: Bouncing Ball with Image Reveal and Music

### Description

This script enhances the bouncing ball simulation by introducing an image that is progressively revealed as the ball collides with the circle's boundary. The ball's movement and color change dynamically upon collisions. Additionally, the script plays background music, and sound effects are synchronized with ball collisions.

### Key Features:
- **Circular Image Reveal**: A hidden image is gradually revealed as the ball collides with the boundary of the central circle. 
- **Sound Effects**: Plays a sound every time a collision occurs, with the collision point triggering the reveal of part of the image.
- **Music**: Background music is played during the animation.
- **Trail Effects**: Each ball leaves a colorful trail as it moves.

### Code Breakdown:
- **Image Masking**: The script uses a circular mask to gradually reveal a hidden image as collisions occur.
- **Sound Handling**: The sound effect duration is controlled so it plays for a short period upon each collision.
- **Dynamic Animation**: The balls leave trails, and their colors change dynamically with each bounce. 

### How to Run:

1. Install the required Python libraries:
    ```bash
    pip install pygame moviepy numpy
    ```

2. Ensure the paths to the image and audio files are correct in the script. The image should be loaded as a circular mask, and the audio file should be a valid MP3 file.

3. Run the script:
    ```bash
    python bouncing_ball_with_image_reveal_and_music.py
    ```

### Output:
- A video file named `bouncing_ball_animation_with_audio.mp4` will be created. The video will show the bouncing ball revealing parts of the image as it hits the boundaries, with the background music and collision sound effects synchronized with the animation.

---

## How to Run

1. Install Python 3.8+.
2. Install the required libraries by running the following commands:
    ```bash
    pip install pygame moviepy numpy
    ```
3. Update the paths to any image or audio files used in the script.
4. Run the script using:
    ```bash
    python <script_name>.py
    ```
5. Upon completion, the script will generate a video file with the animation and sound effects.

---

## Requirements

### Python Dependencies:
- `Pygame`: Used for handling the graphics, animation, and sound effects.
- `MoviePy`: Used for converting the frames into a video and adding sound effects.
- `Numpy`: Required for managing image arrays and transformations.
- `Colorsys`: Used to generate dynamic colors for the balls and trails.

### External Files:
- **Image**: The image file used for the circular reveal effect.
- **Audio**: Sound files for collision effects and background music.

---

Feel free to modify the scripts to adjust the simulation time, ball speeds, gravity, or the image reveal process. This project is highly customizable for your animation and video creation needs!
