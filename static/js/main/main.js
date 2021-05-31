$(document).ready(function () {
    // Category sidebar
    const vanish_width = 990;
    var tg_disabled = false;
    var sm_display = false;

    function sidebar_update_by_res() {
        if ($(window).width() > vanish_width) {
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
            $('#main-wrapper').addClass('justify-content-center');
            tg_disabled = false;
        }, 10);
    }

    function hide_sidebar() {
        $('#sidebar').removeClass('active');
        setTimeout(function() {
            $('#sidebar').css('display', 'none');
            $('#content').css('display', 'block');
            $('#main-wrapper').removeClass('justify-content-center');
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
        if($(window).width() <= vanish_width) {
            hide_sidebar();
        }
    });

    $( window ).resize(function() {
        sidebar_update_by_res();
    });

    sidebar_update_by_res();

    // category side bar on click event
    // set category param to category id

    function insertParam(key, value) {
        key = encodeURIComponent(key);
        value = encodeURIComponent(value);
    
        // kvp looks like ['key1=value1', 'key2=value2', ...]
        var kvp = document.location.search.substr(1).split('&');
        let i=0;
    
        for(; i<kvp.length; i++){
            if (kvp[i].startsWith(key + '=')) {
                let pair = kvp[i].split('=');
                pair[1] = value;
                kvp[i] = pair.join('=');
                break;
            }
        }
    
        if(i >= kvp.length){
            kvp[kvp.length] = [key,value].join('=');
        }
    
        // can return this or...
        let params = kvp.join('&');
    
        // reload page with new params
        document.location.search = params;
    }

    var getUrlParameter = function getUrlParameter(sParam) {
        var sPageURL = window.location.search.substring(1),
            sURLVariables = sPageURL.split('&'),
            sParameterName,
            i;
    
        for (i = 0; i < sURLVariables.length; i++) {
            sParameterName = sURLVariables[i].split('=');
    
            if (sParameterName[0] === sParam) {
                return typeof sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
            }
        }
        return false;
    };

    // get all category links

    var elements = document.getElementsByClassName('category-name');

    var category_click = function() {
        const pk = this.getAttribute('name');
        insertParam('category', pk); // set category param
    };

    for (let i = 0; i < elements.length; i++) {
        elements[i].addEventListener('click', category_click, false);
    }

    $('#filter-submit').click(function(){
        let filter_type = $('#sorting').val()
        insertParam('sorting', filter_type);
    });

    // on page load set filter option based on get parameter
    let sorting_param = getUrlParameter('sorting')
    if (sorting_param != false) {
        $('#sorting').val(sorting_param).change();
    } else {
        $('#sorting').val('').change();
    }

    // mark current selected category 
    const arrow_html = '<i class="fas fa-arrow-right mr-2"></i>';
    var current_category = getUrlParameter('category');

    $('#category-list li').each(function(index) {
        let category_link = $(this).children();
        let category_id = category_link.attr('name');
        let inner_html;
        if (category_id == current_category) {
            inner_html = arrow_html + category_link.html();
            category_link.html(inner_html);
        }
    });
});

