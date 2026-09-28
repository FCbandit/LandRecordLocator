import arcpy
import os
import datetime
import re
from arcgis.gis import GIS
import zipfile
import gc, time

arcpy.env.overwriteOutput = True

#Folder Location
main_folder = r"P:\mppub\MAPSVCS\SPECIAL_PROJECTS\Land_Records_Feature_Locator\downloaded_services"
gdb_name = "LandRecords.gdb"
gdb_path = os.path.join(main_folder, gdb_name)

def downloadServices():
    # REST service URLs
    rest_services = {
        "Parcel_Map": "https://dpw.gis.lacounty.gov/dpw/rest/services/landrecords/MapServer/1",
        "Tract_Map": "https://dpw.gis.lacounty.gov/dpw/rest/services/landrecords/MapServer/2",
        "RecordOfSurvey": "https://dpw.gis.lacounty.gov/dpw/rest/services/landrecords/MapServer/0"
    }

    #Create FGDB
    if not os.path.exists(gdb_path):
        arcpy.CreateFileGDB_management(main_folder, gdb_name)
        print(f"Created GDB: {gdb_path}")

    #Download services
    for fc_name, url in rest_services.items():
        output_fc = os.path.join(gdb_path, fc_name)
        print(f"Downloading {fc_name} from {url}...")
        arcpy.conversion.FeatureClassToFeatureClass(url, gdb_path, fc_name)
        print(f"Saved: {output_fc}")

    print("Done.")

def prepLayers():
    #Delete existing link field within parcel map layer
    arcpy.management.DeleteField(
        in_table=os.path.join(gdb_path,"Parcel_Map"),
        drop_field="LINK",
        method="DELETE_FIELDS"
    )
    #make new field with 100 str
    arcpy.management.AddField(
        in_table=os.path.join(gdb_path,"Parcel_Map"),
        field_name="LINK",
        field_type="TEXT",
        field_precision=None,
        field_scale=None,
        field_length=100,
        field_alias="Link",
        field_is_nullable="NULLABLE",
        field_is_required="NON_REQUIRED",
        field_domain=""
    )
    print("Generated Link field for parcel map layer")
    arcpy.management.AddField(
        in_table=os.path.join(gdb_path,"Parcel_Map"),
        field_name="REF_STRIP",
        field_type="TEXT",
        field_precision=None,
        field_scale=None,
        field_length=75,
        field_alias="REF_STRIP",
        field_is_nullable="NULLABLE",
        field_is_required="NON_REQUIRED",
        field_domain=""
    )
    print("Added REF_STRIP field for parcel map layer")
    #Repair tract map geometry
    arcpy.management.RepairGeometry(
        in_features=os.path.join(gdb_path, "Tract_Map"),
        delete_null="KEEP_NULL",
        validation_method="ESRI"
    )
    arcpy.management.DeleteField(
        in_table=os.path.join(gdb_path, "Tract_Map"),
        drop_field="LINK",
        method="DELETE_FIELDS"
    )
    # make new link field
    arcpy.management.AddField(
        in_table=os.path.join(gdb_path, "Tract_Map"),
        field_name="LINK",
        field_type="TEXT",
        field_precision=None,
        field_scale=None,
        field_length=100,
        field_alias="Link",
        field_is_nullable="NULLABLE",
        field_is_required="NON_REQUIRED",
        field_domain=""
    )
    arcpy.management.AddField(
        in_table=os.path.join(gdb_path, "Tract_Map"),
        field_name="REF_MB",
        field_type="TEXT",
        field_precision=None,
        field_scale=None,
        field_length=75,
        field_alias="",
        field_is_nullable="NULLABLE",
        field_is_required="NON_REQUIRED",
        field_domain=""
    )
    arcpy.management.AddField(
        in_table=os.path.join(gdb_path, "Tract_Map"),
        field_name="REF_STRIP",
        field_type="TEXT",
        field_precision=None,
        field_scale=None,
        field_length=75,
        field_alias="",
        field_is_nullable="NULLABLE",
        field_is_required="NON_REQUIRED",
        field_domain=""
    )
    print("Generated Link field for tract map layer")
    arcpy.management.AddField(
        in_table=os.path.join(gdb_path, "Tract_Map"),
        field_name="REF_MB_STRIP",
        field_type="TEXT",
        field_precision=None,
        field_scale=None,
        field_length=None,
        field_alias="",
        field_is_nullable="NULLABLE",
        field_is_required="NON_REQUIRED",
        field_domain=""
    )
    arcpy.management.AddField(
        in_table=os.path.join(gdb_path, "RecordOfSurvey"),
        field_name="LINK",
        field_type="TEXT",
        field_precision=None,
        field_scale=None,
        field_length=100,
        field_alias="Link",
        field_is_nullable="NULLABLE",
        field_is_required="NON_REQUIRED",
        field_domain=""
    )
    print("Generated Link field for record of survey layer")
    arcpy.management.AddField(
        in_table=os.path.join(gdb_path, "RecordOfSurvey"),
        field_name="RS_BOOKPAGE",
        field_type="TEXT",
        field_precision=None,
        field_scale=None,
        field_length=10,
        field_alias="",
        field_is_nullable="NULLABLE",
        field_is_required="NON_REQUIRED",
        field_domain=""
    )
    arcpy.management.AddField(
        in_table=os.path.join(gdb_path, "RecordOfSurvey"),
        field_name="RS_STRIP",
        field_type="TEXT",
        field_precision=None,
        field_scale=None,
        field_length=10,
        field_alias="",
        field_is_nullable="NULLABLE",
        field_is_required="NON_REQUIRED",
        field_domain=""
    )

