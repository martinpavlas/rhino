import rhinoscriptsyntax as rs


#pick an object
objects = rs.GetObjects("Select Curves", rs.filter.instance)

#Loop between my objects
for id in objects:
    name = rs.ObjectName(id)
    print "Object:", id, name
    new_id = rs.RotateObject(id, [0, 0, 0], 90, [1, 0, 0], 1);
    rs.ObjectName(new_id, "copy " + name)
