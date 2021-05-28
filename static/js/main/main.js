$(document).ready(function () {
    // Category sidebar
    var tg_disabled = false;
    var sm_display = false;

    function sidebar_update_by_res() {
        if ($(window).width() > 768) {
            $('#content').css('display', 'block');
            $('#sidebar').addClass('active');
            $('#sidebar').css('display', 'block');
            sm_display = false;
        } else {
            if (sm_display) {
                $('#content').css('display', 'none');
            } else {
                $('#content').css('display', 'block');
            }
            $('#sidebar').removeClass('active');
            $('#sidebar').css('display', 'none');
        }
    }

    function show_sidebar() {
        $('#sidebar').css('display', 'block');
        setTimeout(function() {
            $('#sidebar').addClass('active');
            $('#content').css('display', 'none');
            tg_disabled = false;
        }, 10);
    }

    function hide_sidebar() {
        $('#sidebar').removeClass('active');
        setTimeout(function() {
            $('#sidebar').css('display', 'none');
            $('#content').css('display', 'block');
            tg_disabled = false;
        }, 300);
    }

    $('#sidebarCollapse').on('click', function () {
        if (!tg_disabled) {
            tg_disabled = true;
            if ($('#sidebar').css('display') == 'block') {
                hide_sidebar();
                sm_display = false;
            } else {
                show_sidebar();
                sm_display = true;
            }
        }
    });

    $('.category-name').on('click', function () {
        if($(window).width() <= 768) {
            hide_sidebar();
        }
    });

    $( window ).resize(function() {
        sidebar_update_by_res();
    });

    sidebar_update_by_res();
});