def calcFields():
    #calculate field
    arcpy.management.CalculateField(
        in_table=os.path.join(gdb_path,"Parcel_Map"),
        field="LINK",
        expression='"https://pw.lacounty.gov/sur/nas/landrecords/parcel/" + !REFERENCE!.split("-")[0] + "/" + !REFERENCE! + ".pdf"',
        expression_type="PYTHON3",
        code_block="",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
    )
    arcpy.management.CalculateField(
        in_table=os.path.join(gdb_path, "Parcel_Map"),
        field="REF_STRIP",
        expression=r"re.sub(r'(^|\D)0+(?=\d)', r'\1', !REFERENCE!)",
        expression_type="PYTHON3",
        code_block="import re",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
    )
    print("Calculated ref strip field")
    print("Calculated fields for parcel map layer.")
    arcpy.management.CalculateField(
        in_table=os.path.join(gdb_path,"Tract_Map"),
        field="LINK",
        expression='"https://pw.lacounty.gov/sur/nas/landrecords/tract/" + !REFERENCE!.split("-")[0].replace("TR","MB") + "/" + !REFERENCE! + ".pdf"',
        expression_type="PYTHON3",
        code_block="",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
    )
    arcpy.management.CalculateField(
        in_table=os.path.join(gdb_path,"Tract_Map"),
        field="REF_MB",
        expression='!REFERENCE!.replace("TR","MB")',
        expression_type="PYTHON3",
        code_block="",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
    )
    arcpy.management.CalculateField(
        in_table=os.path.join(gdb_path, "Tract_Map"),
        field="REF_STRIP",
        expression=r"re.sub(r'(^|\D)0+(?=\d)', r'\1', !REFERENCE!)",
        expression_type="PYTHON3",
        code_block="import re",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
    )

    arcpy.management.CalculateField(
        in_table=os.path.join(gdb_path, "Tract_Map"),
        field="REF_MB_STRIP",
        expression=r"re.sub(r'(^|\D)0+(?=\d)', r'\1', !REFERENCE!)",
        expression_type="PYTHON3",
        code_block="import re",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
    )
    arcpy.management.CalculateField(
        in_table=os.path.join(gdb_path, "Tract_Map"),
        field="REF_MB_STRIP",
        expression='!REF_MB_STRIP!.replace("TR","MB")',
        expression_type="PYTHON3",
        code_block="",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
    )
    arcpy.management.CalculateField(
        in_table=os.path.join(gdb_path,"RecordOfSurvey"),
        field="LINK",
        expression='"https://pw.lacounty.gov/sur/nas/landrecords/survey/RS" + !BOOK_PAGE!.split("-")[0] + "/RS" + !BOOK_PAGE! + ".pdf"',
        expression_type="PYTHON3",
        code_block="",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
    )
    arcpy.management.CalculateField(
        in_table=os.path.join(gdb_path,"RecordOfSurvey"),
        field="RS_BOOKPAGE",
        expression='"RS" + !BOOK_PAGE!',
        expression_type="PYTHON3",
        code_block="",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
    )
    arcpy.management.CalculateField(
        in_table=os.path.join(gdb_path, "RecordOfSurvey"),
        field="RS_STRIP",
        expression=r"re.sub(r'(^|\D)0+(?=\d)', r'\1', !RS_BOOKPAGE!)",
        expression_type="PYTHON3",
        code_block="import re",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
    )

