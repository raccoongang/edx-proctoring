/* globals ProctoredExamModel:false */
$(function() {
    'use strict';

    var proctoredExamView = new edx.courseware.proctored_exam.ProctoredExamView({
        el: $('.proctored_exam_status'),
        proctored_template: '#proctored-exam-status-tpl',
        model: new ProctoredExamModel()
    });
    proctoredExamView.render();

    // initialize jQuery.microphoneChecker plugin
    try {
        $('#check-microphone-btn').on('click', function () {
            $(this).microphoneChecker({
                counterView : true,
                dispatchStop : true
            });
        } catch (e) {
            console.error("jQuery.microphoneChecker plugin not connected or not found");
        }
        $(this).prop("disabled", true)
        $(".check-microphone-alert").fadeIn("slow");
    });
            $(this).prop("disabled", true)
            $(".check-microphone-alert").fadeIn("slow");
        });
    } catch (e) {
        console.error("jQuery.microphoneChecker plugin not connected or not found");
    }

    $('.check-camera-video-start').on('click', function () {
        $(this).attr('disabled', true);
        const $blockVideo = $('#check-camera-video-block', this.element)[0];
        try {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia({video: true}).then(function (stream) {
                    $blockVideo.srcObject = stream;
                });
            }
        } catch (e) {
            console.error('The Video checker failed, the following error occurred:', e);
        }
    });
});
