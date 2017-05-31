$(function() {
    var $tooltip = $('<div class="tooltip">Tooltip</div>');
    $('.bubbletree').append($tooltip);
    $tooltip.hide();

    var tooltip = function(event) {
        if (event.type == 'SHOW') {
            // show tooltip
            vis4.log(event);
            $tooltip.css({
                left: event.mousePos.x + 4,
                top: event.mousePos.y + 4
            });
            $tooltip.html(event.node.label + ' <b>' + event.node.famount + '</b>');
            var bubble = event.target;

            $tooltip.show();
        } else {
            // hide tooltip
            $tooltip.hide();
        }
    };

    $.each(data['children'], function(key, value) {
        data['children'][key]['color'] = vis4color.fromHSL(key / data.children.length * 360, .7, .5).x;
        var node_color = vis4color.fromHSL(key / data.children.length * 360, .7, .5).x;
        if(typeof data['children'][key]['children'] != 'undefined' ){
            $.each(data['children'][key]['children'], function(j, val) {
                data['children'][key]['children'][j]['color'] = vis4color.fromHex(node_color).lightness('*' + (.5 + Math.random() * .5)).x;
            });
        }
    });

    new BubbleTree({
        data: data,
        container: '.bubbletree',
        bubbleType: 'icon',
        bubbleStyles: {
            'cofog': BubbleTree.Styles.Cofog
        },
        formatValue: function(value) {
            return 'C$ ' + value + 'M';
        }
    });
});
