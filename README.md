# Algorithm for Making Panoramic Images (Horizontal & Vertical)

A Python-based project for creating **horizontal and vertical panoramic images** from multiple overlapping photographs.  
This project was developed as part of the **Digital Processing of Images** course at the  
**Faculty of Computer Science and Engineering, University “Ss. Cyril and Methodius” – Skopje**.

**Student**: Klimentina Efremova  
**Index Number**: 235018

---

## Project Overview

This project implements an **automatic panorama stitching algorithm** capable of creating:

- **Horizontal panoramas** (classic left-to-right panoramas)
- **Vertical panoramas** (top-to-bottom panoramas)
- **Automatic direction detection** based on image content

The algorithm combines two or more overlapping images into a single panoramic image using
modern computer vision techniques such as **SIFT feature detection**, **feature matching**,  
**homography estimation (RANSAC)**, and **image warping**.

The system is designed to work with both:
- **Computer-generated test images**
- **Real-world panorama image sets**

---

## Key Features

- Automatic detection of overlapping regions
- **Automatic panorama direction detection** (horizontal / vertical)
- Manual direction override (`--smer horizontal | vertical`)
- Feature-based alignment using **SIFT**
- Robust homography estimation using **RANSAC**
- Intelligent fallback when feature matching fails
- Support for stitching **multiple images in sequence**
- Folder-based batch processing
- Command-line interface (CLI)
- Works with generated examples and real-life panoramas

---


---

## Requirements

- Python **3.7+**
- OpenCV (`opencv-python`)
- NumPy
- Windows / Linux / macOS

---

## Installation & Setup

1. **Enter the main directory**

        cd PanoramicPic_Algorithm

2. **Create and activate a virtual environment**

        python -m venv .venv

    For Windows (PowerShell):

        .venv\Scripts\Activate.ps1

    For Windows (Command Line):

        .venv\Scripts\activate.bat

    For Linux\macOS :

        source .venv\bin\activate


3. **Install dependencies**
        
        pip install opencv-python numpy

----
## How to use
### Basic usage (with Induvidual Images)

#### Default panorama 
The algorithm decides by itself weather it'll do horizontal or vertical panorama based on the image overlapping:

        python main.py image1.jpg image2.jpg image3.jpg

#### Horizontal panorama

        python main.py image1.jpg image2.jpg image3.jpg --smer horizontal --pokazi

#### Vertical panorama

        python main.py image1.jpg image2.jpg image3.jpg --smer vertical --pokazi


### Folder-Based Processing

The program can process entire folders automatically.

Image files must follow the naming convention:

        *_panorama_Part1.jpg
        *_panorama_Part2.jpg
        *_panorama_Part3.jpg
        ...

#### Processing a folder

        python main.py Folder_Name --folder --pokazi

#### Forced horizontal stitching

        python main.py Coast_Panorama --folder --smer horizontal --pokazi

#### Forced vertical stitching

        python main.py Coast_Panorama --folder --smer vertical --pokazi

---
### Panorama with computer generated images

First we generate the images with:
        
        python examples\create_example.py

Then we run the algorithm for horizontal panorama:

        python main.py examples/slika1.jpg examples/slika2.jpg examples/slika3.jpg --pokazi

Or the algorithm for vertical panorama:

        python main.py examples/slika4.jpg examples/slika5.jpg examples/slika6.jpg --pokazi

---
### Panorama with real life images

We order the images in a folder like this:

        PanoramaName_Panorama/
        ├── PanoramaName_Panorama_Expected.jpg
        ├── PanoramaName_panorama_Part1.jpg
        ├── PanoramaName_panorama_Part2.jpg
        └── ...

#### **Already availabe real-life panorama sets:**

    * Shangai_Panorama   // horizontal panorama
    * DutchHouses_Panorama  // horizontal panorama
    * Mountains_Panorama  // horizontal panorama
    * Coast_Panorama   // vertical panorama
    * TokyoArchitecture_Panorama  // vertical panorama

We can just process them with a command like this:

        python main.py DutchHouses_Panorama --folder --pokazi

-----

## Algorithm Description

### Main Steps

