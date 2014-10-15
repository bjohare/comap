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

var IndexMap = OpenLayers.Class({
    
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
                    url: "/map/?map=/home/ubuntu/mapfiles/heritage-south-cycle-route.map",
                    featureType: ["heritage_cycle_route_south"]}),
                box: false,
                style: new OpenLayers.Style({'strokeWidth': 5, 'strokeColor': '#980000'}),
        });
	
        
        var heritage_waypoints = new OpenLayers.Layer.Vector("Heritage Cycle Route South", {
                srsName: "EPSG:4326",
                strategies: [new OpenLayers.Strategy.BBOX()],
                protocol: new OpenLayers.Protocol.WFS({
                    url: "/map/?map=/home/ubuntu/mapfiles/heritage-south-cycle-route.map",
                    featureType: ["heritage_cycle_route_south_waypoints"]}),
                box: false,
                styleMap: pointStyles
            });
        map.addLayers([heritage_route, heritage_waypoints]);
        
        
        /* required to fire selection events on heritage_waypoints */
        var selectControl = new OpenLayers.Control.SelectFeature(heritage_waypoints);
        map.addControl(selectControl);
        selectControl.activate();
        
          
        /* Override GetFeature selectClick */
        OpenLayers.Control.GetFeature.prototype.selectClick = function(evt) {
            var bounds = this.pixelToBounds(evt.xy);
            var baseSRS = this.map.getProjectionObject();
            var layerSRS = new OpenLayers.Projection('EPSG:4326');
            bounds.transform(baseSRS, layerSRS);
            this.setModifiers(evt);
            this.request(bounds, {single: this.single});
        }
            
        var infoctl = new OpenLayers.Control.GetFeature({
                protocol: OpenLayers.Protocol.WFS({
                    url: "/map/?map=/home/ubuntu/mapfiles/heritage-south-cycle-route.map",
                    featureType: "heritage_cycle_route_south_waypoints",
                    featurePrefix: "ms",
                    maxFeatures: 10,
                    formatOptions: {
                        outputFormat: "text/xml"
                    }
                }),
                clickTolerance: 10
        });
        
        
        /* feature selection event handling */
        infoctl.events.register("featureselected", this, function(e) {
                /* get feature attributes */
                var feature = e.feature;
                attrs = feature.attributes;
                
                /* center the map on the selected waypoint */
                var center = new OpenLayers.LonLat(attrs.longitude, attrs.latitude);
                center.transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
                map.setCenter(center,13);
                
                /* clear existing feature info and rebuild */
                $('#info').empty();
                $('#info').append('<h4>' + attrs.name + '</h4>');
                $('#info').append('<p><img id="info" src="/comap/media/' + attrs.image_path + '"/></p>');
                $('#info').append('<p>' + attrs.description + '</p>');
                $('#info').append('<strong>Elevation:</strong> ' + attrs.elevation.split('.')[0] + ' metres<br/>');
                $('#info').append('<strong>Latitude:</strong> ' + attrs.latitude + '<br/>');
                $('#info').append('<strong>Longitude:</strong> ' + attrs.longitude);
                $('#info').append('<p>');
                $('#info').append('<a href="/comap/waypoints/edit/' + attrs.fid + '/"><button><span class="glyphicon glyphicon-edit"></span> Edit this waypoint</button>');
                $('#info').append('<a href="/comap/waypoints/delete/' + attrs.fid + '/">&nbsp;<button><span class="glyphicon glyphicon-remove"></span> Delete this waypoint</button>');
                $('#info').append('</p>');
                $('li[id=' + attrs.fid + ']').css('background-color','yellow').css('color', 'red');
                
        });
        
        /* feature unselection event handling */
        infoctl.events.register("featureunselected", this, function(e){
                $('#info').empty();
                $('#info').append('<span>Select waypoint name or a point on the map to get started...</span>');
                $('li.list-group-item').css('background-color','white').css('color','#526325');
        });
        
        
        /* Add GetFeature Control to map and activate */
        map.addControl(infoctl);
        infoctl.activate();
        
        /* Add map controls */
        map.addControl(new OpenLayers.Control.ScaleLine());
        map.addControl(new OpenLayers.Control.LayerSwitcher());
        
        map.zoomToExtent(new OpenLayers.Bounds(-8.06,52.94,-7.92,53.01).transform("EPSG:4326", "EPSG:900913"));  
        heritage_waypoints.events.register('loadend', heritage_waypoints, function(evt){map.zoomToExtent(heritage_waypoints.getDataExtent())})
        
        // populate info div with user instructions..
        $('#info').append('<span>Select waypoint name or a point on the map to get started...</span>');
        
        /* handle feature selection via hyperlink */
        $("#list a").click(function(){
            var id = $(this).attr("id");
            feature = heritage_waypoints.getFeaturesByAttribute('fid', id)[0];
            selectControl.unselectAll();
            selectControl.select(feature);
            infoctl.setModifiers(null); // throws null pointer if not set
            infoctl.select([feature]);
        });
        
    },
    
});





