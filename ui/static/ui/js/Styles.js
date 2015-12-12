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

var style = {};

/* Route styles */

style.route = (function() {

    var default_styles = [
        new ol.style.Style({
            stroke: new ol.style.Stroke({
                color: "#db337b",
                width: 2.5,
            })
        })
    ];

    var select_styles = [
        new ol.style.Style({
            stroke: new ol.style.Stroke({
                color: "#6B9430",
                width: 3.5,
            })
        })
    ];

    return {
        DEFAULT: default_styles,
        SELECT: select_styles
    }

}());

/* Waypoint styles */

style.waypoint = (function() {

    var default_styles = [
        new ol.style.Style({
            image: new ol.style.Circle({
                radius: 7,
                fill: new ol.style.Fill({
                    color: 'green'
                }),
                stroke: new ol.style.Stroke({
                    color: "#980000",
                    width: 2.5,
                }),
            })
        })
    ];


    function selectWaypoint(feature, resolution) {
        var geom = feature.getGeometry();
        if (geom.getType() == 'Point') {
            var text = feature.get('name');
            var label = style.text.BASE;
            label.setText(text);
            var select_styles = [
                new ol.style.Style({
                    text: label,
                    image: new ol.style.Circle({
                        radius: 10,
                        fill: new ol.style.Fill({
                            color: 'yellow'
                        }),
                        stroke: new ol.style.Stroke({
                            color: "#980000",
                            width: 2.5,
                        })
                    })
                })
            ];
            return select_styles;
        }
    }

    return {
        DEFAULT: default_styles,
        SELECT: selectWaypoint
    }

}());


/* Text styles */

style.text = (function() {

    textStyle = new ol.style.Text({
        font: '14px Ubuntu,sans-serif',
        textAlign: 'center',
        offsetY: -20,
        fill: new ol.style.Fill({
            color: [0, 0, 0, 1]
        }),
        stroke: new ol.style.Stroke({
            color: [255, 255, 255, 0.5],
            width: 4
        })
    });

    return {
        BASE: textStyle
    }

}());





/*

 var selectPointStyle = new OpenLayers.Style({
    pointRadius: 10,
    fillColor: "#6B9430",
    label: " ${name}",
    labelAlign: "lm",
    labelXOffset: "20",
    labelOutlineColor: "white",
    labelOutlineWidth: 3,
    fontSize: 16,
    graphicZIndex: 10,
});

*/