The panorama stitching algorithm follows a multi-stage pipeline designed to handle both **horizontal** and **vertical** panoramas in a robust and flexible way.

1. **Feature Detection**  
   Each image is processed using the **SIFT (Scale-Invariant Feature Transform)** algorithm to detect distinctive keypoints and compute descriptors that are invariant to scale and rotation.

2. **Feature Matching**  
   Feature descriptors between consecutive images are matched using a **Brute-Force Matcher** with *k-nearest neighbors*. Lowe’s ratio test is applied to filter out weak or ambiguous matches.

3. **Automatic Direction Detection**  
   When the stitching direction is set to `auto`, the algorithm:
    - Analyzes the relative displacement of matched keypoints
    - Compares horizontal (`dx`) and vertical (`dy`) movement
    - Falls back to image aspect ratio (portrait vs landscape) if needed  
      Based on this analysis, the panorama is classified as **horizontal** or **vertical**.

4. **Overlap Verification**  
   The algorithm estimates whether two images overlap sufficiently by analyzing the number and distribution of feature matches. This prevents invalid homography calculations when images do not share enough common content.

5. **Homography Estimation (RANSAC)**  
   If sufficient overlap exists, a **homography matrix** is computed using the **RANSAC** algorithm, allowing robust alignment even in the presence of outliers.

6. **Image Warping and Alignment**  
   One image is warped into the coordinate system of the other using the computed homography. The images are then merged into a single canvas.

7. **Fallback Strategy (No Overlap Case)**  
   If overlap is insufficient or homography estimation fails:
    - The images are concatenated directly
    - For vertical panoramas, the algorithm determines whether the new image should be placed **above or below** the existing panorama

8. **Iterative Stitching**  
   For more than two images, the panorama is built incrementally by stitching each new image onto the current panorama result.

9. **Black Border Cropping**  
   After stitching is complete, black borders introduced by perspective warping are automatically detected and removed.

---

## Vertical Panorama Handling

Unlike traditional panorama algorithms that assume horizontal motion, this implementation includes explicit support for **vertical panoramas**:

- Automatic detection of vertical overlap
- Analysis of keypoint displacement along the Y-axis
- Intelligent decision whether a new image belongs on the **top** or **bottom**
- Proper handling of portrait-oriented images

This makes the algorithm suitable for tall structures, architecture, towers, and stacked landscape shots.

---

## Limitations

- Requires sufficient texture for reliable feature matching
- Performance degrades with:
    - Low-texture regions (sky, water, walls)
    - Significant moving objects
- Best suited for images taken from approximately the same viewpoint
- Not optimized for very large image sets or ultra-high resolutions
- No exposure or color correction is applied

---

## Potential Improvements

Future enhancements could include:

1. Exposure and color compensation between images
2. Seam optimization using graph cuts or energy minimization
3. Global bundle adjustment instead of pairwise homographies
4. GPU acceleration for feature detection and matching
5. Support for alternative feature detectors (ORB, AKAZE)
6. Automatic image ordering
7. Lens distortion correction
8. Multi-row and grid-based panoramas

---

## References and Image Sources

The real-world panorama images used for testing and demonstration purposes were obtained from publicly available online resources intended for creative and educational use:

- **Flickr – Panoramas Group**  
  https://www.flickr.com/groups/panoramas/pool/

- **Freepik – Free Photos & Vectors**  
  https://www.freepik.com/free-photos-vectors/

All images are used strictly for **educational and non-commercial purposes**, in accordance with fair use guidelines. Proper credit belongs to the original authors.

---

## Academic Context

This project was developed as part of the **Digital Processing of Images** course and demonstrates practical application of:

- Feature extraction and description
- Robust estimation techniques (RANSAC)
- Geometric transformations and homographies
- Image warping and compositing
- Algorithm design with intelligent fallback strategies

The focus is on clarity, correctness, and educational value rather than production-level optimization.

---

## License and Disclaimer

This project is intended **solely for educational purposes**.  
Commercial use of the code or images may require additional permissions from the respective image authors.

---

## Contact

For academic questions related to this project:

**Klimentina Efremova**  
Faculty of Computer Science and Engineering  
University “Ss. Cyril and Methodius” – Skopje
