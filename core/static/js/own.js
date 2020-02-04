$(function () {
    let body = $('body');
    let select_indicador = $('#indicador');
    let select_year = $('#year');

    if (select_indicador.length > 0) {
        select_indicador.select2();
    }
    if (select_year.length > 0) {
        select_year.select2();
    }

    body
        .on('click', '.ver-mas', function () {
            let text = $(this).children('strong').text();
            text = (text.search('MÁS') > -1) ? 'VER MENOS' : 'VER MÁS';
            $(this).children('strong').text(text);
        })
        .on('mouseover', '.select2', function () {
            $(this).find('.select2-selection__rendered').prop('title', '');
        })

});