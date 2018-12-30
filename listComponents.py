import rhinoscriptsyntax as rs

#pick an object
objects = rs.GetObjects("Select components")

#Loop between my objects
for id in objects:
    name = rs.ObjectName(id)
    print "component:", name
    rc = rs.OffsetCurve(id, [0, 0, 0],  10, normal=None, style=1)
