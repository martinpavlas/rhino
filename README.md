# RhinoCNC for CNCStep

*this project is far from being finished. It can be used at own risk and
I do not take any responsibility for any damage or any injury. Please use
it only if you fully understand what it does or as an inspiration for your
own work. I strongly encourage to run all GCODE in simulator prior to running on the CNC router*

I am a happy user of CNC Step Router mill High-Z S-1400/T-105, unfortunately
as a MacOS X user I was rather unhappy with using ConstruCAM for preparing
GCODE CAM files.

At some point I have decided to use Voxelizer software in combination with a simple post-processor, see [cncproc](https://github.com/martinpavlas/cncstep-tools)

However, even the Voxelizer did not suit my needs. Eventually, as a Rhino3D user, I have decided to write a few Rhino extensions that would fulfil my needs and generate GCODE directly from Rhino.

## GCODE generation

The process of GCODE generation is split into two separate steps:
- creating toolpaths
- generating GCODEs for toolpaths

### Generating toolpaths

`toolpathContour.py` is a script that generates toolpaths for milling inside/outside contours. The script can be run with `runPythonScript` command in Rhino. The script collets information about the path and then generates toolpaths to a separate Toolpaths layer.

### Generating GCODE

When all toolpaths are generated, `generateGcode.py` script can be run to generate GCODE file that can be dirrectly sent to the CNC Step CNC routers.

to be continued...
