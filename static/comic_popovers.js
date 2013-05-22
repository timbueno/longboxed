var attachpopover = function(){
    $(".pop").each(function() {
        var $pElem= $(this);
        $pElem.popover(
            { 
              placement: 'right',
              trigger: 'manual',  
              html: true, 
              delay: { show: 350, hide: 100 },
              template: '<div class="popover comicpopover"><div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>', 
              title: getPopTitle($pElem.attr("id")),
              content: getPopContent($pElem.attr("id"))
            }
        );
        var timer,
            popover_parent;
        function hidePopover(elem) {
            $(elem).popover('hide');
        }
        $pElem.hover(
            function() {
              var self = this;
              clearTimeout(timer);
              $('.popover').hide(); //Hide any open popovers on other elements.
              popover_parent = self
              $(self).popover('show');            
            }, 
            function() {
              var self = this;
              timer = setTimeout(function(){hidePopover(self)},300);                 
        });
        $(document).on({
          mouseenter: function() {
            clearTimeout(timer);
          },
          mouseleave: function() {
            var self = this;
            timer = setTimeout(function(){hidePopover(popover_parent)},300); 
          },
          click: function() {
            var self = this;
            timer = setTimeout(function(){hidePopover(popover_parent)},300); 
          },
          tap: function() {
            var self = this;
            timer = setTimeout(function(){hidePopover(popover_parent)},300); 
          }
        }, '.popover');
    });

    function getPopTitle(target) {
        return $("#" + target + "_content > div.popTitle").html();
    };
            
    function getPopContent(target) {
        return $("#" + target + "_content > div.popContent").html();
    };
}