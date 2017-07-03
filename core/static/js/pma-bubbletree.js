$(function () {
    var $tooltip = $('<div class="tooltip" data-toggle="tooltip">Tooltip</div>');
    $('.bubbletree').append($tooltip);
    $tooltip.tooltip();
    $tooltip.hide();

    var tooltip = function (event) {
        console.log("bubble tooltip");
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

    if (typeof data !== 'undefined') {
        var defaultbubble = new BubbleTree({
            data: data,
            container: '.bubbletree',
            bubbleType: 'icon',
            bubbleStyles: {
                'cofog': BubbleTree.Styles.Cofog,
                'income': BubbleTree.Styles.Income
            },
            formatValue: function (value) {
                return value.toFixed(1);
            },
            tooltipCallback: tooltip
        });
    }

    if (typeof data1 !== 'undefined') {
        var bubble2 = new BubbleTree({
            data: data1,
            container: '#bubbletree1',
            bubbleType: 'icon',
            bubbleStyles: {
                'cofog': BubbleTree.Styles.Cofog,
                'income': BubbleTree.Styles.Income
            },
            formatValue: function (value) {
                return value.toFixed(1);
            }
        });
    }

    if (typeof data2 !== 'undefined') {
        var bubble1 = new BubbleTree({
            data: data2,
            container: '#bubbletree2',
            bubbleType: 'icon',
            bubbleStyles: {
                'cofog': BubbleTree.Styles.Cofog,
                'expense': BubbleTree.Styles.Expense
            },
            formatValue: function (value) {
                return value.toFixed(1);
            }
        });
    }
});
