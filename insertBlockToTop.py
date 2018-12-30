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

    def __init__(self, layer):
        super (Stock, self).__init__()
        self.layer = layer


class Part(object):
    """A part to be placed on the stock for nesting and cutting purposes"""

    def __init__(self, id):
        super(Part, self).__init__()

        # rotate and copy to the Top plane
        bbox = rs.BoundingBox(id)
        initial_plane = rs.PlaneFitFromPoints(bbox)
        final_plane = rs.ViewCPlane("Top")
        xform = rs.XformRotation1(initial_plane, final_plane)
        self.id = rs.TransformObjects(id, xform, True)

        # place part to the "stock" layer
        rs.ObjectLayer(self.id, "stock")

        # mode part to the Origin
        bbox = rs.BoundingBox(self.id)
        rs.MoveObject(self.id, Rhino.Geometry.Point3d(Xmax, 0, 0) - bbox[0])

        # place a label with a block name on the part
        self.place_label()

        # determine size and location
        bbox = rs.BoundingBox(self.id)
        self.size_x = bbox[1][0] - bbox[0][0]
        self.size_y = bbox[2][1] - bbox[0][1]
        self.x = bbox[0][0]
        self.y = bbox[0][1]


    def place_label (self):

        # determine component name and bouding box
        object_name = rs.ObjectName(self.id)
        bbox = rs.BoundingBox(self.id)

        # calculate center of the parts bounding box
        x = bbox[0][0] + (bbox[1][0] - bbox[0][0]) / 2
        y = bbox[0][1] + (bbox[2][1] - bbox[0][1]) / 2

        text_id = rs.AddTextDot(object_name, (x, y, 0))
        rs.ObjectName(text_id, object_name)
        rs.ObjectLayer(text_id, "labels")

        # make a group of the block and the label
        group_id = rs.AddGroup()
        rs.AddObjectsToGroup((self.id, text_id), group_id)


#
# Main
#
Xmax = float(rs.GetDocumentData("Nest", "Xmax"))
Xmax = 0

# define a stock to place parts on
panel = Stock("stock")

#pick an objects
objects = rs.GetObjects("Select components", rs.filter.instance, True, True)

rs.EnableRedraw(False)

#Loop between my objects
for id in objects:
    name = rs.ObjectName(id)


    # move block to the top plane and update its plane property
    part = Part(id)

    # calculate position for next part
    Xmax = part.x + part.size_x
    rs.SetDocumentData( "Nest", "Xmax", str(Xmax))

    print "part: ", name, " @ X = ", part.x

rs.EnableRedraw(True)
