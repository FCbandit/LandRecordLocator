import arcpy
import os
import datetime
import re

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
    print("Addded REF_STRIP field for parcel map layer")
    arcpy.management.DeleteField(
        in_table=os.path.join(gdb_path, "Tract_Map"),
        drop_field="LINK",
        method="DELETE_FIELDS"
    )
    # make new field with 100 str
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
if __name__ == "__main__":
    downloadServices()
    prepLayers()
    calcFields()