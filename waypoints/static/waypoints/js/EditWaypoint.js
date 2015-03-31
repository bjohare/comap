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

var EditWaypointApp = OpenLayers.Class({
    
    /* initial setup */
    initialize: function() {
        this.initForm();
        this.map = this.initMap();
	},

    /* Initialize the form */
    initForm: function(){
        console.log('Initializing form...');
        $('#waypointForm').formValidation({
            framework: 'bootstrap',
            // Feedback icons
            icon: {
                valid: 'glyphicon glyphicon-ok',
                invalid: 'glyphicon glyphicon-remove',
                validating: 'glyphicon glyphicon-refresh'
            },
            // List of fields and their validation rules
            fields: {
                name: {
                    validators: {
                        notEmpty: {
                            message: 'The waypoint name is required and cannot be empty'
                        },
                    }
                },
                description: {
                    validators: {
                        notEmpty: {
                            message: 'The description is required and cannot be empty'
                        }
                    }
                },
                the_geom: {
                    validators: {
                        notEmpty: {
                            message: 'Please add a point to the map.'
                        },
                    }
                },
            }
        });
        
        var progressbar = $('#progressbar').progressbar();
        var that = this;
        $('#progressbar').css("display","none");
        $('#waypointForm').ajaxForm({
            beforeSubmit: function(arr, $form, options) {
                $('#progressbar').css("display","block");
                var now = new Date();
                // update the post values
                arr[1].value = now.toISOString();
                this.url = Config.WAYPOINT_API_URL + '/' + $('#fid').val();
            },
            uploadProgress: function(event, position, total, percentComplete) {
                progressbar.progressbar({value: percentComplete});
            },
            success: function(data, status, xrh) {
                $('#progressbar').css("display","none");
                $('#update-form-panel').css('display','none');
                console.log('Updated Waypoint.')
                var props = xrh.responseJSON.properties;
                var id = xrh.responseJSON.id;
                $('#update-info').css("display", "block");
                $('#update-info-heading').append('<h4>Waypoint updated successfully</h4>');
                $('#update-info-panel').append('<p><span><strong>Waypoint name:</strong> ' + props.name + '</span></p>');
                $('#update-info-panel').append('<p><span><strong>Description:</strong> ' + props.description + '</span></p>');
                $('#update-info-panel').append('<p><span><strong>Created:</strong> ' + moment(props.created).format('Do MMMM YYYY hh:mm a') + '</span></p>');
                $('#update-info-panel').append('<p><span><strong>Route:</strong> ' + props.route.name + '</span></p>');
                $('#update-info-panel').append('<p><span><strong>Elevation:</strong> ' + props.elevation + ' metres.</span></p>');
                $('#update-info-panel').append('<p><span><strong><hr/></p>');
                $('#update-info-panel').append('<p>');
                $('#update-info-panel').append('<a class="editlink" href="/comap/waypoints/edit/' + id + '/"><button><span class="glyphicon glyphicon-edit"></span> Edit this Waypoint..</button></a> &nbsp;');
                $('#update-info-panel').append('<a class="listlink" href="/comap/waypoints/list/' + that.routeId + '/"><button><span class="glyphicon glyphicon-list"></span> List Waypoints for this route..</button></a> &nbsp;');
                $('#update-info-panel').append('<a class="listlink" href="/comap/waypoints/create/' + that.routeId + '/"><button><span class="glyphicon glyphicon-asterisk"></span> Create a new Waypoint..</button></a>');
                $('#update-info-panel').append('</p>');
            },
            error: function(xhr, status, error){
                $('#progressbar').css("display", "none");
                console.log(error);
            },
        });
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
    
        var map = new OpenLayers.Map('edit-waypoint-map',  {options: mapOptions});
		
		/* add layers */
		var ocm = Layers.OCM;
		ocm.options = {layers: "basic", isBaseLayer: false, visibility: false, displayInLayerSwitcher: true};
        map.addLayers([Layers.OCM]);
        
        var waypoints = new OpenLayers.Layer.Vector("Waypoints", {
            styleMap: this.getPointStyleMap(),
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
        
        // add the route and waypoint features to the map
        this.loadVectors(waypoints);
		
		var selectControl = new OpenLayers.Control.SelectFeature([waypoints]);
		map.addControl(selectControl);
		selectControl.activate();
        
		// TODO: map zoom and pan causes this to fire.. so bit buggy.. as map gets reset
		waypoints.events.register("featureadded", selectControl, function(e){
			console.log('featureadded event fired..');
			var geom = e.feature.geometry.clone();
            geom.transform('EPSG:3857', 'EPSG:4326');
            // update the geom on the form and trigger validation
            $('#the_geom').val('POINT(' + geom.x + ' ' + geom.y + ')');
            $('#the_geom').trigger("input");
            var lat = geom.y;
            var lon = geom.x;
            $.get(Config.ELEVATION_API_URL + Config.MAPQUEST_KEY+ '&shapeFormat=raw&latLngCollection=' + lat + ',' + lon,
                  function(data){
                    var elevation = data.elevationProfile[0].height;
                    $('#elevation').val(elevation);
                    $('#elev').html('&nbsp;' + elevation + ' metres');
            });
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
                //map.setCenter(lonlat);
			},
			mode: OpenLayers.Control.ModifyFeature.DRAG,
		});
		map.addControl(modifyControl);
		modifyControl.activate();
		
		map.addControl(new OpenLayers.Control.LayerSwitcher());
        map.zoomToExtent(new OpenLayers.Bounds(-8.06,52.94,-7.92,53.01).transform("EPSG:4326", "EPSG:3857"));       
        
        return map;
    },
    
    loadVectors: function(waypoints) {
        var url = document.URL;
        var parts = url.split('/');
        var id = parts[6];
        console.log('Waypoint id is ' + id);
        var fid = id;
        this.routeId = -1;
        var waypointUrl = Config.WAYPOINT_API_URL + '/' + id + '.json';
        console.log(waypointUrl);
        var that = this;
        $.getJSON(waypointUrl, function(data){
                var props = data.properties;
                that.routeId = data.properties.route.fid;
                if (props.length == 0) {
                    alert('Error, no features found');
                }
                else {
                    $('#fid').val(id);
                    $('#name').val(props.name);
                    $('#description').val(props.description);
                    $('#route').val(that.routeId);
                    var geojson = new OpenLayers.Format.GeoJSON({
                                    'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                                    'externalProjection': new OpenLayers.Projection("EPSG:4326")
                    });
                    var features = geojson.read(data);
                    waypoints.addFeatures(features);
                    var jsonUrl = Config.TRACK_API_URL + '/' + that.routeId + '.json';
                    console.log(jsonUrl);
                    $.getJSON(jsonUrl, function(data){
                        var geojson = new OpenLayers.Format.GeoJSON({
                                    'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                                    'externalProjection': new OpenLayers.Projection("EPSG:4326")
                            });
                            var routeName = data.properties.name;
                            $('#update-form-heading').html('<h5>Add a waypoint to the ' + routeName + ' route</h5>');
                            var route = new OpenLayers.Layer.Vector(routeName, {
                            styleMap: that.getLineStyleMap()
                            });
                            that.map.addLayers([route]);
                            var features = geojson.read(data);
                            route.addFeatures(features);
                            that.map.zoomToExtent(route.getDataExtent());
                    }).fail(function(data){
                        console.log('Failed to load route features..');
                    });
                }
            }).fail(function(data){
                alert('Failed.. do something here..');
            }); 
    },
    
    getLineStyleMap: function(){
        /* Styles */
        var defaultStyle = new OpenLayers.Style({
            strokeColor: "#db337b",
            strokeWidth: 2.5,
            strokeDashstyle: "dash",
            label: " ${name}",
            labelAlign: "lm",
            labelXOffset: "20",
            labelOutlineColor: "white",
            labelOutlineWidth: 3,
            fontSize: 16,
            graphicZIndex: 10,
        });
        
        var selectStyle = new OpenLayers.Style({
            strokeColor: "yellow",
            strokeWidth: 3.5,
            strokeDashstyle: "dashdot",
            label: " ${name}",
            labelAlign: "lm",
            labelXOffset: "20",
            labelOutlineColor: "white",
            labelOutlineWidth: 3,
            fontSize: 16,
            graphicZIndex: 10,
        });
        
        var lineStyles = new OpenLayers.StyleMap(
            {
                "default": defaultStyle,
                "select": selectStyle
        });
        
        return lineStyles;
    },
    
    getPointStyleMap: function(){
        var defaultStyle = new OpenLayers.Style({
            strokeColor: "#980000",
            fillColor: "green",
            pointRadius: 5,
            graphicZIndex:0,
        });
        
        var selectStyle = new OpenLayers.Style({
            pointRadius: 10,
            fillColor: "yellow",
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
        
        return pointStyles;
    }
	
});


