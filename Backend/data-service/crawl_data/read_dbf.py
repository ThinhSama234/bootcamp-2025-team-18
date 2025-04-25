import geopandas as gpd
import json

# Đọc toàn bộ shapefile (geopandas sẽ tự nhận file .shp + .dbf + .shx...)
gdf = gpd.read_file("crawl_data/dbf_data/vnm_pplp_2015_OSM.shp", encoding="cp1252")

results = []
for _, row in gdf.iterrows():
    geom = row.geometry
    if geom and geom.geom_type == "Point":  # chỉ lấy địa điểm có toạ độ điểm
        results.append({
            "name": row.get("PPLP_NAME", "Unknown"),
            "category": row.get("PPLP_TYPE", "place"),
            "coordinates": [geom.x, geom.y],
            "type": "location",
            "admin_level_1": row.get("ADM1_NAME", ""),
            "admin_level_2": row.get("ADM2_NAME", ""),
            "admin_level_3": row.get("ADM3_NAME", "")
        })
# Lưu JSON
with open("locations_from_shapefile.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
# In tổng số địa điểm trích được
print(f"Tổng cộng {len(results)} địa điểm đã được lưu.")