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
                units: 'm',
        }

        map = new OpenLayers.Map('map', {options: mapOptions});
        
        var ocm = Layers.OCM;
        ocm.options = {layers: "basic", isBaseLayer: true, visibility: true, displayInLayerSwitcher: false};
        map.addLayers([ocm]);
        
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
            if (feats.length == 0) {
                $('#map').css('display','none');
                $('ul.list-group').css('display','none');
                $('#detail-panel').css('display','none');
                $('#detail-panel-body').css('display','none');
                $('#create-link').empty();
                var heading = '<h5>No Routes Found</h5>';
                //var panelText = '<h5>There are no routes for ' + group + '.</h5>';
                $('#heading').html(heading);
                //$('#panel').html(panelText);
                //$('#panel').append('<p><span><strong><hr/></p>');
                $('#panel').append('<p>');
                $('#panel').append('<a class="listlink" href="/comap/routes/create/"><button><span class="glyphicon glyphicon-asterisk"></span> Add a new route..</button></a>');
                $('#panel').append('</p>');
            }
            else {
                $('#map').css('visibility','visible');
                $('#detail-panel').css('visibility','visible');
                $('#detail-panel-body').css('display','none');
                var group = feats[0].properties.group;
                var heading = '<h5>' + group + '</h5>';
                $('#heading').html(heading);
                $('#panel').html('<p>Here is a list of Routes for ' + group + '</p>');
                $('#create-link').html('<a class="listlink" href="/comap/routes/create/"><button><span class="glyphicon glyphicon-asterisk"></span> Add a new route..</button></a>');
                // add waypoints to the list..
                $('ul.list-group').empty();
                $.each(feats, function(i){
                    var name = feats[i].properties.name;
                    var id = feats[i].id;
                    $('ul.list-group').append('<li class="list-group-item" id="' + id + '"><a class="route-link" id="' + id + '" href="#">' + name + '</a></li>');
                });
                var geojson = new OpenLayers.Format.GeoJSON({
                        'internalProjection': new OpenLayers.Projection("EPSG:3857"),
                        'externalProjection': new OpenLayers.Projection("EPSG:4326")
                });
                var features = geojson.read(data);
                routes.addFeatures(features);
                map.zoomToExtent(routes.getDataExtent());
            }
            $( "#list a" ).bind( "click", function() {
                var fid = $(this).attr("id");
                var feature = routes.getFeatureByFid(fid);
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
        
        $('#deleteRouteModal').modal({
            keyboard: true,
            backdrop: 'static',
        });
        
        $("#btnDelete").click(function(){
            $("#deleteRouteModal").modal('show');
        });
        
        $("#deleteConfirm").click(function(){
            $('#deleteForm').ajaxSubmit(options);
            $("#deleteRouteModal").modal('hide');
        });
        
    }
    
});





