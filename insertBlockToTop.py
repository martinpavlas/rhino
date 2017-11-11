#
# insert block to the top view
#
# A piece of code to practice cloning of blocks to the "stock" ObjectLayer
# so that it is Top cplane, ready for export to 2D DXF for CAM processing
# The script required .3DM file with "stock" and "stock.labels" layers

import Rhino
import rhinoscriptsyntax as rs

#
# place_label (object)
#
# adds a label with a block name to the center of the block on the Front cplane
#
def place_label (id):

    # determine component name and bouding box
    object_name = rs.ObjectName(id)
    bbox = rs.BoundingBox(id)

    # calculate center of the parts bounding box
    x = (bbox[1][0] - bbox[0][0]) / 2
    y = (bbox[2][1] - bbox[0][1]) / 2
    print "XXX>", x, y
    text_id = rs.AddTextDot(object_name, (Xmax + x + 10, y, 0))
    rs.ObjectName(text_id, object_name)

    # make a group of the block and the label
    group_id = rs.AddGroup()
    rs.AddObjectsToGroup((id, text_id), group_id)

    return




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

    # place a label with a block name on the the milling part
    place_label(NewId)

    # find out the maximum X of the newly created and moved block
    box = rs.BoundingBox(NewId)
    if box:
        for i, point in enumerate(box):
            if Xmax < point[0]:
                Xmax = point[0]

    print "Xmax = ", Xmax
