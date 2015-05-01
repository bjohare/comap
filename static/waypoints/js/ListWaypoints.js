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

var ListWaypointsApp = OpenLayers.Class({
    
    initialize: function(){
        this.buildDeleteDialog();
        $('.carousel').carousel();
    },
    
    main: function() {
        this.map = this.initMap();
    },
    
    initMap: function() {
        
        var mapOptions = {
                displayProjection: new OpenLayers.Projection("EPSG:4326"),
                controls: [new OpenLayers.Control.Attribution(),
                           new OpenLayers.Control.ScaleLine()],
                maxExtent: new OpenLayers.Bounds(10.5,51.5,5.5,55.5).transform("EPSG:4326", "EPSG:3857"),   
                units: 'm',
        }

        map = new OpenLayers.Map('map', {options: mapOptions});
        
        var bing_aerial = Layers.BING_AERIAL;
        var tf_outdoors = Layers.OUTDOORS;
        var townlands = Layers.OSM_TOWNLANDS;
        tf_outdoors.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        bing_aerial.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        map.addLayers([tf_outdoors, bing_aerial]);
        bing_aerial.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        map.addLayers([tf_outdoors, bing_aerial, townlands]);
               
        /* Styles */
        var defaultLineStyle = new OpenLayers.Style({
            strokeColor: "#db337b",
            strokeWidth: 2.5,
            strokeDashstyle: "dash"
        });
        
        var selectLineStyle = new OpenLayers.Style({
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
                "default": defaultLineStyle,
                "select": selectLineStyle
        });
        
        /* Styles */
         
        var defaultPointStyle = new OpenLayers.Style({
            strokeColor: "#980000",
            fillColor: "green",
            pointRadius: 5,
            graphicZIndex:0,
        });
        
        var selectPointStyle = new OpenLayers.Style({
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
                "default": defaultPointStyle,
                "select": selectPointStyle
            });
        
        /* Add the waypoints for the current group */
        var waypoints = new OpenLayers.Layer.Vector('Waypoints', {
            styleMap: pointStyles
        });
        map.addLayers([waypoints]);
        
        /* required to fire selection events on waypoints */
        var selectControl = new OpenLayers.Control.SelectFeature(waypoints,{
            id: 'selectControl'
        });
        map.addControl(selectControl);
        selectControl.activate();
        
        this.buildWaypointList(waypoints, selectControl);
        
        /* feature selection event handling */
        waypoints.events.register("featureselected", this, function(e) {
                var feature = e.feature;
                var fid = feature.fid;
                var feat = feature.clone();
                var attrs = feat.attributes;
                var files = attrs.media.files;
                var geom = feat.geometry.transform('EPSG:3857','EPSG:4326');
                var group = feat.attributes.route.group.name;
                
                // irish grid ref
                wgs84=new GT_WGS84();
                wgs84.setDegrees(geom.y, geom.x);
                irish=wgs84.getIrish();
                gridref = irish.getGridRef(3);
                $('#detail-panel-body').css('display','block');
                $('#detail-heading').html('<h5>' + attrs.name + '</h5>');
                $('.panel-body').find('span.description').html(attrs.description);
                // populate the carousel
                if (files.length > 0) {
                    // need to check for content_type here..
                    // and only add images to the carousel
                    $.each(files, function( index, file) {
                        var content_type = file.content_type.split('/')[0];
                        switch(content_type) {
                            case 'image':
                                var active = index === 0 ? 'active' : '';
                                var indicator = '<li data-target="#carousel" data-slide-to="' + index + '" class="' + active+ '"></li>';
                                var slide = '<div class="item ' + active + '">' +
                                            '<img src="' +  file.media_url + '"/>' +
                                            '</div>'
                                $('.carousel-inner').append(slide);
                                $('.carousel-indicators').append(indicator);
                                $('#carousel').css('display','block');
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
                $('.panel-body').find('span.latitude').html(geom.y.toFixed(4));
                $('.panel-body').find('span.longitude').html(geom.x.toFixed(4));
                $('.panel-body').find('span.irishgrid').html(gridref);
                $('.panel-body').find('span.created').html(moment(attrs.created).format('Do MMMM YYYY hh:mm a'));
                $('.panel-body').find('a.editlink').prop('href','/comap/waypoints/edit/' + fid);
                $('li[id=' + fid + ']').css('background-color','yellow').css('color', 'red');
                $('#deleteForm').prop('action', Config.WAYPOINT_API_URL + '/' + fid);
        });
        
        /* feature unselection event handling */
        waypoints.events.register("featureunselected", this, function(e){
            $('#detail-heading').html('<h5>Select a waypoint</h5>');
            $('#detail-panel-body').css('display','none');
            $('#carousel').css('display','none');
            $('.carousel-inner').empty();
            $('.carousel-indicators').empty();
            $('li.list-group-item').css('background-color','white').css('color','#526325');
            //$('li.list-group-item').append('<span class="glyphicon glyphicon-chevron-right pull-right"></span>');
            $('audio').css('display','none').empty();
            $.each($('audio'), function () {
                this.pause();
                this.currentTime = 0;
            });
            $.each($('video'), function () {
                videojs(this.id).dispose();
            });
            $('#video-panel').css('display','none').empty();
        });
        
        /* Add map controls */
        map.addControl(new OpenLayers.Control.ScaleLine());
        map.addControl(new OpenLayers.Control.LayerSwitcher());
        
        return map;
    },
    
    buildWaypointList: function(waypoints){
        var that = this;
        var selectControl = map.getControlsBy('id','selectControl')[0];
        var url = document.URL;
        var parts = url.split('/');
        var routeId = parts[6];
        console.log('Loading waypoints for route with id: ' + routeId);
        var waypointUrl = Config.WAYPOINT_API_URL + '.json?route_id=' + routeId;
        var routeName = '';
        var numWaypoints = 0;
        
        /* Get the Routes geojson */
        $.getJSON(Config.TRACK_API_URL + '/' + routeId + '.json', function(data, status, jqXHR) {
            var routeId = data.id;
            var props = data.properties;
            var waypts = data.properties.waypoints;
            routeName = data.properties.name;
            if (jqXHR.status == 200) { 
                var geojson = new OpenLayers.Format.GeoJSON({
                        'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                        'externalProjection': new OpenLayers.Projection("EPSG:4326")
                });
                var features = geojson.read(data);
                var route = new OpenLayers.Layer.Vector(routeName,{
                    style: {
                        'strokeWidth': 2.5,
                        'strokeColor': '#6e0004',
                        'strokeDashstyle': 'dash'
                    }
                });
                map.addLayers([route]);
                route.addFeatures(features);
                map.zoomToExtent(route.getDataExtent());
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
                    $('ul.list-group').append('<li class="list-group-item" id="' + id + '"><a class="route-link" id="' + id + '" href="#">' + name + '</a></li>');
                });
                var geojson = new OpenLayers.Format.GeoJSON({
                        'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                        'externalProjection': new OpenLayers.Projection("EPSG:4326")
                });
                var features = geojson.read(waypts);
                waypoints.addFeatures(features);
                selectControl.unselectAll();
                waypoints.events.triggerEvent('featureunselected');
                
            }
            $( "#list a" ).bind( "click", function() {
                var fid = $(this).attr("id");
                var feature = waypoints.getFeatureByFid(fid);
                selectControl.unselectAll();
                selectControl.select(feature);
            });
        });
    },
    
    buildDeleteDialog: function(){
        
        var that = this;
        var options = {
            dataType: 'json',
            beforeSubmit: function(arr, $form, options) {
                console.log('in before submit..');
            },
            success: function(data, status, xhr) {
                console.log(status);
                if (status == 'nocontent') {
                    waypoints = map.getLayersByName('Waypoints')[0]
                    waypoints.destroyFeatures();
                    that.buildWaypointList(waypoints);
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
});





