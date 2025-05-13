from data_interface import MongoDB

uri = "mongodb+srv://truongthinh2301:tpuNNUBTBxrgOm1a@cluster0.dlrf4cw.mongodb.net/"
db = MongoDB(uri, database="travel_db", collection="place")

db.collection.insert_many([
    {
        "name": "Central Park",
        "location": {"type": "Point", "coordinates": [-73.97, 40.77]},
        "category": "Parks"
    },
    {
        "name": "Sara D. Roosevelt Park",
        "location": {"type": "Point", "coordinates": [-73.9928, 40.7193]},
        "category": "Parks"
    },
    {
        "name": "Polo Grounds",
        "location": {"type": "Point", "coordinates": [-73.9375, 40.8303]},
        "category": "Stadiums"
    }
])
#db.collection.create_index([("location", "2dsphere")])

record = db.collection.find({
    "location": {
        "$near": {
            "$geometry": { "type": "Point", "coordinates": [-73.9667, 40.78] },
            "$minDistance": 1000,
            "$maxDistance": 5000
        }
    }
})
print(record[0])

record = db.collection.aggregate([
   {
      "$geoNear": {
         "near": { "type": "Point", "coordinates": [ -73.9667, 40.78 ] },
         "spherical": True,
         "query": { "category": "Parks" },
         "distanceField": "calcDistance"
      }
   }
])
record = list(record)
print(record[0])
# {
#    location: {
#       type: "Point",
#       coordinates: [-73.856077, 40.848447]
#    },
#    name: "Morris Park Bake Shop"
# }

# db.places.aggregate( [
#    {
#       $geoNear: {
#          near: { type: "Point", coordinates: [ -73.9667, 40.78 ] },
#          spherical: true,
#          query: { category: "Parks" },
#          distanceField: "calcDistance"
#       }
#    }
# ] )

# db.places.insertMany( [
#    {
#       name: "Central Park",
#       location: { type: "Point", coordinates: [ -73.97, 40.77 ] },
#       category: "Parks"
#    },
#    {
#       name: "Sara D. Roosevelt Park",
#       location: { type: "Point", coordinates: [ -73.9928, 40.7193 ] },
#       category: "Parks"
#    },
#    {
#       name: "Polo Grounds",
#       location: { type: "Point", coordinates: [ -73.9375, 40.8303 ] },
#       category: "Stadiums"
#    }
# ] )

# db.neighborhoods.findOne({ geometry: { $geoIntersects: { $geometry: { type: "Point", coordinates: [ -73.93414657, 40.82302903 ] } } } })

# { type: "Point", coordinates: [ 40, 5 ] }
