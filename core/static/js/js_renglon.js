$(function () {
    let message_box = $('#message');
    let col_ejecutado = $('.col-ejecutado');

    $('.input-asignado').on('change', function () {
        let body_table = $(this).parents('tbody');
        let rows = body_table.find('tr');
        let data = $(this).data('nombre_total');

        let total_asignado = Sum(rows, '.input-asignado');

        $(`#${data}`).html(total_asignado);
    });
    $('.input-ejecutado').on('change', function () {
        let body_table = $(this).parents('tbody');
        let rows = body_table.find('tr');
        let data = $(this).data('nombre_total');

        let total_ejecutado = Sum(rows, '.input-ejecutado');

        $(`#${data}`).html(total_ejecutado);
    });
    $('.panel-heading').on('click', function () {
        let icon = $(this).find('i');
        if (icon.hasClass('fa-angle-up')) {
            icon.removeClass('fa-angle-up');
            icon.addClass('fa-angle-down');
        } else {
            icon.removeClass('fa-angle-down');
            icon.addClass('fa-angle-up');
        }
    });
    $('#id_periodo').on('change', function () {
        if ($(this).val().toUpperCase() === 'I') {
            col_ejecutado.fadeOut('fast');
        } else {
            col_ejecutado.fadeIn('fast');
        }
        $('.input-ejecutado').val(0).trigger('change');
    });

    //mandar a ocultar mensaje despues de 5segundos
    if (message_box.length > 0) {
        setTimeout(function () {
            message_box.fadeOut('slow');
        }, 5000);
    }

    /**
     * @return {number}
     */
    function Sum(array_elements, class_element) {
        let total = 0;
        array_elements.each(function () {
            let value = $(this).find(class_element).val();
            total += parseFloat(value);
        });
        return total;
    }
});