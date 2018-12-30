import Rhino
import rhinoscriptsyntax as rs
import scriptcontext


def getSegmentId(id):
    return int(rs.GetUserText(id, "SegmentId"))


def translateToGcode(id):

    path = rs.ConvertCurveToPolyline(id)
    points = rs.CurvePoints(path)
    rs.DeleteObject(path)

    for pointId in points:
        print >>f, "G1 X%.3f" % pointId.X, "Y%.3f" % pointId.Y, "Z%.3f" % pointId.Z, "F1200"


def generateToolpath(toolpath):
#    objects = scriptcontext.doc.Objects.FindByLayer(toolpath)
    objects = rs.ObjectsByLayer(toolpath, False)
    if not objects:
        print "No objects found"
        return

    sortedSegments = sorted(objects, key=getSegmentId)

    #Loop between my objects
    for id in sortedSegments:
        print "Segment:", getSegmentId(id)
        translateToGcode(id)


def insertHeader():
    print >>f, """
( File generated with cncproc     )
( format for CNC-STEP controllers )

%
G21 (units set to milimeters)
G90 (use absolute coordinates)
G64 (use path smoothing on)
T1 M6 (change tool)
S16000 M3 (start spindle at full speed)
"""


def insertSafetyStop():
    print >>f, "\nM5 (stop spindle)"



if __name__=="__main__":

    filename = (rs.DocumentName().split("."))[0] + ".gcode"
    print "Generating gcode:", filename

    f = open(filename, 'w')

    insertHeader()

    toolpaths = rs.LayerChildren("Toolpaths")

    for toolpath in toolpaths:
        print toolpath
        generateToolpath(toolpath)


    insertSafetyStop()

    f.close()
