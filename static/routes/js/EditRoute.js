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

var EditRoute = OpenLayers.Class({
    
    initialize: function(){
        
        var url = document.URL;
        var parts = url.split('/');
        var id = parts[6];
        console.log('Loading track with id: ' + id);
        var jsonUrl = Config.TRACK_API_URL + '/' + id + '.json';
        console.log(jsonUrl);
        var that = this;
        $.getJSON(jsonUrl, function(data){
            var props = data.properties;
            var groupId = props.group.id;
            if (props.length === 0) {
                alert('No features found');
            }
            else {
                $('#fid').val(id);
                $('#name').val(props.name);
                $('#description').val(props.description);
                $('#editGpxForm').css('display','block');
                $('option[value="' + props.group.id +'"]').prop('selected','true');
            }
            that.buildGroupSelect(groupId);
        }).fail(function(data){
            alert('Failed.. do something here..');
        });
        
        this.initForm();
    },
    
    initForm: function(){
        
        $('#editGpxForm').formValidation({
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
                /*
                gpxfile: {
                    validators: {
                        notEmpty: {
                            message: 'Please provide a valid GPX file.'
                        }
                    }
                },
                */
                group: {
                    validators: {
                        notEmpty: {
                            message: 'Please choose an owner for this Route.'
                        }
                    }
                }
                
            }
        });
        
        var progressbar = $('#progressbar').progressbar();
        $('#progressbar').css("display","none");
        $('#editGpxForm').ajaxForm({
            beforeSubmit: function(arr, $form, options) {
                this.url = Config.TRACK_API_URL + '/' + $('#fid').val();
                $('#progressbar').css("display","block");
            },
            uploadProgress: function(event, position, total, percentComplete) {
                progressbar.progressbar({value: percentComplete});
            },
            success: function(data, status, xrh) {
                $('#progressbar').css("display","none");
                $('#update-route').css('display','none');
                console.log('Updated Route.')
                props = xrh.responseJSON.properties;
                var id = xrh.responseJSON.id;
                $('#update-info').css("display", "block");
                $('#update-info-heading').append('<h4>Route updated successfully</h4>');
                $('#update-info-panel').append('<p><span><strong>Route name:</strong> ' + props.name + '</span></p>');
                $('#update-info-panel').append('<p><span><strong>Description:</strong> ' + props.description + '</span></p>');
                $('#update-info-panel').append('<p><span><strong>Updated:</strong> ' +moment(props.created).format('Do MMMM YYYY hh:mm a') + '</span></p>');
                $('#update-info-panel').append('<p><span><strong>Group:</strong> ' + props.group.name + '</span></p>');
                $('#update-info-panel').append('<p><span><strong>Updated by:</strong> ' + props.user.username + '</span></p>');
                $('#update-info-panel').append('<p><span><strong><hr/></p>');
                $('#update-info-panel').append('<p>');
                $('#update-info-panel').append('<a class="editlink" href="/comap/routes/edit/' + id + '"><button><span class="glyphicon glyphicon-edit"></span> Edit this Route..</button></a> &nbsp;');
                $('#update-info-panel').append('<a class="listlink" href="/comap/routes/"><button><span class="glyphicon glyphicon-list"></span> List Routes..</button></a> &nbsp;');
                $('#update-info-panel').append('<a class="listlink" href="/comap/routes/create/"><button><span class="glyphicon glyphicon-asterisk"></span> Create a new Route..</button></a>');
                $('#update-info-panel').append('</p>');
            },
            error: function(xhr, status, error){
                console.log('Failed to update route..');
                $('#progressbar').css("display", "none");
                $('#info').empty();
                var json = xhr.responseJSON
                console.log(json);
                $('#info').addClass('error');
                $('#info').append('<h3>Please correct these errors:</h3>');
            },
        });
    },
    
    buildGroupSelect: function(groupId){
        this.groupId = groupId;
        var that = this;
        $.getJSON(Config.USER_API_URL, function(data){
            var groups = data[0].groups;
            if (groups.length > 1) {
                var select = '<select id="group" class="form-control" name="group">';
                $.each(groups, function(i){
                    var group = groups[i];
                    if (group.id === that.groupId) {
                        select = select + '<option value="' + group.id + '" selected>' + group.name + '</option>';
                    }
                    else {
                        select = select + '<option value="' + group.id + '">' + group.name + '</option>'; 
                    }
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
});
