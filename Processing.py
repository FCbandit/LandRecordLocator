import arcpy
import os
import datetime

arcpy.env.overwriteOutput = True

#Folder Location
main_folder = r"P:\mppub\MAPSVCS\STAFF_WORKING\DHAN\APRX\Canyon_Fire\FirePerimeter_EvacZones"

# REST service URLs
rest_services = {
    "Fire_Perimeters": "https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/ArcGIS/rest/services/CA_Perimeters_NIFC_FIRIS_public_view/FeatureServer/0",
    "Evac_Zones": "https://services.arcgis.com/RmCCgQtiZLDCtblq/arcgis/rest/services/Public_Emergency_Map_GENASYS_Alert_Warning_Area/FeatureServer/0"
}

#Create date/timed folder
timestamp = datetime.datetime.now().strftime("%Y%d%m_%H%M")
output_folder = os.path.join(main_folder, timestamp)
os.makedirs(output_folder, exist_ok=True)
print(f"Created folder: {output_folder}")

#Create FGDB
gdb_name = "FireData.gdb"
gdb_path = os.path.join(output_folder, gdb_name)
arcpy.CreateFileGDB_management(output_folder, gdb_name)
print(f"Created GDB: {gdb_path}")

#Download services
for fc_name, url in rest_services.items():
    output_fc = os.path.join(gdb_path, fc_name)
    print(f"Downloading {fc_name} from {url}...")
    arcpy.conversion.FeatureClassToFeatureClass(url, gdb_path, fc_name)
    print(f"Saved: {output_fc}")

print("Done.")