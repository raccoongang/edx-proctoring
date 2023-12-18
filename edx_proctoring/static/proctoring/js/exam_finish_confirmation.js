(function($) {
  'use strict';

  $(document).ready(function () {
    $('.exam-action-button').click(
      function(_) {
        $(window).unbind('beforeunload');

        var action_url = $(this).data('change-state-url');
        var action = $(this).data('action');

        $.ajax({
          url: action_url,
          type: 'PUT',
          data: {action: action},
          success: function() {
            location.reload();
          },
        });
      }
    );
  });
}).call(this, window.jQuery);
