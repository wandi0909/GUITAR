# GUITAR: GUI for Tracking and Analysing flux Ropes

![logo](https://github.com/wandi0909/GUITAR/blob/main/GUITAR_LOGO.png)

The purpose of this tool is to extract and track solar magnetic flux ropes in magnetic field simulation data, based on some input map (2D cuts through a 3D domain) of a suitable proxy (e.g., the twist parameter). It is written in python and thus needs a few non-standard packages to run, being: skimage (0.18.3), pyvista (0.32.1), diplib (3.1.0) and cv2 (4.5.4.60).  The versions in brackets are guaranteed to run, though other (more recent) versions usually run without problems too. For saving animations, installing a software called "imagemagick" is required, but it is not necessary for the GUI to function. The GUI was developed on Windows 11, but was also tested and adjusted to also appear well on MacOS as well as Ubuntu. It may also work well on previous Windows versions and other Linux systems (feedback on that would be appreciated). 

In its current version, the coordinate grid of the input maps has to be uniform (so no unstructured grids, though cartesian is not necessary) and the cuts need to be such that one coordinate is held constant, though implementing the method for oblique angles is on the to-do list. The input shall be provided as .npz or .vtr files, though the former is significantly faster. In either case, all 3 coordinates shall be provided in the input files, with 2 being the full coordinate arrays and 1 of them being an array of size one, indicating the location of the cut. The proxy map shall be given as a 2D array. 

# How to use the GUI:
In the following, the GUI's functionalities and the general usage are outlined. I want to highlight though, that no in-depth discussion about the methodology will be given here, instead, I may refer to the corresponding papers, which discuss this in more detail and using actual simulation data as examples: (https://arxiv.org/abs/2312.00673 [will be replaced with A&A link, once published], [frontiers paper]). 

## Full Extraction Mode
First, a selection window opens, where you can choose in which mode to operate (Full Extraction, Post-Processing, Creating Source Points and Creating Difference Maps). Using the Full Extraction mode, you are asked which file types you want to use. Ideally, you have your data (i.e., the proxy maps) prepared as .npz files. In that case, you are asked to insert the names of your coordinates and your proxies, so that they can be read properly from the npz-archive. If you are using vtr files only, then the coordinate names are not relevant, and only the name of the proxy has to be given. After this you can select your input files via the "Choose Files"-Button, and Load them into the GUI with "Load Files". Following the successfull upload, you are presented with the option to visualize what you uploaded. Note that the spinbox, which indicates the frame number that you are plotting will stay the one and only frame selection for plotting, also for the later processing steps! When the proxy maps are visualized to check if everything is read-in correctly, you can select the polarity of your feature (mostly relevant if you want to use the twist parameter), save the plots (and/or an animation of the plots) or start with the pre-processing of your data for the extraction. The polarity option masks everything below zero to zero if "1" is chosen, or vice versa, masks all pixels to 0 when they are above 0, in case "-1" is selected. 
When you choose to save the plots with the option below the visualization area, first indicate the basename of the files in the textbox (this may also include a full path, like: path/to/myfilename), then hit the save frames or save animation button. You are then presented with a window, which allows you to customize your plots (colormaps, various fontsizes, labels, etc.). Once your selection is done, you can use the "Confirm" button to ultimately save your plots/animation with your selected customization. The filenames in case of plots are the basename, plus the frame-number appended at the end of the given basename. 

Starting the pre-processing with the morphological gradient, you are given two boxes, where you can insert the sizes of the so-called "structuring elements" (short SEs). All SEs used in this GUI are of circular shape, and only the size (i.e., the radius) will be varied. Generally, the morphological gradient acts as a sharpening routine, with tunable parameters (being the SE sizes), where the smaller the size, the less the original image is affected. These sizes are given in pixels, not in physical coordinates and thus, the provided numbers must be integers! Once the calculations are done, they can be visualized with the newly appearing button next to the calculate-button (the same frame selector below the file loading options in the first column is used for this plot). Similarly to before, new saving options appear at the bottom of the first column, in case the processed images should be saved as plots or as an animation. Continuing with the extraction, the processed maps can now be reduced to binary, by applying a suitable threshold, which can be selected below the morphological gradient calculation and visulization. Once a threshold is chosen and applied, the resulting binary mask can be visualized with the "Visualize Mask"-button below. Note that each of these steps can be repeated along with the visualizations, if the result is not satisfactory yet. As a final pre-processing step, some more options are offered, before initializing the tracking (note that these are optional). These are, applying the morphological opening algorithm as well as an additional threshold (either to all frames, or only individual ones). The opening algorithm is there to cut off unwanted sub-features in the reduced binary maps and to reduce noise. This algorithm is again based on comparison with a structuring element, where the bigger the SE size, the stronger the processing. The GUI also offers to input value ranges for the coordinates (they appear as image coordinates x and y, but they generally refer to whatever coordinate appears on the respective axes in the plots), which makes it possible to apply the processing only in certain sub-regions, thus not distorting the whole extracted structure. If an invalid value range is given (like the default x = 0 to 0, y = 0 to 0), then the processing is applied to the whole image. Additionally, a different threshold can be applied, either for sub-regions in one frame, or to a whole frame (again, depending if a valid input is given for the coordinate ranges). The "Visualize Mask" Button is still valid for the processings, so conveniently, each processing step can be checked by visual inspection immediately. Note that the frame selector for the processing and the frame selector for the plotting are not synchronized and have to be adjusted manually! If a processing did not have the desired effect, the "Undo Processing" button makes it possible to undo one step. Note that the goal here is to separate your desired structure from surrounding structures. The surrounding structures do not need to disappear, as they will be excluded by the tracking. 

Once the the pre-processing is satisfactory, the tracking can be initialized. Note that the tracking works backwards in time, thus, one has to select the last frame where the desired structure is still visible in the mask and then hit the "Initialize Tracking" button. Subsequently, you are presented with a spinbox, which lets you choose between 4 different features (indices 0 to 3), which can be visualized with the corersponding button next to it. These are the 4 largest connected features, shown in the last frame the tracking was initialized from. Find your desired feature here and keep the spinbox at this index. Below, you can choose the overlap fraction, which basically is the tracking parameter - the smaller, the smaller the overlap in consecutive frames needs to be, in order to be identified as being the same feature. Upon hitting the "Track" button, the tracking will be done with the chosen parameters (overlap and feature index). Once completed, you can yet again visualize the results to verify for every frame, that the correct feature was tracked throughout (using the same frame selector as for every plot). 

Follwing the tracking, you may (optionally) apply post-processing routines, like the morphological erosion algorithm, or the option to fill the holes in the tracked binary shapes, if there are any. The erosion algorithm works again with comparison of the image features to a structuring element. This processing reduces the binary shape by the SE radius. As before, the processings can be reverted once everytime. The results can be visualized with the "Visualize Processing" button below. The button can also be used as a proceed-button, in case the shapes are already satisfactory. Below, new saving options appear, to save the final binary masks as plots and animations as before, but also as numpy npz-arrays. This is useful as these exact files can be used in the other GUI modes to re-do substeps of the procedure. The coordinates are saved being named "x", "y", "z" and the mask data is named "data", though they correspond to whatever has been given to the program in the initial coordinate name window. Before the arrays, plots, or animations are saved, the correct path and basefilename should be given. 

Finally, to arrive at the source points of the extracted structure for further analysis (e.g., plotting the coresponding 3D magnetic field lines), points inside the extracted shapes are sampled, based on the sampling rate. There are 2 options: uniform sampling, and random sampling. In the case of uniform sampling, the number of points indicated in the sampling size box corresponds to how many grid points are created along the image x direction. The points in image y direction are then calculated, keeping the resulting spacing along x (dx = dy). For the random sampling on the other hand, N^2 random points are created in the image, where N is the number indicated in the sample size box. Subsequently, the program checks for each frame, if the created points lie inside the extracted shape. To save the results, enter the path and basename, after the grid/points are created, into the corresponding appearing textbox. Once the "Get Coordinates" button is used, textfiles are created, containing all 3 coordinates (thus, including the constant one!) of all points that are inside in the extracted shape - with the frame number appended at the end of each filename. 

## Post-Processing Mode
If the post-processing mode is chosen, the previously saved npz-files of the "final" binary maps from the full extraction can be read in here, similarly to before. Upon visualizing the read-in data, you are presented with some post-processing options, analogous to the optional pre- and post-processing sections in the full extraction mode in the second column. Here, again the frame number and sub-image region can be specified for the processings. One can then apply the opening and erosion algorithms with an SE size of choice again for individual or for all frames at a time, as well as fill holes in the provided binary shapes. Note that the sub-image region specification only applies to the erosion and opening, but not to the filling procedure. It is again possible to undo one processing step, if results do not turn out as expected. After at least one processing has been applied, you are offered the option to visualize the results with the "Visualize Processing" button below the processing options section. The visualization frames are controlled by the frame selector in the first column, similar to what has been the case in the full extraction mode. 

If necessary (e.g., because some sub-features have been cut-off with the opening algorithm), the tracking can be done again, analogous to the tracking procedure in the full extraction mode (here termed "Re-tracking"). This means again choosing the last frame where the desired structure appears in the binary map for initialization and then choose the index of this structure in the "choose shape" spinbox. Finally, the overlap fraction has to be specified again and then the tracking can be done with the corresponding "Track" button. In the case that no re-tracking is necessary, or the tracking has been completed, one can proceed with the "Proceed" button. This then opens again the possibilities to save the resulting masks as npz arrays, plots or animations, where plots and animations come with the same customization options as before. Finally, the resulting source points can be saved, also completely analogous to the full extraction mode.

## Source Point Retrieval Mode
This mode only contains the very last step of both of the aforementioned modes and saves the troubles of going through the whole procedure again, if one is only interested in resampling the data points. As in the post-processing mode, the previously saved arrays (from either of the two modes, as well as from the difference map mode) can be loaded here. Subsequently, they can be resampled by selecting the sample size, which corresponds to the number of points along the image x direction for uniform sampling (the points in y are then created automatically by the prescription dx = dy), while for the random sampling, the given number N will yield N^2 randomly sampled points in the image. Textfiles can then be saved again, containing those points that lie inside the read-in binary shapes for each corresponding frame. 

## Difference Map Mode
In this mode, difference maps of previous extractions can be created (using the saved npz files from the first two modes), which can be useful to visualize the difference between two different processings. Two masks can be read-in here, where the difference map is created as Mask 1 - Mask 2. Logically, both masks need to have the exact same sizes. After the difference map is created with the corresponding button, it can be visualized. Following its visualization, below the plots, the output can be saved as arrays, plots and animations, as in the first two modes. Finally, the source points for this difference maps can also be created, completely analogous to all aforementioned modes. Note: here only one textbox appears to save the coordinates, where whatever button has been used last to create the grid/random points will be used for the sampling (uniform or random). As a final note here: With the option to save the output as npz file again, the resulting maps can yet again be read into both the post-processing and source point retrieval mode! One application of this is disentangling different sub-features of solar flux ropes, as shown in our example in the frontiers paper! 
