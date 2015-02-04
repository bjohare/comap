var Layers = {};

Layers.OSM = new OpenLayers.Layer.OSM("OpenStreetMap");

// http://www.thunderforest.com/opencyclemap/
Layers.OCM = new OpenLayers.Layer.OSM("OpenCycleMap",
                ["http://a.tile.opencyclemap.org/cycle/${z}/${x}/${y}.png",
                 "http://b.tile.opencyclemap.org/cycle/${z}/${x}/${y}.png",
                 "http://c.tile.opencyclemap.org/cycle/${z}/${x}/${y}.png"]
            );

// http://www.thunderforest.com/landscape/
Layers.LANDSCAPE = new OpenLayers.Layer.OSM("OSM Landscape",
                ["http://a.tile.thunderforest.com/landscape/${z}/${x}/${y}.png",
                 "http://b.tile.thunderforest.com/landscape/${z}/${x}/${y}.png",
                 "http://c.tile.thunderforest.com/landscape/${z}/${x}/${y}.png"]
            );

// http://www.thunderforest.com/outdoors/
Layers.OUTDOORS = new OpenLayers.Layer.OSM("OSM Outdoors",
                ["http://a.tile.thunderforest.com/outdoors/${z}/${x}/${y}.png",
                 "http://b.tile.thunderforest.com/outdoors/${z}/${x}/${y}.png",
                 "http://c.tile.thunderforest.com/outdoors/${z}/${x}/${y}.png"]
            );
/*
Layers.GOOGLE_SATELLITE = new OpenLayers.Layer.Google("Google Satellite",
            {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22}                                          
            );
*/
Layers.STAMEN_WATERCOLOR = new OpenLayers.Layer.OSM("Stamen Watercolor",
                ["http://tile.stamen.com/watercolor/${z}/${x}/${y}.png",]
            );