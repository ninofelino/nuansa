$(function() {
    function isNumber(n) {
        return !isNaN(parseFloat(n)) && isFinite(n);
      }
      
      function setFontSize(el) {
          var fontSize = el.val();
          
          if ( isNumber(fontSize) && fontSize >= 0.5 ) {
            $('body').css({ fontSize: fontSize + 'em' });
          } else if ( fontSize ) {
            el.val('1');
            $('body').css({ fontSize: '1em' });  
          }
      }
      
      $(function() {
        
        $('#fontSize')
          .bind('change', function(){ setFontSize($(this)); })
          .bind('keyup', function(e){
            if (e.keyCode == 27) {
              $(this).val('1');
              $('body').css({ fontSize: '1em' });  
            } else {
              setFontSize($(this));
            }
          });
        
        $(window)
          .bind('keyup', function(e){
            if (e.keyCode == 27) {
              $('#fontSize').val('1');
              $('body').css({ fontSize: '1em' });  
            }
          });
        
      });
    var $tree = $('#tree1');

     $tree.tree({
      //data: %s,
      autoOpen: 1,
      onCreateLi: function(node, $li) {
          // Append a link to the jqtree-element div.
          // The link has an url '#node-[id]' and a data property 'node-id'.
          $li.find('.jqtree-element').append(
              '<a href="#node-'+ node.id +'" class="edit" data-node-id="'+
              node.id +'">__</a>');
          }
      });


      $tree.on(
      'click', '.edit',
      function(e) {
          // Get the id from the 'node-id' data property
          var node_id = $(e.target).data('node-id');

          // Get the node from the tree
          var node = $tree.tree('getNodeById', node_id);

          if (node) {
              // Display the node name
              alert(node.name);
          }
      }
  );
      
      }) 
