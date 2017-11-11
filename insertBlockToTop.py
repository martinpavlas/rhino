#
# insert block to the top view
#
# A piece of code to practice cloning of blocks to the "stock" ObjectLayer
# so that it is Top cplane, ready for export to 2D DXF for CAM processing
# The script required .3DM file with "stock" and "stock.labels" layers

import Rhino
import rhinoscriptsyntax as rs

# set active layer to "stock", ie. layer where the nesting will take place
rs.CurrentLayer("labels")

#pick an object
objects = rs.GetObjects("Select components", rs.filter.instance, True, True)

Xmax  = 0;

#Loop between my objects
for id in objects:
    name = rs.ObjectName(id)
    print "component:", name

    # prevent inserting a block that is already in stock layer
    # in future possibly update such block

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

    # move of block so that the insert point is at max X of previous
    # object plus 10 units
    box = rs.BoundingBox(NewId)
    rs.MoveObject(NewId, Rhino.Geometry.Point3d(Xmax + 10, 0, 0) - box[0])

    # move block to the "stock" layer
    rs.ObjectLayer(NewId, "stock")

    # place the label with an object name onto the nesting block
    labelX = (box[1][0] - box[0][0]) / 2
    labelY = (box[2][1] - box[0][1]) / 2
    print "XXX>", labelX, labelY
    TextId = rs.AddTextDot(name, (Xmax + labelX + 10, labelY, 0))
    rs.ObjectName(TextId, name)

    # make a group of the block and the label
    groupId = rs.AddGroup()
    rs.AddObjectsToGroup((NewId, TextId), groupId)

    # find out the maximum X of the newly created and moved block
    box = rs.BoundingBox(NewId)
    if box:
        for i, point in enumerate(box):
            if Xmax < point[0]:
                Xmax = point[0]

    print "Xmax = ", Xmax
