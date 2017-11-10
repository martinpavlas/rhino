import rhinoscriptsyntax as rs

#pick an object
objects = rs.GetObjects("Select components", rs.filter.instance)

#Loop between my objects
for id in objects:
    name = rs.ObjectName(id)
    print "component:", name
