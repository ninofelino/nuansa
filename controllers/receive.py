"""
sudo apt-get install postgresql-contrib
"""
class Receive:
    harian="""
    select concat('<a href="/felino/receive/',podate,'">',podate,'</a>') from
    ( 
    select podate from felino_receive group by 1 order by 1 desc
    ) t
    """   
    harian_receive="""
    select (select name from res_partner where id=left(t.barcode,3)::int) as vendor,b.name,podate,sum(qty)
          from felino_receivedetail t
          left outer join product_template b on 
          (select product_tmpl_id from product_product where default_code=t.barcode)=b.id  
          group by 1,2,3 
    """     
    harian_receive_bysup="""
    select (
          select name from res_partner where id=left(t.barcode,3)::int) as vendor,b.name
          ,(select name from product_category where id=b.categ_id)
          ,podate,sum(qty) as  qty,count(*) as baris
          from felino_receivedetail t
          left outer join product_template b on 
          (select product_tmpl_id from product_product where default_code=t.barcode)=b.id  
          where podate='%s'
          group by 1,2,3,4 
    """
    harian_rekapan="""
    select (select name from res_partner where id=t.supplier) as supplier,t.podate,article,array_agg(barcode),sum(qty),sum(price)
    from
    (
    select a.supplier,a.name,c.name as article,a.podate,b.barcode,b.qty,b.price from felino_receive a
    left outer join  felino_receivedetail b  on a.ponum=b.ponum
    left outer join  product_template c on (select min(product_tmpl_id) from product_product where default_code=b.barcode)=c.id 
    where a.podate = DATE 'yesterday'
    )  t group by 1,2,3
    """
    harian_supplier="""
    select concat('<b><a href="/felino/receiving/vendor/',supplier,'">',(select name from res_partner where id=t.supplier::int)
    ,'</b></a><br><small>',ponum,'</small>')
    ,podate
    ,data from
    (
    select a.ponum,a.podate,a.supplier,json_agg(json_build_object(
    'barcode',b.barcode,'qty',b.qty)) as data from 
    felino_receive a
    left outer join felino_receivedetail b on a.ponum=b.ponum
    where a.podate='%s'
    group by 1,2,3
    ) t
    """
    catagory_mclass="""
    select a.id,a.name,json_build_object('id',a.id,'text',a.name,'children',
    json_agg(json_build_object('id',b.id,'text',concat(b.name,b.id::text),'children',felino_mcla(b.id)
    /*,'children',(select json_agg(json_build_object('id',b.id+1000,'text',b.id)) from product_category c limit 1)
    */
    ) order by b.name ) 
    ) as tree
    from product_category a
    left outer join product_category b on a.id=b.parent_id
    
   
    where a.id=3
    group by 1,2 LIMIT 2;
   
    """

    new_catagory_mclass="""
    select a.id,a.name,json_build_object('id',a.id,'name',a.name,'children',
    json_agg(json_build_object('id',b.id,'name',concat(b.name,b.id::text),'children',felino_mcla(b.id)
    /*,'children',(select json_agg(json_build_object('id',b.id+1000,'name',b.id)) from product_category c limit 1)
    */
    ) order by b.name ) 
    ) as tree
    from product_category a
    left outer join product_category b on a.id=b.parent_id
    
   
    where a.id=3
    group by 1,2 LIMIT 2;
   
    """


    tree_mclass="""
    <div id="using_json"></div>
    <script>
    $('#using_json').jstree({ 'core' : {
    'data' :%s

    
    } });
    </script>
    """
    new_tree_mclass="""
    <div id="tree1"></div>
    <script>
      $(function() {
      var $tree = $('#tree1');

       $tree.tree({
        data: %s,
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
            var node_id = $(e.target).data('node-id');
            var node = $tree.tree('getNodeById', node_id);
            if (node.link) {
                 $("#dikanan").html("<center>Loading....</center>");
                 $('.box').jmspinner('small');
                 $('#dikanan').pleaseWait();

                //alert(node.link);
                $.get(node.link, function(data, status){
                  
                  $('#pesan').html(status)
                  $('#dikanan').pleaseWait('stop');
                  //alert("Data: " + data + "Status: " + status);
                  $("#dikanan").html(data)
                });
            }
        }
    );
        
        }) 
  
    </script>
    """
