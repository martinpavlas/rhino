import Rhino
import rhinoscriptsyntax as rs
import scriptcontext
import os


filename = (rs.DocumentName().split("."))[0] + ".gcode"

print "Generating gcode:", filename


def getSegmentId(id):
    return rs.ObjectName(id)


def translateToGcode(f, id):
    curveDegree = rs.CurveDegree(id)

    print "curve degree:", curveDegree

    if curveDegree == 1:
        points = rs.CurvePoints(id)

        for pointId in points:
            print >>f, "G1 X%.3f" % pointId.X, "Y%.3f" % pointId.Y, "Z%.3f" % pointId.Z, "F1200"

    else:
        polyline = rs.ConvertCurveToPolyline(id)
        translateToGcode(f, polyline)


def listToolpathSegments():
    objects = scriptcontext.doc.Objects.FindByLayer("toolpaths")
    if not objects: Rhino.Commands.Result.Cancel

    sortedSegments = sorted(objects, key=getSegmentId)

    f = open(filename, 'w')

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

    #Loop between my objects
    for id in sortedSegments:

        if (rs.IsLine(id)):
            translateToGcode(f, id)
        else:
            for id in rs.ExplodeCurves(id):
                translateToGcode(f, id)
                rs.DeleteObject(id)


    print >>f, "\nM5 (stop spindle)"
    f.close();

if __name__=="__main__":
    listToolpathSegments()
