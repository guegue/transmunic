$(function () {
    let body = $('body');

    body
        .on('click', '.ver-mas', function () {
            let text = $(this).children('strong').text();
            text = (text.search('MÁS') > -1) ? 'VER MENOS' : 'VER MÁS';
            $(this).children('strong').text(text);
        });
});