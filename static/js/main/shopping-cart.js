function cartUpdate() {
    var navbarHeight = parseInt($('#navbar').css('height'));
    var scroll = $(window).scrollTop();
    if (scroll < navbarHeight) {
		var top_val = navbarHeight - scroll + 5;
        $('#floating-cart').css('top', top_val.toString() + 'px');
    } else
    $('#floating-cart').css('top', '3px');
}

cartUpdate();
$(window).scroll(function (event) {
    cartUpdate();
});

$('#nb-toggle').click(function() {
    var elapsed = 0;
    var step = 5;
    var iv = setInterval(function() {
        cartUpdate();
        elapsed += step;
        if (elapsed > 1000)
            clearInterval(iv);
    }, step);
});