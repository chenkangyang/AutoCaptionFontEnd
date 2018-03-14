var ws;

function uploadSocket(obj) {
    // Connect to Web Socket
    ws = new WebSocket("ws://localhost:9001/");
    // Set event handlers.
    ws.onopen = function () {
        ws.send(obj);
    };

    ws.onmessage = function (e) {
        // e.data contains received string.
    };

    ws.onclose = function () {};
    ws.onerror = function (e) {
        console.log(e)
    };
}

function onprogress(evt) {　　
    var loaded = evt.loaded; //已经上传大小情况 
    var tot = evt.total; //附件总大小 
    var per = Math.floor(100 * loaded / tot); //已经上传的百分比  
    $('.progress').attr("style", "display:block;");
    $(".progress-bar").html(per + "%");
    $(".progress-bar").css("width", per + "%");
}

function checkFileExt(filename) {
    var flag = false; //状态
    var arr = ["flv", "mp4", "png"];
    //取出上传文件的扩展名
    var index = filename.lastIndexOf(".");
    var ext = filename.substr(index + 1);
    //循环比较
    for (var i = 0; i < arr.length; i++) {
        if (ext == arr[i]) {
            flag = true; //一旦找到合适的，立即退出循环
            break;
        }
    }
    //条件判断
    if (flag) {
        $('#codeError').attr("style", "display:none;");
    } else {
        $('#codeError').attr("style", "display:block;");
        setTimeout(function () {
            $('#codeError').attr("style", "display:none;");
            $(".fileinput-remove-button").click();
        }, 1500);
    }
}


window.onload = function () {
    // init();
    $(function () {
        $('[data-toggle="tooltip"]').tooltip();
        $("#fileinput").on("filebatchselected", function (event, files) {
            var fileName = files[0].name;
            var fileSize = files[0].size;
            console.log(fileName, fileSize);
            if ($("#fileinput").val() != "") {
                console.log($("#fileinput").val());
                checkFileExt(fileName);
            }
        });
        $('#uploadForm').submit(function () {    
            var data = new FormData($('#uploadForm')[0]);    
            $.ajax({
                url: '/file-upload',
                type: 'POST',
                data: data,
                // async: false,
                cache: false,
                timeout: 5000,
                contentType: false,
                processData: false,
                xhr: function () {　　　　　　
                    var xhr = $.ajaxSettings.xhr();　　　　　　
                    if (onprogress && xhr.upload) {　　　　　　　　
                        xhr.upload.addEventListener("progress", onprogress, false);　　　　　　　　
                        return xhr;　　　　　　
                    }　　　　
                },
                success: function (data) {
                    console.log(data);
                    $(".fileinput-remove-button").click();
                    uploadSocket(data);
                }
            });    
            return false;   
        });
    });
}