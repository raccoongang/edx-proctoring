(function($) {
  'use strict';

  $(document).ready(function () {
    function submitUnsavedProblems(user_id) {
      var user_prefix = user_id + ':';
      var handler_suffixes = ['problem_check', 'submit_problem', 'student_submit'];
      var submissions = Object.keys(sessionStorage).filter(function(item) {
        return item.startsWith(user_prefix) && handler_suffixes.some(function(handler) {
          return item.endsWith(handler);
        });
      });
      for (var i = 0; i < submissions.length; i += 1) {
        var submit_url = submissions[i].slice(user_prefix.length),
            payload = sessionStorage.getItem(submissions[i]);
        $.ajax({
          url: submit_url,
          type: 'POST',
          data: payload,
          dataType: 'json',
          success: function(data) {
            sessionStorage.clear();
          },
        });
      }
    }

    $('.exam-action-button').click(
      function(_) {
        $(window).unbind('beforeunload');

        var action_url = $(this).data('change-state-url');
        var action = $(this).data('action');
        var user_id = $(this).data('user-id');

        $.ajax({
          url: action_url,
          type: 'PUT',
          data: {action: action},
          success: function() {
            if (action === 'submit') {
              submitUnsavedProblems(user_id);
            }
            location.reload();
          },
        });
      }
    );
  });
}).call(this, window.jQuery);
