$(function () {
    'use strict';
    $('#fileupload')
        .fileupload({
            dataType: 'json',
            autoUpload: true,
            singleFileUploads: true,
            maxChunkSize: 10000000, // 10MB
            maxFileSize: 100000000, // 1000MB
        })

        .on('fileuploadsubmit', function (e, data) {
            var $this = $(this);
            $.ajax({
                type: 'POST',
                url: '/+upload/new',
                data: JSON.stringify({
                    filename: data.files[0].name,
                size: data.files[0].size,
                type: data.files[0].type
                }),
                contentType: 'application/json',
                success: function (result) {
                    data.url = result.url;
                    $this.fileupload('send', data);
                }
            });
            return false;
        })

        .on('fileuploadadd', function (e, data) {
            data.context = $('<div class="alert alert-processing"/>').appendTo('#files');
            $.each(data.files, function (index, file) {
                var node = $('<p/>')
                    .append($('<span/>').text(file.name));
                node.appendTo(data.context);
            });
        })

        .on('fileuploaddone', function (e, data) {
            $(data.context)
                .attr('class', 'alert alert-success')
            $.each(data.result.files, function (index, file) {
                $(data.context.children()[index]) = $('<a>')
                    .attr('target', '_blank')
                    .prop('href', file.url);
            })
        })

        .on('fileuploadfail', function (e, data) {
            $(data.context)
                .attr('class', 'alert alert-danger')
                .append('<p><strong>Upload failed!</strong></p>');
        })

        .on('fileuploadprogressall', function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            $('#fileupload-progress .progress-bar').css('width', progress + '%');
        })

        .on('fileuploadstart', function (e, data) {
            $('#fileupload-progress').css('visibility', 'visible');
        })

        .on('fileuploadstop', function (e, data) {
            $('#fileupload-progress').css('visibility', 'hidden');
        })

        .on('fileuploadprocessalways', function (e, data) {
            var index = data.index,
                file = data.files[index],
                node = $(data.context.children()[index]);
            if (file.error) {
                node
                    .append('<br>')
                    .append('<strong>' + file.error + '</strong>')
                    .wrap("<div class='alert alert-danger'></div>");
            }
            if (index + 1 === data.files.length) {
                data.context.find('button')
                    .text('Upload')
                    .prop('disabled', !!data.files.error);
            }
        })

        .prop('disabled', !$.support.fileInput)
        .parent().addClass($.support.fileInput ? undefined : 'disabled');
});
