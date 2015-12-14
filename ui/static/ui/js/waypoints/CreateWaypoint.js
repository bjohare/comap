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

var waypoints = {};

waypoints.create = (function() {

    // private vars
    var routeId = null;
    var route = null;
    var waypoints = null;
    var map = null;

    function _init() {

        var url = document.URL;
        var parts = url.split('/');
        var id = parts[6];
        console.log('Route id is ' + id);
        routeId = id;
        // add the route id to the form.
        $('#route').val(this.routeId);
        $('[data-toggle="popover"]').popover();

    }

    /* Initialize the form */
    function _initForm() {
        console.log('Initializing form...');

        // Initialize the jQuery File Upload widget:
        var fileUpload = $('#fileupload').fileupload({
            // Uncomment the following to send cross-domain cookies:
            //xhrFields: {withCredentials: true},
            url: Config.WAYPOINT_MEDIA_API_URL + '.json',
            type: 'POST',
            autoUpload: false,
            dropZone: $('#dropzone'),
            previewMaxWidth: 100,
            previewMaxHeight: 100,
            maxNumberOfFiles: 5,
            maxFileSize: 10000000,
        });

        /*
        $('#fileupload').bind('fileuploadadded', function (e, data) {
            //$('#dz-message').css('display','none');
            $('#dropzone').css('border','2px solid lightgrey');
        });
        */
        var that = this;
        that.cancelled = 0;
        $('#fileupload').bind('fileuploadfail', function(e, data) {
            that.cancelled += 1;
            var numFiles = data.originalFiles.length;
            if (numFiles == that.cancelled) {
                that.cancelled = 0;
                console.log('All uploads cancelled');
                $('#dz-message').css('display', 'block');
            }
        });


        var that = this;
        that.submitted = 0;
        $('#fileupload').bind('fileuploadcompleted', function(e, data) {
            that.submitted += 1;
            var numFiles = data.getNumberOfFiles();
            if (numFiles == that.submitted) {
                that.submitted = 0;
                console.log('All files submitted.');
                $('#create-form-panel').css('display', 'none');
                $('#create-info').css('display', 'block');
            }
        });

        $('#fileupload').bind('fileuploadchange', function(e, data) {
            console.log('changed...')
        });

        $('#dropzone').bind('dragover', function(e) {
            var dropZone = $('#dropzone');
            dropZone.addClass('in');
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
        });

        $('#dropzone').bind('drop dragleave', function(e) {
            $('#dropzone').removeClass('in hover');
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
            if (data.fv.getInvalidFields().length > 0) { // There is invalid field
                data.fv.disableSubmitButtons(true);
            }
        });

        $('#waypointForm').ajaxForm({
            url: Config.WAYPOINT_API_URL + ".json",
            beforeSubmit: function(arr, $form, options) {
                $('#progressbar').css("display", "block");
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
                    var formData = {
                        waypoint_id: waypointId,
                        csrfmiddlewaretoken: csrftoken
                    };
                    $('#fileupload').fileupload({
                        formData: formData
                    });
                    $('.fileupload-buttonbar').find('.start').click();
                } else {
                    $('#create-form-panel').css('display', 'none');
                    $('#create-info').css('display', 'block');
                }

            },
            error: function(xhr, status, error) {
                $('#progressbar').css("display", "none");
                console.log(error);
            },
        });
    }

    function _initMap() {

        /* Layers */

        // osm
        var osm = new ol.layer.Tile({
            title: 'OpenStreetMap',
            source: new ol.source.OSM()
        });

        // routes
        route = new ol.layer.Vector({
            title: 'Route',
            style: style.route.SELECT,
            projection: 'EPSG:3857'
        });

        // waypoints
        var features = new ol.Collection();
        waypoints = new ol.layer.Vector({
            source: new ol.source.Vector({
                features: features
            }),
            title: 'Waypoints',
            style: style.waypoint.SELECT,
            projection: 'EPSG:3857'
        });

        // controls
        var scaleline = new ol.control.ScaleLine();

        // interactions
        select = new ol.interaction.Select({
            style: style.waypoint.SELECT,
            layers: [waypoints]
        });

        draw = new ol.interaction.Draw({
            features: features,
            type: 'Point'
        });

        var modify = new ol.interaction.Modify({
            features: features,
            // the SHIFT key must be pressed to delete vertices, so
            // that new vertices can be drawn at the same position
            // of existing vertices
            /*
            deleteCondition: function(event) {
                return ol.events.condition.shiftKeyOnly(event) &&
                    ol.events.condition.singleClick(event);
            }
            */
        });

        // view
        var view = new ol.View({
            center: [0, 0],
            zoom: 2,
            maxZoom: 19
        });

        // map
        map = new ol.Map({
            layers: [osm, route, waypoints],
            target: 'edit-waypoint-map',
            view: view,
            controls: ol.control.defaults({
                attributionOptions: {
                    collapsible: false
                }
            }).extend([scaleline]),
            interactions: ol.interaction.defaults().extend([select, draw, modify]),
        });

        $('#reset-map').bind('click', function(e) {
            map.getView().fit(route.getSource().getExtent(), map.getSize());
        });

        // add the route to the map
        _loadRoute();

        // handle feature addition
        features.on('add', function(e) {
            // only allow one feature
            // to be added to the map
            map.removeInteraction(draw);
            var feature = this.getArray()[0];
            var feat = feature.clone();
            _updateFeatureAttributes(feat);
        });

        // handle feature modification
        modify.on('modifyend', function(e) {
            var feature = e.features.getArray()[0];
            var feat = feature.clone();
            _updateFeatureAttributes(feat);
        });
    }

    // update the ui with feature attributes
    function _updateFeatureAttributes(feature){
        var feat = feature.clone();
        var attrs = feat.getProperties();
        var geom = feat.getGeometry();
        var point = ol.proj.transform(
            geom.getCoordinates(), 'EPSG:3857', 'EPSG:4326'
        );
        // irish grid ref
        wgs84 = new GT_WGS84();
        wgs84.setDegrees(point[1], point[0]);
        irish = wgs84.getIrish();
        gridref = irish.getGridRef(3);
        var lat = wgs84.latitude.toFixed(5)
        var lon = wgs84.longitude.toFixed(5);
        $('#lat').html('&nbsp;' + lat);
        $('#lng').html('&nbsp;' + lon);
        $('#gridref').html('&nbsp;' + gridref);
        $.get(Config.ELEVATION_API_URL + Config.MAPQUEST_KEY + '&shapeFormat=raw&latLngCollection=' + lat + ',' + lon,
            function(data) {
                var elevation = data.elevationProfile[0].height;
                $('#elevation').val(elevation);
                $('#elev').html('&nbsp;' + elevation + ' metres');
            });
    }

    // load the route
    function _loadRoute() {
        /* Add the routes for the current group */
        var jsonUrl = Config.TRACK_API_URL + '/' + routeId + '.json';
        console.log(jsonUrl);
        $.getJSON(jsonUrl, function(data) {
            // add the route to the map
            var geoJSONFormat = new ol.format.GeoJSON();
            var source = new ol.source.Vector({
                format: geoJSONFormat,
            });
            var features = geoJSONFormat.readFeatures(data, {
                dataProjection: 'EPSG:4326',
                featureProjection: 'EPSG:3857'
            });
            source.addFeatures(features);
            route.setSource(source);
            var extent = route.getSource().getExtent();
            map.getView().fit(extent, map.getSize());

            $('#reset-map').bind('click', function(e) {
                map.getView().fit(route.getSource().getExtent(), map.getSize());
            });
        }).fail(function(data) {
            console.log('Failed to load route features..');
        });
    }

    // public
    return {
        init: function() {
            _init();
            _initForm();
            _initMap();
        }
    };

}());


$(document).ready(function() {
    waypoints.create.init();
});
