# 

A Python-based project for creating panoramic images from multiple overlapping photographs, developed as part of the **Digital Processing of Images** course at the **Faculty of Computer Science and Engineering, University Ss. Cyril and Methodius**.

**Student**: Klimentina Efremova  
**Index Number**: 235018

## Project Overview

This project implements an automatic panorama stitching algorithm that combines two or more overlapping images into a single, wide panoramic image. The algorithm uses computer vision techniques including feature detection (SIFT), feature matching, homography estimation (RANSAC), and image warping to align and blend images seamlessly.

### Key Features
- Automatic detection of overlapping regions between images
- Feature-based image alignment using SIFT (Scale-Invariant Feature Transform)
- Robust homography estimation with RANSAC for handling outliers
- Support for stitching multiple images in sequence
- Intelligent fallback mechanism when feature matching fails
- Command-line interface for easy batch processing
- Support for both generated test images and real-world photographs

## Requirements

- Python 3.7 or higher
- Windows operating system (for the activation script)
- Basic understanding of command-line operations

## Installation and Setup

1. **Clone or download** the project to your local machine
2. **Install required dependencies**:
          pip install opencv-python numpy matplotlib
  

## How to Use

### 1. Activate the Virtual Environment
Before running any commands, activate the virtual environment:
          .venv\Scripts\Activate.ps1

If you encounter issues with PowerShell, try the Command Prompt version:
          .venv\Scripts\activate.bat

### 2. Available Commands

#### Basic Usage with Individual Images

   # Stitch two specific images
             python main.py image1.jpg image2.jpg --pokazi

  # Stitch three specific images
            python main.py image1.jpg image2.jpg image3.jpg --pokazi

#### Processing Entire Folders
The program can automatically process all images in a folder that follow the naming convention `*_panorama_Part*.jpg`:

  # Process all images in a folder
            python main.py FolderName --folder --pokazi


#### Complete Workflow for Generated Examples

The project includes an `examples` folder with computer-generated test images. To test the algorithm from scratch:

1. **Clean previous results**:
   
             Remove-Item panorama_rezultat.jpg
             Remove-Item examples\*.jpg
   

2. **Regenerate example images**:
     
             python examples\create_example.py
   

4. **Create panorama from examples**:
   
             python main.py examples\slika1.jpg examples\slika2.jpg examples\slika3.jpg --pokazi
   

### 3. Real-World Panorama Examples

The project includes several real-world panorama sets downloaded from the internet. Each set is organized in its own folder with the following structure:


    PanoramaName_Panorama/
    ├── PanoramaName_Panorama_Expected.jpg  # The original downloaded panorama
    ├── PanoramaName_panorama_Part1.jpg     # First segment
    ├── PanoramaName_panorama_Part2.jpg     # Second segment
    └── ...                                 # Additional segments

#### Working with Real Panoramas

1. **Before processing**, remove any previous results:
   
              Remove-Item "PanoramaName_Panorama\PanoramaName_Panorama_Result.jpg"
   
   *(Replace "PanoramaName" with the actual folder name, e.g., "Mountains", "Shanghai", etc.)*

2. **Process the panorama folder**:
  
             python main.py PanoramaName_Panorama --folder --pokazi
   

3. **Compare the result** with the expected panorama (`PanoramaName_Panorama_Expected.jpg`) to evaluate the algorithm's performance.

#### Available Real Panorama Sets
- `Mountains_Panorama/` - 5-part mountain landscape
- `Shanghai_Panorama/` - 2-part cityscape
- `DutchHouses_Panorama/` - 4-part architectural scene

## Algorithm Details

### Technical Implementation

The panorama stitching process follows these key steps:

1. **Feature Detection**: Uses SIFT algorithm to detect keypoints and compute descriptors for each image
2. **Feature Matching**: Matches keypoints between consecutive images using k-nearest neighbors and Lowe's ratio test
3. **Homography Estimation**: Computes perspective transformation (homography) using RANSAC for robustness against outliers
4. **Image Warping**: Applies the homography matrix to warp images into a common coordinate system
5. **Blending and Compositing**: Merges images with intelligent blending at seams

### Intelligent Fallback Mechanism

When the algorithm cannot find sufficient feature matches between images (common with low-texture regions like skies or uniform surfaces), it employs a fallback strategy:
- Attempts matching in reverse order
- If still unsuccessful, uses simple concatenation with gradient blending
- Delays black area filling until all images are processed
- 

## Potential Improvements

While the current implementation produces good results for many scenarios, several enhancements could improve robustness and quality:

1. **Exposure Compensation**: Adjust for brightness and color differences between images
2. **Seam Finding**: Implement optimal seam detection (e.g., graph cuts) for better blending
3. **Bundle Adjustment**: Global optimization of all homographies simultaneously rather than pairwise
4. **GPU Acceleration**: Utilize GPU for faster feature detection and matching
5. **Alternative Feature Detectors**: Support for ORB, AKAZE, or other detectors for different scenarios
6. **Automatic Image Ordering**: Determine correct stitching order without manual input
7. **Lens Distortion Correction**: Account for camera lens distortion before stitching
8. **Multi-Row Stitching**: Support for grid-based panoramas, not just single rows

## Limitations

- Requires images with sufficient texture for feature matching
- Works best with images taken from approximately the same viewpoint (rotational panoramas)
- May struggle with moving objects in overlapping regions
- Performance decreases with very high-resolution images or many sequential images

## Troubleshooting

### Common Issues and Solutions

1. **"No module named 'cv2'" error**: Ensure you've activated the virtual environment and installed dependencies
2. **Memory errors with large images**: The algorithm includes automatic downscaling, but very large panoramas may still cause issues
3. **Poor stitching results**: Ensure images have sufficient overlap (20-40%) and texture
4. **Black lines in output**: This is often due to the fallback mechanism; check that images actually overlap

### Debugging Tips

- Use the `--pokazi` flag to visualize results immediately
- Check the console output for information about detected keypoints and matches
- For difficult panoramas, try processing fewer images at once

## Academic Context

This project was developed for the **Digital Processing of Images** course, demonstrating practical application of computer vision concepts including:
- Image feature extraction and description
- Geometric transformations and homographies
- Robust estimation techniques (RANSAC)
- Image warping and compositing
- Algorithm design with fallback strategies

The implementation balances theoretical correctness with practical robustness, handling real-world challenges like insufficient features, varying image qualities, and memory constraints.

## License and Attribution

This educational project is developed for academic purposes. Real-world panorama images are used under fair use for educational demonstration. Commercial use may require proper attribution and licensing of source images.

## Contact

For questions about this project related to the academic course, please contact the project admin Klimentina Efremova.
---

*Note: This project is intended for educational purposes as part of the Digital Processing of Images course requirements. The algorithm implementation focuses on demonstrating core computer vision concepts rather than production-level robustness.*
