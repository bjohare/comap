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

waypoints.edit = (function(){

    // private vars
    var routeId = null;
    var route = null;
    var waypoints = null;
    var map = null;
    var modify = null;
    var features = null;

    /* Initialize the form */
    function _initForm(){

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

        $('#fileupload').bind('fileuploaddestroy', function (e, data) {
            var csrftoken = $('input[name="csrfmiddlewaretoken"]').val();
            var settings = {
                'accepts': 'application/json',
                'method': 'POST',
                'context': data.context,
                'data': {'_method': 'DELETE',
                         'csrfmiddlewaretoken': csrftoken
                }
            }
            console.log('Deleting: ' + data.url);
            $.ajax(data.url, settings).success(function(data, status, jqXHR){
                $(this).fadeOut("slow", function(){
                    this.remove();
                });
            });

        });


        $('#fileupload').bind('fileuploadprocessfail', function(e, data){
            console.log('processfail', data.files[data.index].name);
            if (data.files.error) {
                //$('.fileinput-button').prop('disabled', true);
                //$('#save').prop('disabled', true);
            }
        });

        submitted = 0;
        $('#fileupload').bind('fileuploadcompleted', function (e, data) {
            submitted += 1;
            var numFiles = data.files.length;
            if (numFiles == submitted) {
                submitted = 0;
                console.log('All files submitted.');
                $('#update-form-panel').css('display','none');
                $('#update-info').css('display', 'block');
            }
        });

        $('#dropzone').bind('dragover', function (e) {
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

        $('#dropzone').bind('drop dragleave', function(e){
           $('#dropzone').removeClass('in hover');
        });

         $('#save').bind('click', function(e){
           $('#dropzone').css('display','none');
           $('.fileinput-button').prop('disabled', true);
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
        });

        //var progressbar = $('#progressbar').progressbar();
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
                //progressbar.progressbar({value: percentComplete});
            },
            success: function(data, status, xrh) {
                console.log('Updated Waypoint.')
                var props = xrh.responseJSON.properties;
                var id = xrh.responseJSON.id;
                $('#update-info-heading').append('<h4>Waypoint updated successfully</h4>');
                $('#update-info-panel').append('<p><span><strong>Waypoint name:</strong> ' + props.name + '</span></p>');
                $('#update-info-panel').append('<p><span><strong>Description:</strong> ' + props.description + '</span></p>');
                $('#update-info-panel').append('<p><span><strong>Created:</strong> ' + moment(props.created).format('Do MMMM YYYY hh:mm a') + '</span></p>');
                $('#update-info-panel').append('<p><span><strong>Route:</strong> ' + props.route.name + '</span></p>');
                $('#update-info-panel').append('<p><span><strong>Elevation:</strong> ' + props.elevation + ' metres.</span></p>');
                $('#update-info-panel').append('<p><span><strong><hr/></p>');
                $('#update-info-panel').append('<p>');
                $('#update-info-panel').append('<a class="editlink" href="/comap/waypoints/edit/' + id + '/"><button><span class="glyphicon glyphicon-edit"></span> Edit this Waypoint..</button></a> &nbsp;');
                $('#update-info-panel').append('<a class="listlink" href="/comap/waypoints/list/' + routeId + '/"><button><span class="glyphicon glyphicon-list"></span> List Waypoints for this route..</button></a> &nbsp;');
                $('#update-info-panel').append('<a class="listlink" href="/comap/waypoints/create/' + routeId + '/"><button><span class="glyphicon glyphicon-asterisk"></span> Create a new Waypoint..</button></a>');
                $('#update-info-panel').append('</p>');

                 // get new waypoint id and post the media
                var template = $('.template-upload');
                var media = template.data('data');
                if (media) {
                    if (media.files.error) {
                        alert('Please fix form errors.');
                        return;
                    }
                    var waypointId = id;
                    var csrftoken = $("input[name='csrfmiddlewaretoken']").val();
                    var formData = {waypoint_id: waypointId, csrfmiddlewaretoken: csrftoken};
                    $('#fileupload').fileupload({
                        formData: formData
                    });
                    $('.fileupload-buttonbar').find('.start').click();
                }
                else {
                    $('#update-form-panel').css('display','none');
                    $('#update-info').css('display', 'block');
                }
            },
            error: function(xhr, status, error){
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
        features = new ol.Collection();
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

        modify = new ol.interaction.Modify({
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
            interactions: ol.interaction.defaults().extend([select, modify]),
        });

        $('#reset-map').bind('click', function(e) {
            map.getView().fit(route.getSource().getExtent(), map.getSize());
        });

        // add the route and waypoint to the map
        _loadVectors();

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
        $('#the_geom').val('POINT(' + lon + ' ' + lat + ')');
    }


    // the route and the waypoint to edit
    function _loadVectors(){
        var url = document.URL;
        var parts = url.split('/');
        var id = parts[6];
        console.log('Waypoint id is ' + id);
        var fid = id;
        routeId = -1;
        var waypointUrl = Config.WAYPOINT_API_URL + '/' + id + '.json';
        $.getJSON(waypointUrl, function(data){
                var props = data.properties;
                //populate the media template
                var files = props.media;
                var template = tmpl('template-download', files);
                $('.files').append(template);
                routeId = data.properties.route.fid;
                if (props.length == 0) {
                    alert('Error, no features found');
                }
                else {
                    $('#fid').val(id);
                    $('#name').val(props.name);
                    $('#description').val(props.description);
                    $('#route').val(routeId);
                    $('#update-form-heading').html('<h5>Update the ' + props.name + ' waypoint</h5>');
                    var geoJSONFormat = new ol.format.GeoJSON();
                    var source = new ol.source.Vector({
                        format: geoJSONFormat,
                    });
                    var wpts = geoJSONFormat.readFeatures(data, {
                        dataProjection: 'EPSG:4326',
                        featureProjection: 'EPSG:3857'
                    });
                    features.extend(wpts);

                    source.addFeatures(wpts);
                    waypoints.setSource(source);


                    var jsonUrl = Config.TRACK_API_URL + '/' + routeId + '.json';
                    $.getJSON(jsonUrl, function(data){
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
                    }).fail(function(data){
                        console.log('Failed to load route features..');
                    });
                }
            }).fail(function(data){
                alert('Failed.. do something here..');
            });
    }

    // public
    return {
        init: function(){
            _initForm();
            _initMap();
        }
    };

}());

$(document).ready(function() {
    waypoints.edit.init();
});
