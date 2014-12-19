/*
    Copyright (C) 2014  Brian O'Hare

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/
 
var EditMap = OpenLayers.Class({
    
    /* initial setup */
    initialize: function(fid) {
        this.feat_id = fid;
	},
    
    main: function(){
        this.map = this.initMap();
    },
    
    /* map creation */
    initMap: function() {
		
        var mapOptions = {
                displayProjection: new OpenLayers.Projection("EPSG:4326"),
                controls: [new OpenLayers.Control.Attribution(),
                           new OpenLayers.Control.ScaleLine()],
                maxExtent: new OpenLayers.Bounds(10.5,51.5,5.5,55.5).transform("EPSG:4326", "EPSG:3857"),
                units: 'm',
        }
    
        var map = new OpenLayers.Map('edit-map',  {options: mapOptions});
		
		/* add layers */
		var ocm = Layers.OCM;
		ocm.options = {layers: "basic", isBaseLayer: false, visibility: false, displayInLayerSwitcher: true};
        map.addLayers([Layers.OCM]);
		var sat = Layers.GOOGLE_SATELLITE;
		map.addLayers([sat]);
		
		/*
		var land = Layers.LANDSCAPE;
		ocm.addOptions({layers: "basic", isBaseLayer: false, visibility: true, displayInLayerSwitcher: true});
        map.addLayers([land]);
		
		var outdoors = Layers.OUTDOORS;
		map.addLayers([outdoors]);
		*/
		
        /* Styles */
         
        var defaultStyle = new OpenLayers.Style({
            strokeColor: "#980000",
            fillColor: "green",
            pointRadius: 5,
            graphicZIndex:0,
        });
        
        var selectStyle = new OpenLayers.Style({
            pointRadius: 10,
            fillColor: "yellow",
            label: " ${name}",
            labelAlign: "lm",
            labelXOffset: "20",
            labelOutlineColor: "white",
            labelOutlineWidth: 3,
            fontSize: 16,
            graphicZIndex: 10,
        });
        
        var pointStyles = new OpenLayers.StyleMap(
            {
                "default": defaultStyle,
                "select": selectStyle
            });

        var heritage_route = new OpenLayers.Layer.Vector("Heritage South Route", {
                srsName: "EPSG:4326",
                strategies: [new OpenLayers.Strategy.BBOX()],
                protocol: new OpenLayers.Protocol.WFS({
                    url: "/map/",
                    featureType: ["heritage_cycle_route_south"]}),
                box: false,
                style: {'strokeWidth': 4, 'strokeColor': '#6e0045', 'strokeLinecap': 'round', 'strokeDashstyle':'dot'},
        });
		map.addLayers([heritage_route]);
        
        var waypoints = new OpenLayers.Layer.Vector("Waypoints", {
            strategies: [new OpenLayers.Strategy.Fixed()],
            protocol: new OpenLayers.Protocol.HTTP({
                url: "/comap/api/waypoints/" + this.feat_id + ".json",
                format: new OpenLayers.Format.GeoJSON(),
            }),
            styleMap: pointStyles,
            eventListeners: {
					"vertexmodified": function(evt){
						// update the long/lat values on the form
						var lonlat = map.getLonLatFromPixel(evt.pixel);
						lonlat.transform(map.getProjectionObject(), new OpenLayers.Projection("EPSG:4326"));
						var lat = lonlat.lat.toPrecision(8);
						var lon = lonlat.lon.toPrecision(8);
						$('#lat').html('&nbsp;' + lat);
						$('#lng').html('&nbsp;' + lon);
						$('#the_geom').val('POINT(' + lon + ' ' + lat + ')');
					},
					
                },
        });
        map.addLayers([waypoints]);
		
		var selectControl = new OpenLayers.Control.SelectFeature([waypoints]);
		map.addControl(selectControl);
		selectControl.activate();
		
		// TODO: map zoom and pan causes this to fire.. so bit buggy.. as map gets reset
		
		waypoints.events.register("featureadded", selectControl, function(e){
			console.log('featureadded event fired..');
			var geom = e.feature.geometry;
			console.log(e.feature);
			var center = new OpenLayers.LonLat(geom.x, geom.y);
			this.map.setCenter(center,13);
			selectControl.select(e.feature);
		});
		
		
		// add modify feature control to allow feature editing..
		var modifyControl = new OpenLayers.Control.ModifyFeature(waypoints, {
			selectControl: selectControl,
			dragComplete: function(feature){
				// get the elevation for the updated feature and update the form.
                var feat = feature.clone();
                var geom = feat.geometry.transform('EPSG:3857', 'EPSG:4326');
				var lat = geom.y;
				var lon = geom.x;
				$.get(Config.ELEVATION_API_URL + Config.MAPQUEST_KEY+ '&shapeFormat=raw&latLngCollection=' + lat + ',' + lon,
					  function(data){
						var elevation = data.elevationProfile[0].height;
						$('#elevation').val(elevation);
						$('#elev').html('&nbsp;' + elevation + ' metres');
				});
				var bounds = waypoints.getDataExtent();
				var lonlat = new OpenLayers.LonLat(bounds.left, bounds.bottom);
				map.setCenter(lonlat);
			},
			mode: OpenLayers.Control.ModifyFeature.DRAG,
		});
		map.addControl(modifyControl);
		modifyControl.activate();
		
		map.addControl(new OpenLayers.Control.LayerSwitcher());
        map.zoomToExtent(new OpenLayers.Bounds(-8.06,52.94,-7.92,53.01).transform("EPSG:4326", "EPSG:3857"));       
        
        return map;
    },
	
});



