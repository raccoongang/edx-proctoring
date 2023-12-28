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

      return submissions.map(function(item) {
        var submit_url = item.slice(user_prefix.length);
        var payload = sessionStorage.getItem(item);

        return new Promise(function(resolve) {
          $.ajax({
            url: submit_url,
            type: 'POST',
            data: payload,
            dataType: 'json',
            success: function(data) {
              resolve(data);
            },
          });
        });
      });
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
              var submitted_problems = submitUnsavedProblems(user_id);
              Promise.all(submitted_problems)
                .finally(function() {
                  sessionStorage.clear();
                  location.reload();
                });
            } else {
              location.reload();
            }
          },
        });
      }
    );
  });
}).call(this, window.jQuery);
