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

var RouteMap = OpenLayers.Class({
    
    initialize: function(){
        // required
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
                style: new OpenLayers.Style({'strokeWidth': 5, 'strokeColor': '#980000'}),
        });
        
        var waypoints = new OpenLayers.Layer.Vector("Waypoints", {
            strategies: [new OpenLayers.Strategy.Fixed()],
            protocol: new OpenLayers.Protocol.HTTP({
                url: "/comap/api/waypoints.json",
                format: new OpenLayers.Format.GeoJSON(),
            }),
            styleMap: pointStyles
        });
        map.addLayers([waypoints]);
        
        /* required to fire selection events on heritage_waypoints */
        var selectControl = new OpenLayers.Control.SelectFeature(waypoints);
        map.addControl(selectControl);
        selectControl.activate();
        
        /* feature selection event handling */
        waypoints.events.register("featureselected", this, function(e) {
                /* get feature attributes */
                var feature = e.feature;
                var fid = feature.fid;
                var feat = feature.clone();
                var attrs = feat.attributes;
                var geom = feat.geometry.transform('EPSG:3857','EPSG:4326');
                
                $('#instructions').css('display','none');
                $('#info').css('display','block');
                $('#info').find('span.name').html('<h4>' + attrs.name + '</h4>');
                $('#info').find('span.image').html('<img id="info" src="/comap/media/' + attrs.image_path + '"/>');
                $('#info').find('span.description').html(attrs.description);
                $('#info').find('span.elevation').html(Math.floor(attrs.elevation) + ' metres');
                $('#info').find('span.latitude').html(geom.y.toFixed(6));
                $('#info').find('span.longitude').html(geom.x.toFixed(6));
                $('#info').find('a.editlink').prop('href','/comap/waypoints/edit/' + fid);
                
                $('li[id=' + attrs.fid + ']').css('background-color','yellow').css('color', 'red');
                
                /* update the submit url on the delete form once we know what the fid is */
                $('#deleteForm').prop('action','/comap/api/waypoints/' + fid);
                
        });
        
        /* feature unselection event handling */
        waypoints.events.register("featureunselected", this, function(e){
                $('#info').css('display','none');
                $('#instructions').css('display','block');
                $('li.list-group-item').css('background-color','white').css('color','#526325');
        });
        
        /* Add map controls */
        map.addControl(new OpenLayers.Control.ScaleLine());
        map.addControl(new OpenLayers.Control.LayerSwitcher());
        
        map.zoomToExtent(new OpenLayers.Bounds(-8.06,52.94,-7.92,53.01).transform("EPSG:4326", "EPSG:3857"));  
        waypoints.events.register('loadend', waypoints, function(evt){map.zoomToExtent(waypoints.getDataExtent())})
        
        /* handle route loading via hyperlink click */
        $("#list a").click(function(){
            var fid = $(this).attr("id");
            var feature = waypoints.getFeatureByFid(fid);
            selectControl.unselectAll();
            selectControl.select(feature);
        });
        
        return map;
    },
});





