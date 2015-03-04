var Layers = {};

Layers.OSM = new OpenLayers.Layer.OSM("OpenStreetMap");

// http://www.thunderforest.com/opencyclemap/
Layers.OCM = new OpenLayers.Layer.OSM("OpenCycleMap",
                ["http://a.tile.opencyclemap.org/cycle/${z}/${x}/${y}.png",
                 "http://b.tile.opencyclemap.org/cycle/${z}/${x}/${y}.png",
                 "http://c.tile.opencyclemap.org/cycle/${z}/${x}/${y}.png"],
                {crossOriginKeyword: null}
            );

// http://www.thunderforest.com/landscape/
Layers.LANDSCAPE = new OpenLayers.Layer.OSM("OSM Landscape",
                ["http://a.tile.thunderforest.com/landscape/${z}/${x}/${y}.png",
                 "http://b.tile.thunderforest.com/landscape/${z}/${x}/${y}.png",
                 "http://c.tile.thunderforest.com/landscape/${z}/${x}/${y}.png"],
                {crossOriginKeyword: null}
            );

// http://www.thunderforest.com/outdoors/
Layers.OUTDOORS = new OpenLayers.Layer.OSM("OSM Outdoors",
                ["http://a.tile.thunderforest.com/outdoors/${z}/${x}/${y}.png",
                 "http://b.tile.thunderforest.com/outdoors/${z}/${x}/${y}.png",
                 "http://c.tile.thunderforest.com/outdoors/${z}/${x}/${y}.png"],
                {crossOriginKeyword: null}
            );

Layers.STAMEN_WATERCOLOR = new OpenLayers.Layer.OSM("Stamen Watercolor",
                ["http://a.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg",
                 "http://b.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg",
                 "http://c.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg"],
                {crossOriginKeyword: null}
            );

Layers.MAP_BOX_HIKE = new OpenLayers.Layer.XYZ('Hiking Base Map', [
            'http://a.tiles.mapbox.com/v4/' + 'bjohare.lcbh2m4m' + '/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiYmpvaGFyZSIsImEiOiI1S3VKQ3NFIn0.TPJtCWtEGXg45rUz766_2Q',
            'http://b.tiles.mapbox.com/v4/' + 'bjohare.lcbh2m4m' + '/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiYmpvaGFyZSIsImEiOiI1S3VKQ3NFIn0.TPJtCWtEGXg45rUz766_2Q',
            'http://c.tiles.mapbox.com/v4/' + 'bjohare.lcbh2m4m' + '/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiYmpvaGFyZSIsImEiOiI1S3VKQ3NFIn0.TPJtCWtEGXg45rUz766_2Q',
            'http://d.tiles.mapbox.com/v4/' + 'bjohare.lcbh2m4m' + '/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiYmpvaGFyZSIsImEiOiI1S3VKQ3NFIn0.TPJtCWtEGXg45rUz766_2Q'], {
            sphericalMercator: true,
            wrapDateLine: true
        });

Layers.MAP_BOX_OUTDOORS = new OpenLayers.Layer.XYZ('Outdoors Base Map', [
            'http://a.tiles.mapbox.com/v4/' + 'bjohare.lcbha25i' + '/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiYmpvaGFyZSIsImEiOiI1S3VKQ3NFIn0.TPJtCWtEGXg45rUz766_2Q',
            'http://b.tiles.mapbox.com/v4/' + 'bjohare.lcbha25i' + '/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiYmpvaGFyZSIsImEiOiI1S3VKQ3NFIn0.TPJtCWtEGXg45rUz766_2Q',
            'http://c.tiles.mapbox.com/v4/' + 'bjohare.lcbha25i' + '/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiYmpvaGFyZSIsImEiOiI1S3VKQ3NFIn0.TPJtCWtEGXg45rUz766_2Q',
            'http://d.tiles.mapbox.com/v4/' + 'bjohare.lcbha25i' + '/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiYmpvaGFyZSIsImEiOiI1S3VKQ3NFIn0.TPJtCWtEGXg45rUz766_2Q'], {
            sphericalMercator: true,
            wrapDateLine: true
        });

var apiKey = 'AhhQBBaTq3cZgChLehXIWlMTWRqG-GVUi9rb_0xGK_QQSwEAigT80_UJpgZvrPC5';
Layers.BING_AERIAL = new OpenLayers.Layer.Bing({
                name: "Aerial",
                key: apiKey,
                type: "Aerial"
            });