import Rhino
import rhinoscriptsyntax as rs
from math import atan2, pi, asin

def DecomposeXformRotation(arrXform):
    arrRotate = Rhino.Geometry.Point3d.Unset
    arrRotate.X = atan2(- arrXform.M21, arrXform.M22)
    arrRotate.Y = asin(arrXform.M20)
    arrRotate.Z = atan2(arrXform.M10, arrXform.M00)
    return arrRotate


#pick an object
objects = rs.GetObjects("Select Curves", rs.filter.instance)

#Loop between my objects
for id in objects:
    name = rs.ObjectName(id)
    print "Object:", id, name
    r = DecomposeXformRotation(rs.BlockInstanceXform(id))
    v = round( r[0] * -180/pi, 0) + 0
    if v < 0: v += 360

    print "v = %.2f" % v

#    new_id = rs.RotateObject(id, [0, 0, 0], 90, [1, 0, 0], 1);
#    rs.ObjectName(new_id, "copy " + name)
