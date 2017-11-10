import Rhino
import rhinoscriptsyntax as rs



#pick an object
objects = rs.GetObjects("Select components", rs.filter.instance)

#Loop between my objects
for id in objects:
    name = rs.ObjectName(id)
    print "component:", name

    # determine plane where the block is constructed
    cplane = rs.GetUserText(id, "cplane")
    if not cplane:
        cplane = "Front"
        rs.SetUserText(id, "cplane", cplane)

    # move block to the top plane and update its plane property
    print "plane:", cplane
    initial_plane = rs.ViewCPlane(cplane)
    final_plane = rs.ViewCPlane("Top")
    xform = rs.XformRotation1(initial_plane, final_plane)
    NewId = rs.TransformObjects(id, xform, True)
    rs.SetUserText(NewId, "cplane", "Top")
    print "remapped"

    # move of block so that the insert point is at origin
    rs.MoveObject(NewId, Rhino.Geometry.Point3d(0, 0, 0) - rs.BlockInstanceInsertPoint(NewId))

    # move block to the "stock" layer
    rs.ObjectLayer(NewId, "stock")
