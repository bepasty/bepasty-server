$(function () {
    'use strict';
    var url = window.location.hostname === '/+upload/json' ?
        '//+upload/json' : '/+upload/json'
    $('#fileupload').fileupload({
        url: url,
        dataType: 'json',
        autoUpload: true,
        maxFileSize: 100000000 // 100 MB
    }).on('fileuploadadd',function (e, data) {
            data.context = $('<div/>').appendTo('#files');
            $.each(data.files, function (index, file) {
                var node = $('<p/>')
                    .append($('<span/>').text(file.name));
                node.appendTo(data.context);
            });
        }).on('fileuploadprocessalways',function (e, data) {
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
        }).on('fileuploadprogressall',function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 15);
            $('#progress .progress-bar').css(
                'width',
                progress + '%'
            );
        }).on('fileuploaddone',function (e, data) {
            $.each(data.result.files, function (index, file) {
                var link = $('<a>')
                    .attr('target', '_blank')
                    .prop('href', file.url);
                $(data.context.children()[index])
                    .wrap(link)
                    .wrap("<div class='alert alert-success'></div>");
            });
        }).on('fileuploadfail',function (e, data) {
            $.each(data.result.files, function (index, file) {
                var error = $('<span/>').text(file.error);
                $(data.context.children()[index])
                    .append('<br>')
                    .append('<strong>' + error + '</strong>')
                    .wrap("<div class='alert alert-danger'></div>");
            });
        }).prop('disabled', !$.support.fileInput)
        .parent().addClass($.support.fileInput ? undefined : 'disabled');
});