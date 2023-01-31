# AutoMat
AutoMat is a plugin for Maya which creates __PBR-Material-Setups__ automatically from a selected texture folder.
__It's currently only working for Arnolds aiStandardSurface-Shader__

## Installation
[video guide](https://youtu.be/YQhrmUSLaAw)

text guide
1. Download .zip from [releases](https://github.com/philnewm/autoMat/releases/latest)
2. Extract .zip and rename to __autoMat__ if neccessary, folder name is important
3. copy plugin folder
   + on Windows copy the __autoMat__ folder into the Documents folder:
   `C:\<username>\Documents\maya\2022\scripts\`
   + on Linux copy the __autoMat__ folder into the users home directory:
   `/home/<username>/maya/2022/scripts/`
4. open Mayas script editor ans switch to a python tab
5. paste this code into the python tab
   ```python
   from autoMat.src import ui
   ui.AutoMatUI(dock=True)
   ```
6. highlight it and middle mouse drag into one of your shelves
7. click the newly created button and the UI should open up

## How to use
video guide

text guide
1. Setup one folder per material
2. select a material folder or group multiple material folders into one folder
3. choose your settings for displacement and projection
4. let it setup the materials for you, this may take some time, especially the first time

## Features
+ support for aiStandardSurface-Shader
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