def refreshData():
    Service_item_ID = "29b9ab882bea41d7bdd4590eb843f9b2"

    GDB_path = r"P:\mppub\MAPSVCS\SPECIAL_PROJECTS\Land_Records_Feature_Locator\downloaded_services\LandRecords.gdb"
    ZIP_path = r"P:\mppub\MAPSVCS\SPECIAL_PROJECTS\Land_Records_Feature_Locator\downloaded_services\Zipped_Exports\LandRecords.gdb.zip"

    #source layer and agol layer mapping
    LAYER_MAP = {
        "RecordOfSurvey": "RecordOfSurvey",
        "Parcel_Map": "Parcel_Map",
        "Tract_Map": "Tract_Map"
    }
    #Sign into AGOL
    gis = GIS("home")
    print("Signed in as:", gis.users.me.username)
    #Confirm item name
    svc_item = gis.content.get(Service_item_ID)
    print("Service:", svc_item.title)

    #Clear any locks
    arcpy.ClearWorkspaceCache_management()
    gc.collect()
    time.sleep(2)

    #Zip up source GDB
    if os.path.exists(ZIP_path):
        os.remove(ZIP_path)

    with zipfile.ZipFile(ZIP_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(GDB_path):
            for f in files:
                full_path = os.path.join(root, f)
                arcname = os.path.relpath(full_path, os.path.dirname(GDB_path))
                zipf.write(full_path, arcname)

    print("Zipped FGDB:", ZIP_path)

    #Upload temp FGDB onto AGOL
    root_folder = gis.content.folders.get()  # root

    src_item = root_folder.add(
        item_properties={
            "title": "LandRecords_fgdb_upload",
            "type": "File Geodatabase"
        },
        file=ZIP_path
    ).result()

    print("Uploaded source item:", src_item.id)

    #Truncate and append each layer
    for lyr in svc_item.layers:
        layer_name = lyr.properties.name

        if layer_name not in LAYER_MAP:
            print(f"Skipping layer not in map: {layer_name}")
            continue

        fc_name = LAYER_MAP[layer_name]
        print(f"\nUpdating layer: {layer_name}")

        #Delete existing features
        del_result = lyr.delete_features(where="1=1")
        print("  Deleted features")

        #Append from FGDB
        append_result = lyr.append(
            item_id=src_item.id,
            upload_format="filegdb",
            source_table_name=fc_name,
            upsert=False
        )
        print("  Appended:", append_result)

    #Remove temp source item in AGOL
    src_item.delete()

    print("Data refresh complete.")

if __name__ == "__main__":
    start_time = time.time()

    downloadServices()
    prepLayers()
    calcFields()
    refreshData()

    elapsed = time.time() - start_time
    print(f"\nTotal runtime: {elapsed / 60:.2f} minutes ({elapsed:.1f} seconds)")