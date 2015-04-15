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

var CreateWaypointApp = OpenLayers.Class({
    
    /* initial setup */
    initialize: function() {
        
        var url = document.URL;
        var parts = url.split('/');
        var id = parts[6];
        console.log('Route id is ' + id);
        this.routeId = id;
        // add the route id to the form.
        $('#route').val(this.routeId);
        this.initForm();
        this.map = this.initMap();
        $('[data-toggle="popover"]').popover();

	},

    /* Initialize the form */
    initForm: function() {
        console.log('Initializing form...');
        
         // Initialize the jQuery File Upload widget:
        var fileUpload = $('#fileupload').fileupload({
            // Uncomment the following to send cross-domain cookies:
            //xhrFields: {withCredentials: true},
            url: Config.WAYPOINT_MEDIA_API_URL + '.json',
            type: 'POST',
            //singleFileUploads: false,
            autoUpload: false,
            dropZone: $('#dropzone'),
        });
        
        
        $('#fileupload').bind('fileuploadadded', function (e, data) {
            $('#dropzone').css('border','1px solid lightgrey');
            $('#dz-message').css('display','none');
        });
        
        $('#fileupload').bind('fileuploadstopped', function (e, data) {
            $('#dropzone').css('border','1px dashed #6B9430');
            $('#dz-message').css('display','block');
        });
        
        var that = this;
        that.submitted = 0;
        $('#fileupload').bind('fileuploadcompleted', function (e, data) {
            that.submitted += 1;
            var numFiles = data.getNumberOfFiles();
            if (numFiles == that.submitted) {
                console.log('All files submitted.')
                $('#create-form-panel').css('display','none');
                $('#create-info').css('display', 'block');
            }
        });
        
        $(document).bind('dragover', function (e) {
            var dropZone = $('#dropzone'),
                timeout = window.dropZoneTimeout;
            if (!timeout) {
                dropZone.addClass('in');
            } else {
                clearTimeout(timeout);
            }
            var found = false,
                node = e.target;
            do {
                if (node === dropZone[0]) {
                    found = true;
                    break;
                }
                node = node.parentNode;
            } while (node != null);
            if (found) {
                dropZone.addClass('hover');
            } else {
                dropZone.removeClass('hover');
            }
            window.dropZoneTimeout = setTimeout(function () {
                window.dropZoneTimeout = null;
                dropZone.removeClass('in hover');
            }, 100);
        }); 
    
            
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
        }).on('success.field.fv', function(e, data) {
            if (data.fv.getInvalidFields().length > 0) {    // There is invalid field
                data.fv.disableSubmitButtons(true);
            }
        });
       
        $('#waypointForm').ajaxForm({
            url: Config.WAYPOINT_API_URL + ".json",
            beforeSubmit: function(arr, $form, options) {
                $('#progressbar').css("display","block");
                var now = new Date();
                // update the post values
                arr[1].value = now.toISOString();
            },
            uploadProgress: function(event, position, total, percentComplete) {
                //progressbar.progressbar({value: percentComplete});
            },
            success: function(data, status, xrh) {
                console.log('Created Waypoint.')
                var props = xrh.responseJSON.properties;
                var id = xrh.responseJSON.id;
                $('#create-info-heading').append('<h4>Waypoint created successfully</h4>');
                $('#create-info-panel').append('<p><span><strong>Waypoint name:</strong> ' + props.name + '</span></p>');
                $('#create-info-panel').append('<p><span><strong>Description:</strong> ' + props.description + '</span></p>');
                $('#create-info-panel').append('<p><span><strong>Created:</strong> ' + moment(props.created).format('Do MMMM YYYY hh:mm a') + '</span></p>');
                $('#create-info-panel').append('<p><span><strong>Route:</strong> ' + props.route.name + '</span></p>');
                $('#create-info-panel').append('<p><span><strong>Elevation:</strong> ' + props.elevation + ' metres.</span></p>');
                $('#create-info-panel').append('<p><span><strong><hr/></p>');
                $('#create-info-panel').append('<p>');
                $('#create-info-panel').append('<a class="editlink" href="/comap/waypoint/edit/' + id + '/"><button><span class="glyphicon glyphicon-edit"></span> Edit this Waypoint..</button></a> &nbsp;');
                $('#create-info-panel').append('<a class="listlink" href="/comap/waypoints/list/' + that.routeId + '/"><button><span class="glyphicon glyphicon-list"></span> List Waypoints for this route..</button></a> &nbsp;');
                $('#create-info-panel').append('<a class="listlink" href="/comap/waypoints/create/' + that.routeId + '/"><button><span class="glyphicon glyphicon-asterisk"></span> Create a new Waypoint..</button></a>');
                $('#create-info-panel').append('</p>');
                
                 // get new waypoint id and post the media
                var template = $('.template-upload');
                var media = template.data('data');
                if (media) {
                    var waypointId = data.id;
                    var csrftoken = $("input[name='csrfmiddlewaretoken']").val();
                    var formData = {waypoint_id: waypointId, csrfmiddlewaretoken: csrftoken};
                    $('#fileupload').fileupload({
                        formData: formData
                    });
                    $('.fileupload-buttonbar').find('.start').click();
                }
                else {
                    $('#create-form-panel').css('display','none');
                    $('#create-info').css('display', 'block');
                }
                
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
        var mbox_hike = Layers.MAP_BOX_HIKE;
        var mbox_out = Layers.MAP_BOX_OUTDOORS;
        var bing_aerial = Layers.BING_AERIAL;
        mbox_hike.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        mbox_out.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        bing_aerial.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        map.addLayers([mbox_hike, mbox_out, bing_aerial]);
        
        /*
		var ocm = Layers.OCM;
		ocm.options = {layers: "basic", isBaseLayer: false, visibility: false, displayInLayerSwitcher: true};
        map.addLayers([Layers.OCM]);
        */
        
        // add the route layer to the map
        this.loadRouteVector();
        
        var waypoints = new OpenLayers.Layer.Vector("Waypoints", {
            styleMap: this.getPointStyleMap(),
            eventListeners: {
					"vertexmodified": function(evt){
						// update the long/lat values on the form
						var lonlat = map.getLonLatFromPixel(evt.pixel);
						lonlat.transform(map.getProjectionObject(), new OpenLayers.Projection("EPSG:4326"));
						var lat = lonlat.lat.toPrecision(8);
						var lon = lonlat.lon.toPrecision(8);
						// irish grid ref
                        wgs84=new GT_WGS84();
                        wgs84.setDegrees(lat, lon);
                        irish=wgs84.getIrish();
                        gridref = irish.getGridRef(3);
						$('#lat').html('&nbsp;' + lat);
						$('#lng').html('&nbsp;' + lon);
                        $('#gridref').html('&nbsp;' + gridref);
						$('#the_geom').val('POINT(' + lon + ' ' + lat + ')');
					},
					
                },
        });
        map.addLayers([waypoints]);
		
		var selectControl = new OpenLayers.Control.SelectFeature([waypoints]);
		map.addControl(selectControl);
		selectControl.activate();
        
        var pointControl = new OpenLayers.Control.DrawFeature(waypoints,
                                OpenLayers.Handler.Point);
        map.addControl(pointControl);
        pointControl.activate();
        
		// TODO: map zoom and pan causes this to fire.. so bit buggy.. as map gets reset
		waypoints.events.register("featureadded", selectControl, function(e){
			console.log('featureadded event fired..');
			var geom = e.feature.geometry.clone();
            geom.transform('EPSG:3857', 'EPSG:4326');
            // update the geom on the form and trigger validation
            $('#the_geom').val('POINT(' + geom.x + ' ' + geom.y + ')');
            $('#the_geom').trigger("input");
            var lat = geom.y.toPrecision(8);
            var lon = geom.x.toPrecision(8);
            wgs84=new GT_WGS84();
            wgs84.setDegrees(lat, lon);
            irish=wgs84.getIrish();
            gridref = irish.getGridRef(3);
            $('#lat').html('&nbsp;' + lat);
            $('#lng').html('&nbsp;' + lon);
            $('#gridref').html('&nbsp;' + gridref);
            $.get(Config.ELEVATION_API_URL + Config.MAPQUEST_KEY+ '&shapeFormat=raw&latLngCollection=' + lat + ',' + lon,
                  function(data){
                    var elevation = data.elevationProfile[0].height;
                    $('#elevation').val(elevation);
                    $('#elev').html('&nbsp;' + elevation + ' metres');
            });
            // only allow one feature to be added.
            pointControl.deactivate();
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
    
    loadRouteVector: function() {
        /* Add the routes for the current group */
        var that = this;
        var jsonUrl = Config.TRACK_API_URL + '/' + this.routeId + '.json';
        console.log(jsonUrl);
        $.getJSON(jsonUrl, function(data){
            var geojson = new OpenLayers.Format.GeoJSON({
                        'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                        'externalProjection': new OpenLayers.Projection("EPSG:4326")
                });
                var routeName = data.properties.name;
                $('#create-form-heading').html('<h5>Add a waypoint to the ' + routeName + ' route</h5>');
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



