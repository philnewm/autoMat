# AutoMat
AutoMat is a plugin for Maya which creates __PBR-Material-Setups__ automatically from a selected texture folder.

## Features
+ support for aiStandardSurfaceShader
+ settings for __colorspace__ selection 
+ setup material for __Triplanar Projection__
+ options for triplanar projection and displacement

## Planned features
+ custom option for colorspace defaults
+ additional settings regarding the file search
+ selection for other Render Engines (Vray and Redshift are planned)

## Installation
1. copy plugin folder
   + on Windows copy the __autoMat__ folder into `C:\<username>\Documents\maya\2022\scripts\`
   + on Linux copy the __autoMat__ folder into `/home/<username>/maya/2022/scripts/`
2. paste this code into Mayas script editor
   ```python
   from autoMat.src import ui
   ui.AutoMatUI(dock=True)
   ```
3. mark it and middle mouse drag into one of your shelves
4. click the created button and the UI should open up

## Developed and tested using
+ OS: Fedora 35
+ Maya Version: 2022.4
+ Arnold Version: MtoA 5.2.0 (Arnold Core 7.1.3.0) 
