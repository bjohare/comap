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

var route = {};

route.list = (function() {

    var map = null;
    var routes = null;
    var select = null;

    return {
        init: function() {
            _initMap();
            _buildDeleteDialog();
        }
    }

    function _initMap() {

        /* Layers */

        // osm
        var osm = new ol.layer.Tile({
            title: 'OpenStreetMap',
            source: new ol.source.OSM()
        });

        // routes
        routes = new ol.layer.Vector({
            title: 'Routes',
            style: style.route.DEFAULT,
            projection: 'EPSG:3857'
        });

        // controls
        var scaleline = new ol.control.ScaleLine();

        // interactions
        select = new ol.interaction.Select({
            style: style.route.SELECT
        })

        // view
        var view = new ol.View({
            center: [0, 0],
            zoom: 2
        });

        // map
        map = new ol.Map({
            layers: [osm, routes],
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
            map.getView().fit(routes.getSource().getExtent(), map.getSize());
        });

        /* Build the route list. */
        _buildRouteList(routes);

        /* Handle feature selection events */
        select.getFeatures().on('add', function(e) {
            var feature = this.getArray()[0];
            var fid = feature.getId();
            var feat = feature.clone();
            var attrs = feat.getProperties();
            map.getView().fit(feature.getGeometry().getExtent(), map.getSize());
            $('#detail-panel-body').css('display', 'block');
            $('#detail-heading').html('<h5>' + attrs.name + '</h5>');
            if (!attrs.image_path == 'none_provided') {
                $('.panel-body').find('span.image').html('<img id="info" src="/comap/media/' + attrs.image_path + '"/>');
            }
            $('.panel-body').find('span.description').html(attrs.description);
            $('.panel-body').find('span.created').html(moment(attrs.created).format('Do MMMM YYYY hh:mm a'));
            $('.panel-body').find('a.editlink').prop('href', '/comap/routes/edit/' + fid);
            $('.panel-body').find('a.download').prop('href', attrs.gpx_url);
            $('.panel-body').find('a.waypointlink').prop('href', '/comap/waypoints/list/' + fid);
            $('li[id=' + fid + ']').css('background-color', '#6B9430').css('color', 'white');
            $('li[id=' + fid + '] a').css('color', 'white');
            $('#deleteForm').prop('action', Config.TRACK_API_URL + '/' + fid);
        });

        select.getFeatures().on('remove', function(e) {
            $('#detail-heading').html('<h5>Select a route</h5>');
            $('#detail-panel-body').css('display', 'none');
            $('li.list-group-item').css('background-color', 'white');
            $('li.list-group-item a').css('color', '#526325');
        });
    }


    function _buildRouteList(routes) {
        // get the routes from the tracks api and build the page..
        $.getJSON(Config.TRACK_API_URL, function(data) {
            var feats = data.features;
            var foundGroups = [];
            $.each(feats, function(i) {
                var group = feats[i].properties.group.name;
                foundGroups.push(group);
            });
            var groups = _.uniq(foundGroups);
            $('#routes').empty();
            $.each(groups, function(i) {
                var group = groups[i];
                var groupId = group.replace(/ /g, '-').toLowerCase();
                var html = '<div class="panel panel-default">' +
                    '<div id="heading-wrap" class="panel-heading"><span class="glyphicon-heading glyphicon glyphicon-list pull-left">&nbsp</span>' +
                    '<div id="heading"><h5>' + group + '</h5></div></div>' +
                    '<ul id="' + groupId + '"' + 'class="list-group"></ul>' +
                    '</div>';
                $('#routes').append(html);
                $.each(feats, function(j) {
                    var feature = feats[j];
                    var name = feature.properties.name;
                    var id = feature.id;
                    var featGroup = feature.properties.group.name;
                    if (group === featGroup) {
                        $('ul#' + groupId).append('<li class="list-group-item" id="' + id + '"><a class="route-link" id="' + id + '" href="#">' + name + '</a><span class="glyphicon glyphicon-chevron-right pull-right"></span></li>');
                    }
                });
            });
            $('#routes').append('<div id="create-link" class="listlink"></div>');
            $('#create-link').html('<a class="listlink" href="/comap/routes/create/"><button class="btn btn-success"><span class="glyphicon glyphicon-plus"></span> Add a new Route</button></a>');
            $('#routes-map-panel').css('visibility', 'visible');
            $('#detail-panel').css('visibility', 'visible');
            $('#detail-panel-body').css('display', 'none');

            // add the features to the map
            var geoJSONFormat = new ol.format.GeoJSON();
            var source = new ol.source.Vector({
                format: geoJSONFormat,
            });
            var features = geoJSONFormat.readFeatures(data, {
                dataProjection: 'EPSG:4326',
                featureProjection: 'EPSG:3857'
            });
            source.addFeatures(features);
            routes.setSource(source);
            var extent = routes.getSource().getExtent();
            map.getView().fit(extent, map.getSize());
            $("a.route-link").bind("click", function() {
                var fid = $(this).attr("id");
                var feature = routes.getSource().getFeatureById(fid);
                select.getFeatures().clear();
                select.getFeatures().push(feature);
            });

        }).fail(function(data) {
            if (data.status == 404) {
                var message = data.responseJSON.detail;
                console.log(message);
                $('#routes-map-panel').css('display', 'none');
                //$('#map').css('display','none');
                $('ul.list-group').css('display', 'none');
                $('#detail-panel').css('display', 'none');
                $('#detail-panel-body').css('display', 'none');
                $('#create-link').empty();
                var heading = '<h5>No Routes Found</h5>';
                var panelText = '<h5>' + message + '</h5>';
                $('#heading').html(heading);
                $('#panel').html(panelText);
                $('#panel').append('<p><span><strong><hr/></p>');
                $('#panel').append('<p>');
                $('#panel').append('<a class="listlink" href="/comap/routes/create/"><button class="btn btn-success"><span class="glyphicon glyphicon-plus"></span> Add a new Route</button></a>');
                $('#panel').append('</p>');
            } else {
                console.log('Crap.. something went wrong there...');
            }
        });
    }

    function _buildDeleteDialog() {
        var options = {
            dataType: 'json',
            beforeSubmit: function(arr, $form, options) {
                console.log('in before submit..');
            },
            success: function(data, status, xhr) {
                console.log(status);
                if (status == 'nocontent') {
                    routes.getSource().clear();
                    _buildRouteList(routes);
                }
            },
            error: function(xhr, status, error) {
                var json = xhr.responseJSON
                errors = json.errors;
                console.log(errors);
            },
        }

        var modalOpts = {
            keyboard: true,
            backdrop: 'static',
        }

        $("#btnDelete").click(function() {
            $("#deleteRouteModal").modal(modalOpts, 'show');
        });

        $("#deleteConfirm").click(function() {
            $('#deleteForm').ajaxSubmit(options);
            $("#deleteRouteModal").modal('hide');
        });

    }

}());

$(document).ready(function() {
    route.list.init();
});
