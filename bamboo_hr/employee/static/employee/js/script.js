/**
* BAMBOO HR
* Md. Hasan Shahriar
* 14/7/2017
*/
$(document).ready(function(){
    // Date picker
    $('input.datepicker').Zebra_DatePicker();

    // Drag file select
    $('input[type="file"]').ezdz();

    // username selction
    $('.employee_id_show').text($('#employee_id').val());

    // form buttons
    $(document).on( 'click', '.rename-btn button', function(){
        var emp = $('#employee_id option:selected').text();
        var dt = $('#signed_date').val();
        var tmp = $('#category_id option:selected').text();
        var fd = tmp.split("-")[0];
        var ft = tmp.split("-")[1];
        $('.file-upload-alert .alert-content').html('<p>Confirm file upload:</p><p><b>Employee Name: '+emp+'</b></p><p><b>Signed date: '+dt+'</b></p><p><b>Folder: '+fd+'</b></p><p><b>File type: '+ft+'</b></p>');
        $('.file-upload-alert, .confirm-btn').show();
        $('.rename-btn').hide();
    });

    // file upload message
    $(document).on( 'click', '.file-upload-alert .hide-alert', function(e){
        $('.rename-btn').show();
        $('.confirm-btn, .file-upload-alert').hide();
    });

});