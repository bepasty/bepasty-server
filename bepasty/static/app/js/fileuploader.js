jqXHR = null;
$(function () {
    'use strict';
    $('#fileupload')
        .fileupload({
            dataType: 'json',
            autoUpload: true,
            singleFileUploads: true,
            maxChunkSize: 10 * 1024 * 1024, // 10 MiB
            maxFileSize: 4 * 1024 * 1024 * 1024 // 4 GiB
        })

        .on('fileuploadadd', function (e, data) {
            data.context = $('<div class="alert alert-processing"/>')
                .appendTo('#files');

            // Generate human readable file size
            function humansize (size) {
                var suffix = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"],
                    tier = 0;

                while (size >= 1024) {
                    size = size / 1024;
                    tier++;
                }

                return Math.round(size * 10) / 10 + " " + suffix[tier];
            }

            // Add one paragraph per file
            $.each(data.files, function (index, file) {
                var node = $('<p/>')
                    .text(file.name + " (" + humansize(file.size) + ")");
                node.appendTo(data.context);
            });
        })

        .on('fileuploadsubmit', function (e, data) {
            var $this = $(this);
            // Create new item
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
                    jqXHR = $this.fileupload('send', data);
                    jqXHR.error(function (jqXHR, textStatus, errorThrown)
                        {
                            //Delete file garbage on server
                            $.ajax({
                                type: 'GET',
                                url: data.url+'/abort'
                            });
                        });
                    }
            });
            return false;
        })

        .on('fileuploaddone', function (e, data) {
            $(data.context)
                .attr('class', 'alert alert-success');
            $.each(data.result.files, function (index, file) {
                $(data.context.children()[index])
                    .wrapInner($('<a target="_blank" class="alert-link">')
                        .prop('href', file.url));
                $('#filelist').append(file.name + "\n");
            });
            $('#filelist-form').show();
            jqXHR = null;
        })

        .on('fileuploadfail', function (e, data) {
            $(data.context)
                .attr('class', 'alert alert-danger')
                .append('<p><strong>Upload failed!</strong></p>');
            jqXHR = null;
        })

        .on('fileuploadprogressall', function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            $('#fileupload-progress').find('.progress-bar').css('width', progress + '%');
        })

        .on('fileuploadstart', function (e, data) {
            $('#fileupload-progress').css('visibility', 'visible');
            $('#fileupload-abort').css('visibility', 'visible')
        })

        .on('fileuploadstop', function (e, data) {
            $('#fileupload-progress').css('visibility', 'hidden');
            $('#fileupload-abort').css('visibility', 'hidden');
        })

        .on('fileuploadprocessfail', function (e, data) {
            $(data.context)
                .attr('class', 'alert alert-danger');
            var index = data.index,
                file = data.files[index];
            $(data.context.children()[index])
                .append('<br>')
                .append('<strong>' + file.error + '</strong>');
        });

    $('#fileupload-abort').click(function (e) {
        bootbox.confirm("Are you sure you want to abort the upload?", function(result) {
            if (result == true && jqXHR != null){
                jqXHR.abort();
            }
        });
    });
});
