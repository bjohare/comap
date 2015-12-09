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

route.create = (function() {

    return {
        init: initForm
    }

    function initForm(){

        $('#gpxForm').formValidation({
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
                            message: 'The route name is required and cannot be empty.'
                        },
                    }
                },
                description: {
                    validators: {
                        notEmpty: {
                            message: 'The description is required and cannot be empty.'
                        }
                    }
                },
                gpxfile: {
                    validators: {
                        notEmpty: {
                            message: 'Please provide a valid GPX file.'
                        }
                    }
                },
                group: {
                    validators: {
                        notEmpty: {
                            message: 'Please select the owner of this Route.'
                        }
                    }
                }
                
            }
        });

        _buildGroupSelect();

        var progressbar = $('#progressbar').progressbar();
        $('#progressbar').css("display","none");
        $('#gpxForm').ajaxForm({
            url: Config.TRACK_API_URL,
            beforeSubmit: function(arr, $form, options) {
                $('#progressbar').css("display","block");
            },
            uploadProgress: function(event, position, total, percentComplete) {
                progressbar.progressbar({value: percentComplete});
            },
            success: function(data, status, xrh) {
                $('#progressbar').css("display","none");
                $('#create-route').css('display','none');
                console.log('Created Route.')
                var props = xrh.responseJSON.properties;
                var id = xrh.responseJSON.id;
                $('#create-info').css("display", "block");
                $('#create-info-heading').append('<h4>Route created successfully</h4>');
                $('#create-info-panel').append('<p><span><strong>Route name:</strong> ' + props.name + '</span></p>');
                $('#create-info-panel').append('<p><span><strong>Description:</strong> ' + props.description + '</span></p>');
                $('#create-info-panel').append('<p><span><strong>Created:</strong> ' + moment(props.created).format('Do MMMM YYYY hh:mm a') + '</span></p>');
                $('#create-info-panel').append('<p><span><strong>Group:</strong> ' + props.group.name + '</span></p>');
                $('#create-info-panel').append('<p><span><strong>Created by:</strong> ' + props.user.username + '</span></p>');
                $('#create-info-panel').append('<p><span><strong><hr/></p>');
                $('#create-info-panel').append('<p>');
                $('#create-info-panel').append('<a class="editlink" href="/comap/routes/edit/' + id + '"><button><span class="glyphicon glyphicon-edit"></span> Edit this Route..</button></a> &nbsp;');
                $('#create-info-panel').append('<a class="listlink" href="/comap/routes/"><button><span class="glyphicon glyphicon-list"></span> List Routes..</button></a> &nbsp;');
                $('#create-info-panel').append('<a class="listlink" href="/comap/routes/create/"><button><span class="glyphicon glyphicon-asterisk"></span> Create a new Route..</button></a>');
                $('#create-info-panel').append('</p>');
            },
            error: function(xhr, status, error){
                $('#progressbar').css("display","none");
                $('#create-route').css('display','none');
                console.log('Route creation failed.')
                $('#create-info').css("display", "block");
                $('#create-info-heading').append('<h4>Failed to create the route</h4>');
                $('#create-info-panel').append('<p><span>There was an error during route creation. ' + xhr.statusText + '</span></p>');
                
    
            },
        });
    }

    function _buildGroupSelect(){
        $.getJSON(Config.USER_API_URL, function(data){
            var groups = data[0].groups;
            if (groups.length > 1) {
                var select = '<select id="group" class="form-control" name="group">';
                $.each(groups, function(i){
                    var group = groups[i];
                    select = select + '<option value="' + group.id + '">' + group.name + '</option>';
                });
                select = select + '</select>';
                $('#select-owner').append(select);
                $('#form-select-owner').css('display','block');
            }
            else {
                var input = '<input type="hidden" name="group" value="' + groups[0].id + '"/>';
                $('#select-owner').html(input);
            }
            $('#create-route-panel').css('display','block');
        }); 
    }


}());

$(document).ready(function() {
    route.create.init();
});