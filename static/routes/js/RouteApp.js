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

var RouteApp = OpenLayers.Class({
    
    initialize: function(){  
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
                scales:[500000,350000,250000,100000,25000,20000,15000,10000,5000,2500],   
                units: 'm',
        }

        map = new OpenLayers.Map('map', {options: mapOptions});
        
        var bing_aerial = Layers.BING_AERIAL;
        var tf_outdoors = Layers.OUTDOORS;
        var townlands = Layers.OSM_TOWNLANDS;
        
        bing_aerial.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        map.addLayers([tf_outdoors, bing_aerial]);
        bing_aerial.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: true};
        map.addLayers([tf_outdoors, bing_aerial, townlands]);
        
        /* Styles */
        var defaultStyle = new OpenLayers.Style({
            strokeColor: "#db337b",
            strokeWidth: 2.5,
            strokeDashstyle: "dash"
        });
        
        var selectStyle = new OpenLayers.Style({
            strokeColor: "yellow",
            strokeWidth: 3.5,
            strokeDashstyle: "dashdot",
            label: '${name}',
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
        
        /* Add the routes for the current group */
        var routes = new OpenLayers.Layer.Vector('Routes', {
            styleMap: lineStyles
        });
        map.addLayers([routes]);
        
        /* required to fire selection events on routes */
        var selectControl = new OpenLayers.Control.SelectFeature(routes,{
            id: 'selectControl'
        });
        map.addControl(selectControl);
        selectControl.activate();
        
        this.buildRouteList(routes, selectControl);
        
        this.buildDeleteDialog();
        
        /* feature selection event handling */
        routes.events.register("featureselected", this, function(e) {
                var feature = e.feature;
                var fid = feature.fid;
                var feat = feature.clone();
                var attrs = feat.attributes;
                var geom = feat.geometry.transform('EPSG:3857','EPSG:4326');
                $('#detail-panel-body').css('display','block');
                $('#detail-heading').html('<h5>' + attrs.name + '</h5>');
                if (!attrs.image_path == 'none_provided') {
                    $('.panel-body').find('span.image').html('<img id="info" src="/comap/media/' + attrs.image_path + '"/>');
                }
                $('.panel-body').find('span.description').html(attrs.description);
                $('.panel-body').find('span.created').html(moment(attrs.created).format('Do MMMM YYYY hh:mm a'));
                $('.panel-body').find('a.editlink').prop('href','/comap/routes/edit/' + fid);
                $('.panel-body').find('a.download').prop('href',attrs.gpx_url);
                $('.panel-body').find('a.waypointlink').prop('href','/comap/waypoints/list/' + fid);
                $('li[id=' + fid + ']').css('background-color','yellow').css('color', 'red');
                $('#deleteForm').prop('action', Config.TRACK_API_URL + '/' + fid);
                
        });
        
        /* feature unselection event handling */
        routes.events.register("featureunselected", this, function(e){
            $('#detail-heading').html('<h5>Select a route</h5>');
            $('#detail-panel-body').css('display','none');
            $('li.list-group-item').css('background-color','white').css('color','#526325');
        });
        
        /* Add map controls */
        map.addControl(new OpenLayers.Control.ScaleLine());
        map.addControl(new OpenLayers.Control.LayerSwitcher());
        
        return map;
    },
    
    buildRouteList: function(routes){
        var that = this;
        var selectControl = map.getControlsBy('id','selectControl')[0];
        // get the routes from the tracks api and build the page..
        $.getJSON(Config.TRACK_API_URL, function(data){
            var feats = data.features;
            var foundGroups = [];
            $.each(feats, function(i){
                var group = feats[i].properties.group.name;
                foundGroups.push(group);
            });
            var groups = _.uniq(foundGroups);
            $('#routes').empty();
            $.each(groups, function(i){
                var group = groups[i];
                var groupId = group.replace(' ', '-').toLowerCase();
                var html =  '<div class="panel panel-default">' +
                                '<div id="heading-wrap" class="panel-heading"><span class="glyphicon-heading glyphicon glyphicon-list pull-left">&nbsp</span>' +
                                    '<div id="heading"><h5>' + group + '</h5></div></div>' +
                                '<div id="panel" class="panel-body"><p>Here is a list of Routes for ' + group + '</div>' +
                                '<ul id="' + groupId + '"' + 'class="list-group"></ul>' +
                            '</div>';
                $('#routes').append(html);
                $.each(feats, function(j){
                    var feature = feats[j];
                    var name = feature.properties.name;
                    var id = feature.id;
                    var featGroup = feature.properties.group.name;
                    if (group === featGroup) {
                        $('ul#' + groupId).append('<li class="list-group-item" id="' + id + '"><a class="route-link" id="' + id + '" href="#">' + name + '</a></li>'); 
                    }
                });
            });
            $('#routes').append('<div id="create-link" class="listlink"></div>');
            $('#create-link').html('<a class="listlink" href="/comap/routes/create/"><button class="btn btn-success"><span class="glyphicon glyphicon-plus"></span> Add a new Route</button></a>');
            $('#routes-map-panel').css('visibility','visible');
            $('#detail-panel').css('visibility','visible');
            $('#detail-panel-body').css('display','none');
            //var group = feats[0].properties.group.name;
            //var heading = '<h5>' + group + '</h5>';
            //$('#heading').html(heading);
            //$('#panel').html('<p>Here is a list of Routes for ' + group + '</p>');
            
            // add waypoints to the list..
            /*
            $('ul.list-group').empty();
            $.each(feats, function(i){
                var name = feats[i].properties.name;
                var id = feats[i].id;
                $('ul.list-group').append('<li class="list-group-item" id="' + id + '"><a class="route-link" id="' + id + '" href="#">' + name + '</a></li>');
            });
            */
            var geojson = new OpenLayers.Format.GeoJSON({
                    'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                    'externalProjection': new OpenLayers.Projection("EPSG:4326")
            });
            var features = geojson.read(data);
            routes.addFeatures(features);
            map.zoomToExtent(routes.getDataExtent());
            $( "a.route-link" ).bind( "click", function() {
                var fid = $(this).attr("id");
                var feature = routes.getFeatureByFid(fid);
                selectControl.unselectAll();
                selectControl.select(feature);
            });
            
        }).fail(function(data){
            if (data.status == 404) {
                var message = data.responseJSON.detail;
                console.log(message);
                $('#routes-map-panel').css('display','none');
                //$('#map').css('display','none');
                $('ul.list-group').css('display','none');
                $('#detail-panel').css('display','none');
                $('#detail-panel-body').css('display','none');
                $('#create-link').empty();
                var heading = '<h5>No Routes Found</h5>';
                var panelText = '<h5>' + message + '</h5>';
                $('#heading').html(heading);
                $('#panel').html(panelText);
                $('#panel').append('<p><span><strong><hr/></p>');
                $('#panel').append('<p>');
                $('#panel').append('<a class="listlink" href="/comap/routes/create/"><button class="btn btn-success"><span class="glyphicon glyphicon-plus"></span> Add a new Route</button></a>');
                $('#panel').append('</p>');
            }
            else {
                console.log('Crap.. something went wrong there...');
            }
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
                    routes = map.getLayersByName('Routes')[0]
                    routes.destroyFeatures();
                    that.buildRouteList(routes);
                } 
            },
            error: function(xhr, status, error){
                var json = xhr.responseJSON
                errors = json.errors;
                console.log(errors);
            },
        }
        
        var modalOpts = {
            keyboard: true,
            backdrop: 'static',
        }
        
        $("#btnDelete").click(function(){
            $("#deleteRouteModal").modal(modalOpts, 'show');
        });
        
        $("#deleteConfirm").click(function(){
            $('#deleteForm').ajaxSubmit(options);
            $("#deleteRouteModal").modal('hide');
        });
        
    }
    
});





