# AutoMat
AutoMat is a plugin for Maya which creates __PBR-Material-Setups__ automatically from a selected texture folder.

## Installation
Here is a video guide

And the same as text
1. Download .zip from releases
2. Extract .zip and rename to __autoMat__ 
3. copy plugin folder
   + on Windows copy the __autoMat__ folder into the Documents Folder: `C:\<username>\Documents\maya\2022\scripts\`
   + on Linux copy the __autoMat__ folder into the users home directory: `/home/<username>/maya/2022/scripts/`
4. open Mayas script editor ans switch to a python tab
5. paste this code into the python tab
   ```python
   from autoMat.src import ui
   ui.AutoMatUI(dock=True)
   ```
6. highlight it and middle mouse drag into one of your shelves
7. click the created button and the UI should open up


## Features
+ support for aiStandardSurfaceShader
+ settings for colorspace selection 
+ setup material for triplanar projection
+ options for triplanar projection and displacement

## Planned features
+ custom option for colorspace defaults
+ additional settings regarding the file search like custom naming convention
+ selection for other Render Engines (Vray and Redshift are planned)

## Known limitations
+ currently no support for following aiStandartSurface inputs
   + Subsurface color
   + Subsurface Radius
   + Coat color
   + Coat roughness
   + Sheen color
   + Sheen roughness

## Developed and tested using
+ OS: Fedora 35
+ Maya Version: 2022.4
+ Arnold Version: MtoA 5.2.0 (Arnold Core 7.1.3.0) 
