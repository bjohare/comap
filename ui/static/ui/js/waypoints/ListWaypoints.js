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

waypoints.list = (function(){

    // private
    var map = null;
    var route = null;
    var waypoints = null;
    var select = null;

    function _initMap(){

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
        waypoints = new ol.layer.Vector({
            title: 'Waypoints',
            style: style.waypoint.DEFAULT,
            projection: 'EPSG:3857'
        })

        // controls
        var scaleline = new ol.control.ScaleLine();

        // interactions
        select = new ol.interaction.Select({
            style: style.waypoint.SELECT,
            layers: [waypoints]
        })

        // view
        var view = new ol.View({
            center: [0, 0],
            zoom: 2,
            maxZoom: 19
        });

        // map
        map = new ol.Map({
            layers: [osm, route, waypoints],
            target: 'map',
            view: view,
            controls: ol.control.defaults({
                attributionOptions: {
                    collapsible: false
                }
            }).extend([scaleline]),
            interactions: ol.interaction.defaults().extend([select]),
        });

        $('#reset-map').bind('click', function(e) {
            map.getView().fit(route.getSource().getExtent(), map.getSize());
        });


        /* build list of waypoints */
        _buildWaypointList();

        /* feature selection event handling */
        select.getFeatures().on('add', function(e) {
                var feature = this.getArray()[0];
                var fid = feature.getId();
                var feat = feature.clone();
                var attrs = feat.getProperties();
                var files = attrs.media.files;
                //var geom = feat.geometry.transform('EPSG:3857','EPSG:4326');
                var group = attrs.route.group.name;
                var geom = feat.getGeometry();
                var point = ol.proj.transform(
                                geom.getCoordinates(), 'EPSG:3857', 'EPSG:4326'
                            );
                map.getView().fit(geom.getExtent(), map.getSize(),{
                    maxZoom: 15
                });
                // irish grid ref
                wgs84=new GT_WGS84();
                wgs84.setDegrees(point[1], point[0]);
                irish=wgs84.getIrish();
                gridref = irish.getGridRef(3);
                $('#detail-panel-body').css('display','block');
                $('#detail-heading').html('<h5>' + attrs.name + '</h5>');
                $('.panel-body').find('span.description').html(attrs.description);
                // populate the carousel
                if (files.length > 0) {
                    // need to check for content_type here..
                    // and only add images to the carousel
                    var numImages = 0;
                    $.each(files, function( index, file) {
                        var content_type = file.content_type.split('/')[0];
                        switch(content_type) {
                            case 'image':
                                numImages += 1;
                                if (numImages === 1) {
                                    // initialize it on first pass
                                    $('#carousel').carousel();
                                    $('#carousel').css('display','block');
                                }
                                var active = numImages === 1 ? 'active' : '';
                                var indicator = '<li data-target="#carousel" data-slide-to="' + index + '" class="' + active+ '"></li>';
                                var slide = '<div class="item ' + active + '">' +
                                            '<img src="' +  file.media_url + '"/>' +
                                            '</div>'
                                $('.carousel-inner').append(slide);
                                $('.carousel-indicators').append(indicator);
                                $('#carousel').carousel('cycle');
                                break;
                            case 'audio':
                                var audio = $('audio');
                                audio.css('display','block');
                                audio.append('<source src="' + file.media_url + '" type="' + file.content_type + '"/>');
                                break;
                            case 'video':
                                var video = $('#video-panel');
                                var vid = "vid_" + index;
                                video.css('display','block');
                                video.append('<video id="' + vid + '" preload controls class="video-js vjs-default-skin vjs-big-play-centered embed-responsive-item">' +
                                                '<source src="' + file.media_url + '" type="' + file.content_type + '"/>' +
                                             '</video>');
                                videojs(vid, {"width":"auto", "height":"auto"});
                                break;
                        }
                    });
                }
                else {
                    $('#carousel').carousel('pause');
                    $('#carousel').css('display','none');
                }
                $('.panel-body').find('span.elevation').html(attrs.elevation + ' metres');
                $('.panel-body').find('span.latitude').html(point[0].toFixed(4));
                $('.panel-body').find('span.longitude').html(point[1].toFixed(4));
                $('.panel-body').find('span.irishgrid').html(gridref);
                $('.panel-body').find('span.created').html(moment(attrs.created).format('Do MMMM YYYY hh:mm a'));
                $('.panel-body').find('a.editlink').prop('href','/comap/waypoints/edit/' + fid);
                $('li[id=' + fid + ']').css('background-color','#6B9430').css('color', 'white');
                $('li[id=' + fid + '] a').css('color', 'white');
                $('#deleteForm').prop('action', Config.WAYPOINT_API_URL + '/' + fid);
        });

        /* feature unselection event handling */
        select.getFeatures().on("remove", function(e){
            $('#detail-heading').html('<h5>Select a waypoint</h5>');
            $('#detail-panel-body').css('display','none');
            $('.carousel-inner').empty();
            $('.carousel-indicators').empty();
            $('#carousel').carousel('pause');
            $('#carousel').css('display','none');
            $('li.list-group-item').css('background-color','white');
            $('li.list-group-item a').css('color','#526325');
            $('audio').css('display','none').empty();
            $.each($('audio'), function () {
                this.pause();
                //this.currentTime = 0;
            });
            $.each($('video'), function () {
                videojs(this.id).dispose();
            });
            $('#video-panel').css('display','none').empty();
        });
    }

    function _buildWaypointList(){
        var url = document.URL;
        var parts = url.split('/');
        var routeId = parts[6];
        console.log('Loading waypoints for route with id: ' + routeId);
        //var waypointUrl = Config.WAYPOINT_API_URL + '.json?route_id=' + routeId;
        var routeName = '';
        var numWaypoints = 0;

        /* Get the Routes geojson */
        $.getJSON(Config.TRACK_API_URL + '/' + routeId + '.json', function(data, status, jqXHR) {
            var routeId = data.id;
            var props = data.properties;
            var waypts = data.properties.waypoints;
            routeName = data.properties.name;
            if (jqXHR.status == 200) {

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
            }

            if (waypts.features.length == 0) {
                $('#waypoints-map-panel').css('display','none');
                $('ul.list-group').css('display','none');
                $('#detail-panel').css('display','none');
                $('#detail-panel-body').css('display','none');
                $('#create-link').empty();
                var heading = '<h5>No Waypoints</h5>';
                var panelText = '<h5>There are no waypoints associated with the ' + routeName + ' route.</h5>';
                $('#heading').html(heading);
                $('#panel').html(panelText);
                $('#panel').append('<p><span><strong><hr/></p>');
                $('#panel').append('<p>');
                $('#panel').append('<a class="listlink" href="/comap/waypoints/create/' + routeId +'"><button class="btn btn-success"><span class="glyphicon glyphicon-plus"></span> Add a new Waypoint</button></a>');
                $('#panel').append('</p>');
            }
            else {
                $('#waypoints-map-panel').css('visibility','visible');
                //$('#map').css('visibility','visible');
                $('#detail-panel').css('visibility','visible');
                $('#detail-panel-body').css('display','none');
                var heading = '<h5>' + routeName + '</h5>';
                $('#heading').html(heading);
                $('#panel').html('<p>Here is a list of waypoints for the ' + routeName + ' route.</p>');
                $('#create-link').html('<a class="listlink" href="/comap/waypoints/create/' + routeId +'"><button class="btn btn-success"><span class="glyphicon glyphicon-plus"></span> Add a new waypoint</button></a>');
                // add waypoints to the list..
                $('ul.list-group').empty();
                var features = waypts.features;
                $.each(features, function(i){
                    var name = features[i].properties.name;
                    var id = features[i].id;
                    $('ul.list-group').append('<li class="list-group-item" id="' + id + '"><a class="route-link" id="' + id + '" href="#">' + name + '</a><span class="glyphicon glyphicon-chevron-right pull-right"></span></li>');
                });

                // add the waypoints to the map
                var geoJSONFormat = new ol.format.GeoJSON();
                var source = new ol.source.Vector({
                    format: geoJSONFormat,
                });
                var features = geoJSONFormat.readFeatures(waypts, {
                    dataProjection: 'EPSG:4326',
                    featureProjection: 'EPSG:3857'
                });
                source.addFeatures(features);
                waypoints.setSource(source);

            }
            $( "#list a" ).bind( "click", function() {
                var fid = $(this).attr("id");
                var feature = waypoints.getSource().getFeatureById(fid);
                select.getFeatures().clear();
                select.getFeatures().push(feature);
            });
        }).fail(function() {
            console.log( "failed to get route..." );
            $('#waypoints-map-panel').css('display','none');
            $('ul.list-group').css('display','none');
            $('#detail-panel').css('display','none');
            $('#detail-panel-body').css('display','none');
            $('#create-link').empty();
            var heading = '<h5>No Waypoints</h5>';
            var panelText = '<h5>No route found.</h5>';
            $('#heading').html(heading);
            $('#panel').html(panelText);
        });
    }

    function _buildDeleteDialog(){

        var options = {
            dataType: 'json',
            beforeSubmit: function(arr, $form, options) {
                console.log('in before submit..');
            },
            success: function(data, status, xhr) {
                console.log(status);
                if (status == 'nocontent') {
                    // remove features and readd them
                    waypoints.getSource().clear();
                    _buildWaypointList(waypoints);
                }
            },
            error: function(xhr, status, error){
                var json = xhr.responseJSON
                console.log(error);
            },
        }

        var modalOpts = {
            keyboard: true,
            backdrop: 'static',
        }

        $("#btnDelete").click(function(){
            $("#deleteWaypointModal").modal(modalOpts, 'show');
        });

        $("#deleteConfirm").click(function(){
            $('#deleteForm').ajaxSubmit(options);
            $("#deleteWaypointModal").modal('hide');
        });
    }

    // public
    return {
        init: function(){
            _initMap();
            _buildDeleteDialog();
        }

    };

}());

$(document).ready(function() {
    waypoints.list.init();
});






