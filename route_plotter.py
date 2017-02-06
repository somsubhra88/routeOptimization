#Author : Abhijeet Phatak
import os
import csv
# from tkinter import *
from collections import defaultdict

legend_x  = ['black','dark blue','green','sky blue','yellow','gold','pink','red','orange','pale green','maroon','navy','brown']
legend_y = ['"#000000"','"#0000FF"','"#008000"','"#00BFFF"','"#FFFF00"','"#FFD700"','"#FF1493"','"#FF0000"','"#FF4500"','"#98FB98"','"#800000"','"#000080"','"#8B4513"']

wd = os.getcwd()
try:
    os.remove(wd + "\\route_plotter.html")
except:
    pass
filename = wd + "\\route_plotter.html"
f = open(filename,'a')

#center_x = input("Enter lattitude for map center :")
center_x = 12.8852659
#center_y = input("Enter longitude for map center :")
center_y = 77.6533668
#zoom = input("Enter level of zoom :")
zoom = 12

sub1 = """<!DOCTYPE html>
<html>
<head>
<title>Route Optimization Visualization</title>

<meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
<style type="text/css">
html { height: 100% }
body { height: 100%; margin: 0; padding: 0 }
#map_canvas { height: 100% }
</style>
<script type="text/javascript" src="http://maps.googleapis.com/maps/api/js"></script>

<script>
"""

print("Enter the file you need to visualize")
#root = Tk()
#root.withdraw()
file_path = "D:\\SomSubhra\\Route Optimization\\Detail Path - Best Cost Output.csv"

final_matrix = []
csvfile = open(file_path,'r')
print("Analyzing..." + filename)

reader = csv.reader(csvfile, delimiter=',')
next(reader, None)
for row in reader:
    final_matrix += [row]

num_of_vans = int(max(final_matrix[-1][0]))
print("Number of vans used "+str(num_of_vans))

print("Writing the code for plotter...")
sub2 = """function initialize() {
        var homeLatlng = new google.maps.LatLng(%s,%s);
        var myOptions = {
            zoom: %s,
            center: homeLatlng,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
""" %(center_x,center_y,zoom)

coords = []
coord_dict = defaultdict(list)
for i in range(len(final_matrix)):
    coord_dict[int(final_matrix[i][0])].append("new google.maps.LatLng"+str((float(final_matrix[i][5]),float(final_matrix[i][6]))))

submain = ''

for j in range(num_of_vans):
    arrcoords = "[\n" + ',\n\t\t\t'.join(item for item in coord_dict[j+1]) + "\n]"
    color = legend_y[j]
    submain += """var arrCoords%s = %s;

    var route%s = new google.maps.Polyline({
    path: arrCoords%s,
    strokeColor: %s,
    strokeOpacity: 1.0,
    strokeWeight: 4,
    geodesic: false,
    map: map
    });

    """ %(j,str(arrcoords),j,j,color)

sub3 = """
\t\t;
\t}
google.maps.event.addDomListener(window, 'load', initialize);
</script>
</head>
<body>
  <div id="map_canvas"></div>
</body>
</html>"""


f.write(sub1)
f.write(sub2)
f.write(submain)
f.write(sub3)
f.close()
csvfile.close()

for i in range(num_of_vans):
    print("Route for van "+str(i+1)+" is shown by " + str(legend_x[i]) + " color.")

#os.system("pause")
