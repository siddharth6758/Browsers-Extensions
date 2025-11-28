jQuery(document).ready(function() {
  $('#backBtn').on('click', function (e) {
      e.preventDefault();

      const idToken = localStorage.getItem('idToken');
      if (idToken) {
      const url = '/?token=' + encodeURIComponent(idToken);
      globalThis.location.href = url;
      } else {
      globalThis.location.href = '/';
      }
  });

  $(async function () {
    console.log('preset_form.js loaded');

    const [tab] = await chrome.tabs.query({active: true, lastFocusedWindow: true});
    console.log(tab.url);

    $('#presetForm').on('submit', function (e) {
      e.preventDefault();

      const name = $('#presetName').val().trim();
      const url = tab.url;

      if (!name || !url) {
        $('#presetMsg').text('Preset name and URL are required.');
        return;
      }

      $.ajax({
        url: '/save_preset',
        type: 'POST',
        contentType: 'application/json',
        headers: {
          'Authorization': 'Bearer ' + localStorage.getItem('idToken')
        },
        data: JSON.stringify({
          preset_id: name,
          preset_data: url
        }),
        success: function () {
          $('#presetMsg').text('Preset saved successfully!');
        },
        error: function (xhr) {
          const msg = xhr.responseJSON?.detail || 'Failed to save preset.';
          $('#presetMsg').text(msg);
        }
      });
    });
  });
});