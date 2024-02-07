
$(document).ready(function() {
    $('#changelist :checkbox').change(function() {
        console.log('change');
        // Save the current scroll position in the URL hash
        window.location.hash = 'scrollPos=' + $(window).scrollTop();
        // Click the input with name "_save" to submit the form
        $('input[name="_save"]').click();
    });

    // If a scroll position is saved in the URL hash, scroll to that position
    if (window.location.hash.startsWith('#scrollPos=')) {
        $(window).scrollTop(window.location.hash.split('=')[1]);
    }
});