#
# insert block to the top view
#
# A piece of code to practice cloning of blocks to the "stock" ObjectLayer
# so that it is Top cplane, ready for export to 2D DXF for CAM processing
# The script required .3DM file with "stock" and "stock.labels" layers

import Rhino
import rhinoscriptsyntax as rs

class Stock(object):
    """An stock of material that will be used for milling components"""

    Xmax  = 0;

    def __init__(self, layer):
        super (Stock, self).__init__()
        self.layer = layer



class Part(object):
    """A part to be placed on the stock for nesting and cutting purposes"""



    def __init__(self, id, cplane):
        super(Part, self).__init__()
        self.id = id
        self.size_x = 0
        self.size_y = 0
        self.x = 0
        self.y = 0

        # rotate and copy to the Top plane
        initial_plane = rs.ViewCPlane(cplane)
        final_plane = rs.ViewCPlane("Top")
        xform = rs.XformRotation1(initial_plane, final_plane)
        part_id = rs.TransformObjects(id, xform, True)
        rs.SetUserText(part_id, "cplane", "Top")

        # move block to the "stock" layer
        rs.ObjectLayer(part_id, "stock")

        bbox = rs.BoundingBox(part_id)
        rs.MoveObject(part_id, Rhino.Geometry.Point3d(0, 0, 0) - bbox[0])

        # place a label with a block name on the the milling part
        place_label(part_id)

        bbox = rs.BoundingBox(part_id)
        self.size_x = bbox[1][0] - bbox[0][0]
        self.size_y = bbox[2][1] - bbox[0][1]
        self.x = bbox[0][0]
        self.y = bbox[0][1]

        print "size_x = ", self.size_x, " size_y = ", self.size_y
        print "x = ", self.x, " y = ", self.y



#
# place_label (object)
#
# adds a label with a component name to the center of the block
# on the Front cplane
#
def place_label (id):

    # determine component name and bouding box
    object_name = rs.ObjectName(id)
    bbox = rs.BoundingBox(id)

    # calculate center of the parts bounding box
    x = (bbox[1][0] - bbox[0][0]) / 2
    y = (bbox[2][1] - bbox[0][1]) / 2

    text_id = rs.AddTextDot(object_name, (x, y, 0))
    rs.ObjectName(text_id, object_name)
    rs.ObjectLayer(text_id, "labels")

    # make a group of the block and the label
    group_id = rs.AddGroup()
    rs.AddObjectsToGroup((id, text_id), group_id)

    return

def determine_cplane (id):

    cplane = rs.GetUserText(id, "cplane")
    if not cplane:
        cplane = "Front"
        rs.SetUserText(id, "cplane", cplane)

    return


# define a stock to place parts on
panel = Stock("stock")

#pick an objects
objects = rs.GetObjects("Select components", rs.filter.instance, True, True)

rs.EnableRedraw(False)

#Loop between my objects
for id in objects:
    name = rs.ObjectName(id)
    print "component:", name

    # prevent inserting a block that is already in stock layer
    # in future possibly update such block

    # determine plane where the block is constructed
    cplane = determine_cplane(id)

    # move block to the top plane and update its plane property
    part = Part(id, cplane)

    # placement should happen here

    # find out the maximum X of the newly created and moved block
    box = rs.BoundingBox(part.id)
    if box:
        for i, point in enumerate(box):
            if panel.Xmax < point[0]:
                panel.Xmax = point[0]

    print "Xmax = ", panel.Xmax

rs.EnableRedraw(True)
