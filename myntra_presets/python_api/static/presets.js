jQuery(document).ready(function() {
    console.log("Presets JS loaded");
    $('#loginForm').on('submit', function(e) {
        e.preventDefault();

        const email = $('#loginEmail').val();
        const password = $('#loginPassword').val();

        $.ajax({
            url: '/signin',
            type: 'POST',
            data: JSON.stringify({
                email: email,
                password: password
            }),
            contentType: "application/json",
            success: function(response) {
                localStorage.setItem('refreshToken', response.refreshToken);
                localStorage.setItem('localId', response.localId);
                localStorage.setItem('email', response.email);
                localStorage.setItem('idToken', response.idToken);
                globalThis.location.href = '/?token=' + encodeURIComponent(response.idToken);
            },
            error: function(xhr, status, error) {
                // Display error message
                const errorMsg = xhr.responseJSON?.detail || 'Login failed. Please try again.';
                $('#loginError').text(errorMsg);
            }
        });
    });

    $('#signupForm').on('submit', function(e) {
        e.preventDefault();

        const email = $('#signupEmail').val();
        const password = $('#signupPassword').val();

        $.ajax({
            url: '/signup',
            type: 'POST',
            data: JSON.stringify({
                email: email,
                password: password
            }),
            contentType: "application/json",
            success: function(response) {
                localStorage.setItem('refreshToken', response.refreshToken);
                localStorage.setItem('localId', response.localId);
                localStorage.setItem('email', response.email);
                localStorage.setItem('idToken', response.idToken);
                globalThis.location.href = '/?token=' + encodeURIComponent(response.idToken);
            },
            error: function(xhr, status, error) {
                const errorMsg = xhr.responseJSON?.detail || 'Signup failed. Please try again.';
                $('#signupError').text(errorMsg);
            }
        });
    });

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
});
