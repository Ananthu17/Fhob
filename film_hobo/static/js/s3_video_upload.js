//Bucket Configurations
AWS.config.update({
	accessKeyId : 'AKIASATMOOGBI6XUJ6CO',
	secretAccessKey : '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',
    maxRetries: 10
});
AWS.config.region = 'us-east-2';

$( document ).ready(function() {
    var bucketName = 'filmhobo-videos';


	// $("#uploadForm").submit(function() {
    $('body').on('click' , '#upload_video', function(){
        var user_id = $("#user_id").val();
        var project_name = $("#project_name").val();
        var project_id = $("#project_id").val();
        var path = user_id+"/"+project_name+"/"+project_id+".mp4"
        // console.log(user_id)
        // console.log(project_name)
        // console.log(project_id)

		var bucket = new AWS.S3({params: {Bucket: 'filmhobo-videos'}});
		var uploadFiles = $('#upFile')[0];
		var upFile = uploadFiles.files[0];
		if (upFile) {
            // update video type in table
            data_dict = {};
            data_dict['project_id'] = project_id;
            $.get('/project/save-video-upload-type/', data_dict)
            .done(function(data) {
            });
            const options = {
                partSize: 5 * 1024 * 1024,
                // how many concurrent uploads
                queueSize: 5
            };
            document.getElementById("progress-bar").style.display = "block";
			var uploadParams = {Key: path, ContentType: upFile.type, Body: upFile};


            try {
                 bucket.upload(uploadParams, options)
                .on('httpUploadProgress', function(progress) {
                    var uploaded = parseInt((progress.loaded * 100) / progress.total);
                    $("progress").attr('value', uploaded);
                    console.log(uploaded+"%");
                    if(uploaded==100){
                        document.getElementById("progress-bar").style.display = "none";
                        $('#upFile').val(null);
                        $('#success_message').fadeIn().html("Video Uploaded Successfully.");
                        setTimeout(function() {$('#success_message').fadeOut("slow");}, 2000 );
                    }
                }).send(function(err, data) {
                    console.log(err);
                    $("#showMessage").html(err);
                });
            }catch(error) {
                console.log('upload ERROR', filePath, error);
            }
		}else{
            $("#err-msg").html("This field is required.")
        }
		return false;
	});

});