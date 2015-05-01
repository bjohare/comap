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

var tf_options = {
            layers: "basic",
            attribution: "Testing",
            isBaseLayer: true, visibility: true, displayInLayerSwitcher: true
        }

// http://www.thunderforest.com/outdoors/
Layers.OUTDOORS = new OpenLayers.Layer.OSM("OSM Outdoors",
                ["http://a.tile.thunderforest.com/outdoors/${z}/${x}/${y}.png",
                 "http://b.tile.thunderforest.com/outdoors/${z}/${x}/${y}.png",
                 "http://c.tile.thunderforest.com/outdoors/${z}/${x}/${y}.png"],
                 {layers: "basic",
                 attribution: 'Maps ©' + '<a href="http://www.thunderforest.com">Thunderforest</a>, Data © ' + '<a href="http://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
                 isBaseLayer: true,
                 visibility: true,
                 displayInLayerSwitcher: true,
                 crossOriginKeyword: null}
            );

Layers.STAMEN_WATERCOLOR = new OpenLayers.Layer.OSM("Stamen Watercolor",
                ["http://a.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg",
                 "http://b.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg",
                 "http://c.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg"],
                {crossOriginKeyword: null}
            );

Layers.MAP_BOX_HIKE = new OpenLayers.Layer.XYZ(' Hiking Base Map', [
            'http://a.tiles.mapbox.com/v4/' + 'bjohare.lcbh2m4m' + '/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiYmpvaGFyZSIsImEiOiI1S3VKQ3NFIn0.TPJtCWtEGXg45rUz766_2Q',
            'http://b.tiles.mapbox.com/v4/' + 'bjohare.lcbh2m4m' + '/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiYmpvaGFyZSIsImEiOiI1S3VKQ3NFIn0.TPJtCWtEGXg45rUz766_2Q',
            'http://c.tiles.mapbox.com/v4/' + 'bjohare.lcbh2m4m' + '/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiYmpvaGFyZSIsImEiOiI1S3VKQ3NFIn0.TPJtCWtEGXg45rUz766_2Q',
            'http://d.tiles.mapbox.com/v4/' + 'bjohare.lcbh2m4m' + '/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiYmpvaGFyZSIsImEiOiI1S3VKQ3NFIn0.TPJtCWtEGXg45rUz766_2Q'], {
            sphericalMercator: true,
            wrapDateLine: true,
            attribution: "<a href='https://www.mapbox.com/about/maps/' target='_blank'>&copy; Mapbox &copy; OpenStreetMap</a> <a class='mapbox-improve-map' href='https://www.mapbox.com/map-feedback/' target='_blank'>Improve this map</a>"
        });

Layers.MAP_BOX_OUTDOORS = new OpenLayers.Layer.XYZ(' Outdoors Base Map', [
            'http://a.tiles.mapbox.com/v4/' + 'bjohare.lcbha25i' + '/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiYmpvaGFyZSIsImEiOiI1S3VKQ3NFIn0.TPJtCWtEGXg45rUz766_2Q',
            'http://b.tiles.mapbox.com/v4/' + 'bjohare.lcbha25i' + '/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiYmpvaGFyZSIsImEiOiI1S3VKQ3NFIn0.TPJtCWtEGXg45rUz766_2Q',
            'http://c.tiles.mapbox.com/v4/' + 'bjohare.lcbha25i' + '/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiYmpvaGFyZSIsImEiOiI1S3VKQ3NFIn0.TPJtCWtEGXg45rUz766_2Q',
            'http://d.tiles.mapbox.com/v4/' + 'bjohare.lcbha25i' + '/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiYmpvaGFyZSIsImEiOiI1S3VKQ3NFIn0.TPJtCWtEGXg45rUz766_2Q'], {
            sphericalMercator: true,
            wrapDateLine: true,
            attribution: "<a href='https://www.mapbox.com/about/maps/' target='_blank'>&copy; Mapbox &copy; OpenStreetMap</a> <a class='mapbox-improve-map' href='https://www.mapbox.com/map-feedback/' target='_blank'>Improve this map</a>"
        });

var apiKey = 'AhhQBBaTq3cZgChLehXIWlMTWRqG-GVUi9rb_0xGK_QQSwEAigT80_UJpgZvrPC5';
Layers.BING_AERIAL = new OpenLayers.Layer.Bing({
                name: " Bing Aerial",
                key: apiKey,
                type: "Aerial"
            });

/* Townland Layer and Style */

var context =
            {
                getColor: function(feature) {
                    return '#DFC1DA';
                },
                getSize: function(feature) {
                    return feature.attributes["type"] / map.getResolution() * .703125;
                }
            };
var template =
            {
                strokeColor: "${getColor}",
                fillColor: 'transparent',
                fillOpacity: 0.5,
                strokeWidth: 3,
                strokeDashstyle: "dot",
                label: " ${name}",
                labelAlign: "lm",
                labelXOffset: "10",
                labelOutlineColor: "white",
                labelOutlineWidth: 3,
                fontSize: 9,
            };

var townland_style = new OpenLayers.Style(template, {context: context})

Layers.OSM_TOWNLANDS = new OpenLayers.Layer.Vector("Townlands", {
            internalProjection: new OpenLayers.Projection("EPSG:3857"),
            externalProjection: new OpenLayers.Projection("EPSG:4326"),
            styleMap: new OpenLayers.StyleMap(townland_style),
            //minScale: 1/100000,
            //maxScale: 1/2500,
            strategies: [new OpenLayers.Strategy.Fixed()],
            protocol: new OpenLayers.Protocol.HTTP({
                url: "/comap/media/townlands/monaghan_townlands_osm.json",
                format: new OpenLayers.Format.GeoJSON()
            })
        });