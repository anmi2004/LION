# What can this add-on do?
LION is an add-on that performs automatic Optical Character Recognition (OCR) on specific screen areas at predefined intervals.  

Why is it called "smart"? Not because I developed it, nor because the "i" makes a clever acronym.  

Since it performs repeated OCR scans on the same screen area, it would normally read identical text multiple times - which isn't ideal. To solve this, I implemented a mechanism that prevents speech output when newly recognized text closely matches previous results.

# What can I use it for?
My primary purpose for developing this add-on was subtitle reading. Its working principle enables it to read various types of screen-based subtitles, including those on YouTube, Netflix, Bilibili, embedded subtitles in AVI files, and even live TV captions!  

When using, always set videos to full-screen mode as it mimics human visual perception. Larger text yields better recognition results, though accuracy isn't perfect. For optimal performance:  
- Enlarge subtitle fonts when possible  
- Use high-resolution displays  
The OCR engine isn't flawless and may struggle with certain graphics.  

Beyond subtitles, it can monitor screen text that isn't directly accessible, like video game menus. However, it cannot recognize highlighted text selections.

# How do I use it?
To start with default settings: Press <kbd>NVDA+ALT+N</kbd>. LION will perform full-screen OCR every 1 second and only speak when text changes.  

For customization:  
1. Navigate to <menupath>NVDA menu > Preferences > LION Settings</menupath>  
2. Example use case: Video files might display logos in the top-left corner that get read alongside subtitles. The next section explains solutions.  

**Available settings**:  
1. **OCR Interval**: Frequency of OCR operations (0.1-10 seconds)  
2. **OCR Target**: Screen area to scan (Options: Current Control/Current Window/Navigation Object/Full Screen)  
3. **Crop Pixels (Top/Bottom/Right/Left)**: Trims unwanted areas in Full Screen/Current Window modes. Useful for ignoring persistent logos - e.g., cropping 10% from top removes top-left logos. For efficiency, you might crop 70% from top as subtitles typically occupy the lower third.  

# Changelog
## Version 2.0
1. Complete OCR engine overhaul using PaddleOCR-json for improved accuracy  
2. Implemented add-on template for easier compilation  

## Version 1.15
1. Adapted for NVDA 2022.1 compatibility  
2. Completed interface translations  
3. Added shortcut customization in <menuitem>Input Gestures</menuitem> dialog  
4. Added warnings when initiating OCR during screensaver/black screen  
5. Changed default shortcut to <kbd>NVDA+ALT+N</kbd>  

## Version 1.12
1. Ensured compatibility with NVDA 2021.1  
2. Fixed various bugs  
3. Updated activation/deactivation sounds  

## Version 1.11
Fixed a major YouTube full-screen mode bug  

## Version 1.1
1. Crop settings now affect Current Window mode  
2. Added similarity threshold (0-1) for gaming scenarios:  
   - Compares current text with previous output  
   - 0: All texts considered identical (unusable)  
   - 1: Always speaks (even duplicates)  
   - Default: 0.5  

## Version 1.0
Initial release
