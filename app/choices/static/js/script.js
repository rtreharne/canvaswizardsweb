function buildQueryString(){
    var queryString = "";
    var selectedModules = $('.selected');
    selectedModules.each(function() {
        queryString += $(this).attr('id') + ",";
    });
    // strip trailing comma
    queryString = queryString.slice(0, -1);

    // get this url
    var url = window.location.href;

    // if there is already a query string, remove it
    if (url.indexOf('?') > -1) {
        url = url.split('?')[0];
    }

    // add query string to url
    url += '?modules=' + queryString;
    // update href of id="share-link" element
    $('#share-link').attr('href', url);
}





function updateYearPoints(clickedModule) {
    var totalPoints = 0;

    // Get closest .year to clickedModule
    // Find all .selected modules within that .year
    // Add up all the credits of those modules
    // Update the .year-total with the total credits
    var year = $(clickedModule).closest('.year');
    var selectedModules = year.find('.selected');
    selectedModules.each(function() {
        totalPoints += parseFloat($(this).attr('credits'));
    });
    year.find('.year-total').text(totalPoints);
    limitModules(year);

}

function limitModules(year) {
    var year = $(year);
    var totalPoints = 0;
    var selectedModules = year.find('.selected');
    selectedModules.each(function() {
        totalPoints += parseFloat($(this).attr('credits'));
    });

    var notSelectedModules = year.find('.module').not('.selected');
    notSelectedModules.each(function() {
        if (totalPoints + parseFloat($(this).attr('credits')) > 120) {
            $(this).addClass('disabled');
        } else {
            $(this).removeClass('disabled');
        }
    });   
}

function setYearPoints(year) {
    var year = $(year);
    var totalPoints = 0;
    var selectedModules = year.find('.selected');
    selectedModules.each(function() {
        totalPoints += parseFloat($(this).attr('credits'));
    });
    year.find('.year-total').text(totalPoints);
    limitModules(year);
}

function checkPrerequisites() {
    var selectedModules = $('.selected');
    var unselectedModules = $('.module').not('.selected');

    // create an array of selected module ids
    var selectedModuleIds = [];
    selectedModules.each(function() {
        selectedModuleIds.push($(this).attr('id'));
    });

    // for each unselected module, check if any selectedModuleIds are in its prerequisites
    unselectedModules.each(function() {
        
        var prerequisites = $(this).attr('alt-title');
        //console.log(prerequisites);
        
        if (prerequisites !== 'Required: ') {
            prerequisites = prerequisites.split(": ")[1].split(', ');
            

                        
            // id of this
            var id = $(this).attr('id');
        
            if (prerequisites.every(val => selectedModuleIds.includes(val))) {
                $(this).removeClass('pnotsat');
            } else {
                $(this).addClass('pnotsat');
            }
        }
    });
}

// on tap and hold show tooltip for mobile using touchstart and touchend



document.addEventListener('click', function(event) {
    if (event.target.classList.contains('module')) {
        if ((event.target.classList.contains('selected') && !event.target.classList.contains('compulsory')) || (event.target.classList.contains('disabled'))) {
            event.target.classList.remove('selected');
            
            updateYearPoints(event.target);
            checkPrerequisites();
            buildQueryString();
            
        } else {
            event.target.classList.add('selected');
            
            updateYearPoints(event.target);
            checkPrerequisites();
            buildQueryString();
            
        }
    }
});

// On click id="share-link" element, copy href to clipboard
$('#share-link').on('click', function(event) {
    // prevent default action
    event.preventDefault();
    var copyText = $('#share-link').attr('href');
    navigator.clipboard.writeText(copyText)
        .then(function() {
            alert('Link copied to clipboard');
        })
        .catch(function(error) {
            console.error('Failed to copy link to clipboard:', error);
        });
});

// On click id="transcript", if class="off", hide all .module elements that are not .selected
// If class="on", show all .module elements

$('#transcript').on('click', function(event) {
    event.preventDefault();
    if ($(this).hasClass('off')) {
        $(this).removeClass('off');
        $(this).addClass('on');
        $('.module').not('.selected').hide();
        $(this).text('[Transcript: on]');
    } else {
        $(this).removeClass('on');
        $(this).addClass('off');
        $('.module').show();
        $(this).text('[Transcript: off]');
    }
});


$(document).ready(function() {

        
    $('.year').each(function() {
        
        setYearPoints(this);
        buildQueryString();
        // select all modules in query string
        var queryString = window.location.search;
        var urlParams = new URLSearchParams(queryString);
        var modules = urlParams.get('modules');
        if (modules !== null) {
            var selectedModules = modules.split(',');
            selectedModules.forEach(function(module) {
                $('#' + module).addClass('selected');
                updateYearPoints($('#' + module));
            });
        }
        
    });

    checkPrerequisites();
});










