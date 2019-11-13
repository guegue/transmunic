$(function () {
    let body = $('body');

    body
        .on('click', '.ver-mas', function () {
            let text = $(this).children('strong').text();
            text = (text.search('MAS') > -1) ? 'VER MENOS' : 'VER MAS';
            $(this).children('strong').text(text);
        });
});