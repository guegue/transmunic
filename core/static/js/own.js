$(function () {

    var lista_municipios = $('.listado-municipios');
    var lista_indicadores = $('.listado-indicadores');
    var lista_transferencias = $('#listado-transferencias');
    var municipio = $('.municipio');
    var municipio2 = $('#municipio2');
    let body = $('body');
    let select_indicador = $('#indicador');
    let select_year = $('#year');

    lista_municipios.select2({
        placeholder: 'Municipio',
        allowClear: true
    });
    municipio.select2({
        placeholder: 'Municipios',
        allowClear: true
    });
    lista_indicadores.select2({
        placeholder: 'Resumen Municipal',
        allowClear: true
    });

    lista_transferencias.select2({
        placeholder: 'Transferencias',
        allowClear: true
    });


    if (select_indicador.length > 0 && select_indicador.attr('type') === undefined) {
        select_indicador.select2();
    }
    if (select_year.length > 0) {
        select_year.select2();
    }
    if (municipio2.length > 0) {
        municipio2.select2({
            placeholder: '(Municipio)'
        });
    }


    body
        .on('click', '.ver-mas', function () {
            let text = $(this).children('strong').text();
            text = (text.search('MÁS') > -1) ? 'VER MENOS' : 'VER MÁS';
            $(this).children('strong').text(text);
        })
        .on('mouseover', '.select2', function () {
            $(this).find('.select2-selection__rendered').prop('title', '');
        });


    lista_municipios.on('select2:selecting', function (e) {
        window.location = e.params.args.data.id;
    });


    lista_municipios
        .on('select2:open', function () {
            $('.select2-dropdown').addClass('select2-dropdown-middle_width');
            $('.select2-search--dropdown .select2-search__field').attr('placeholder', 'Escribir el municipio');
        })
        .on('select2:close', function () {
            $('.select2-search--dropdown .select2-search__field').attr('placeholder', null);
        });

    municipio
        .on('select2:open', function () {
            $('.select2-search--dropdown .select2-search__field').attr('placeholder', 'Escribir el municipio');
        })
        .on('select2:close', function () {
            $('.select2-search--dropdown .select2-search__field').attr('placeholder', null);
        });

    lista_indicadores
        .on('select2:selecting', function (e) {
            window.location = e.params.args.data.id;
        })
        .on('select2:open', function () {
            $('.select2-dropdown').addClass('select2-dropdown-width');
            $('.select2-search--dropdown .select2-search__field').attr('placeholder', 'Escribir el Indicador');
        })
        .on('select2:close', function () {
            $('.select2-search--dropdown .select2-search__field').attr('placeholder', null);
        });

    lista_transferencias
        .on('select2:selecting', function (e) {
            window.location = e.params.args.data.id;
        });

    $('.pma-navbar').show();
});