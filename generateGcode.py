import Rhino
import rhinoscriptsyntax as rs
import scriptcontext

feedrateMove = 6000


def getSegmentId(id):
    segmentId = rs.GetUserText(id, "SegmentId")

    if segmentId:
      return int(segmentId)
    else:
      return


def moveToStartPoint(id):
    pointId = rs.CurveStartPoint(id)
    print >>f, "G1 X%.3f" % pointId.X, "Y%.3f" % pointId.Y, "Z%.3f" % pointId.Z, "F%d" % feedrateMove


def translateToGcode(id):
    path = rs.ConvertCurveToPolyline(id)
    points = rs.CurvePoints(path)
    rs.DeleteObject(path)

    feedrate = int(rs.GetUserText(id, "Feedrate"))

    for pointId in points:
<<<<<<< HEAD
        print >>f, "G1 X%.3f" % pointId.X, "Y%.3f" % pointId.Y, "Z%.3f" % pointId.Z, "F2400"
        rs.AddPoint(pointId)
=======

        print >>f, "G1 X%.3f" % pointId.X, "Y%.3f" % pointId.Y, "Z%.3f" % pointId.Z, "F%d" % feedrate
>>>>>>> 0c6b8369211545784bb7543c66e361bbb45a0741


def generateToolpath(toolpath):
    objects = rs.ObjectsByLayer(toolpath, False)
    if not objects:
        print "No objects found"
        return

    print >>f, "\n( toolpath: %s )\n" % toolpath

    sortedSegments = sorted(objects, key=getSegmentId)

    # move to starting point (first is the TextDot)
    moveToStartPoint(sortedSegments[1])

    #Loop between my objects
    for id in sortedSegments:
        if getSegmentId(id):
            translateToGcode(id)


def insertHeader():
    print >>f, """
( File generated with cncproc     )
( format for CNC-STEP controllers )

%
G21 (units set to milimeters)
G90 (use absolute coordinates)
G64 (use path smoothing on)
(T1 M6) (change tool)
S16000 M3 (start spindle at full speed)
"""


def insertSafetyStop():
    print >>f, "\nM5 (stop spindle)"


def getLayerOrder(layerName):
    return rs.LayerOrder(layerName)


if __name__=="__main__":

    filename = (rs.DocumentName().split("."))[0] + ".gcode"
    print "Generating gcode:", filename

    f = open(filename, 'w')

    insertHeader()

    toolpaths = sorted(rs.LayerChildren("Toolpaths"), key=getLayerOrder)

    for toolpath in toolpaths:
        print toolpath
        generateToolpath(toolpath)


    insertSafetyStop()

    f.close()
