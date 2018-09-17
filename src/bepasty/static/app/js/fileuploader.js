jqXHR = {};
$(function () {
    'use strict';

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

    $('#fileupload')
        .fileupload({
            dataType: 'json',
            autoUpload: true,
            singleFileUploads: true,
            maxChunkSize: MAX_BODY_SIZE,
            maxFileSize: MAX_ALLOWED_FILE_SIZE
        })

        .on('fileuploadadd', function (e, data) { })

        .on('fileuploadsubmit', function (e, data) {
            var $this = $(this);
            var file = data.files[0]
            // Create new item
            $.ajax({
                type: 'POST',
                url: UPLOAD_NEW_URL,
                data: JSON.stringify({
                    filename: file.name,
                    size: file.size,
                    type: file.type,
                    maxlife_unit: $("select[name=maxlife-unit] option:selected").val(),
                    maxlife_value: $("input[name=maxlife-value]").val()
                }),
                contentType: 'application/json',
                success: function (result) {
                    data.url = result.url;

                    data.context = $('<div class="alert alert-processing"/>')
                        .appendTo('#files');

                    var abortButton = $('<button id="' + result.name + '" class="'
                        + ' fileupload-abort btn btn-danger"/>').text('abort');
                    abortButton.appendTo(data.context);

                    abortButton.click(function (e) {
                        jqXHR[result.name].abort();
                        abortButton.css('display', 'none')
                    });

                    var fileItem = $('<p/>').text(file.name);
                    fileItem.append(' <span class="break-word">('
                        + humansize(file.size)
                        + ')</span>');
                    fileItem.appendTo(data.context);

                    var _jqXHR = $this.fileupload('send', data);
                    _jqXHR.error(function (jqXHR, textStatus, errorThrown) {
                            //Delete file garbage on server
                            $.ajax({
                                type: 'GET',
                                url: data.url+'/abort'
                            });
                        });
                    jqXHR[result.name] = _jqXHR;
                }
            });
            return false;
        })

        .on('fileuploaddone', function (e, data) {
            $(data.context)
                .attr('class', 'alert alert-success');
            $.each(data.result.files, function (index, file) {
                $(data.context[0].childNodes[1])
                    .wrapInner($('<a target="_blank" class="alert-link">')
                        .prop('href', file.url));
                $('#filelist').append(file.name + "\n");
                delete jqXHR[file.name];
                $('#' + file.name).css('display', 'none');
            });
            $('#filelist-form').show();
        })

        .on('fileuploadfail', function (e, data) {
            $(data.context)
                .attr('class', 'alert alert-danger')
                .append('<p><strong>Upload failed!</strong></p>');
            var name = data.url.split('/').pop();
            delete jqXHR[name];
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
            var progressBar = $('#fileupload-progress')
            progressBar.css('visibility', 'hidden');
            progressBar.find('.progress-bar').css('width', 0 + '%');
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
                for (var key in jqXHR) {
                    jqXHR[key].abort();
                    $('#' + key).css('display', 'none');
                }
            }
            $('#fileupload-progress').find('.progress-bar').css('width', 0 + '%');
        });
    });
});
