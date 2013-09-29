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

        .on('fileuploadstart', function (e, data) {
            $('#fileupload-progress').css('visibility', 'visible');
        })

        .on('fileuploadstop', function (e, data) {
            $('#fileupload-progress').css('visibility', 'hidden');
        })

        .on('fileuploadfail', function (e, data) {
            $(data.context.children()[0])
                .append('<br>')
                .append('<strong>Upload failed!</strong>')
                .wrap("<div class='alert alert-danger'></div>");
        })

        .on('fileuploadadd', function (e, data) {
            data.context = $('<div/>').appendTo('#files');
            $.each(data.files, function (index, file) {
                var node = $('<p/>')
                    .append($('<span/>').text(file.name));
                node.appendTo(data.context);
            });
        })

        .on('fileuploadprocessalways', function (e, data) {
            console.log("processalways")
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

        .on('fileuploadprogressall', function (e, data) {
            console.log("progressall")
            var progress = parseInt(data.loaded / data.total * 100, 10);
            $('#fileupload-progress .progress-bar').css('width', progress + '%');
        })

        .on('fileuploaddone', function (e, data) {
            console.log("done")
            $.each(data.result.files, function (index, file) {
                var link = $('<a>')
                    .attr('target', '_blank')
                    .prop('href', file.url);
                $(data.context.children()[index])
                    .wrap(link)
                    .wrap("<div class='alert alert-success'></div>");
            })
        })

        .prop('disabled', !$.support.fileInput)
        .parent().addClass($.support.fileInput ? undefined : 'disabled');
});
