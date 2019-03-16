# -*- coding: utf-8 -*-
#import thread6
#pip install dataset
# pip3 install dataset 
#sudo su
import thread6
import time
import base64
import json
import subprocess
import time
import json
from dbfread import DBF
from odoo import http,exceptions
import re
import os
import glob
import csv
import base64
import cgi
import logging
import pandas as pd 
import pandas.io.sql as psql
import psycopg2 as pg
import xml.etree.ElementTree as ET
import locale
from datetime import datetime
from dateutil.parser import parse
import sqlite3
from sqlite3 import Error
import dataset
from . import receive
from . import stock
import re
import glob
import pathlib

import numpy as np
import plotly
import plotly.graph_objs as go



#import datetime
# DELETE FROM ir_attachment WHERE url LIKE '/web/content/%';
# UPDATE ir_module_module SET state = 'to remove' WHERE name = 'my_module_to_uninstall' ,
# sudo apt-get install python3-pandas
# 
datalama='/mnt/poserver/ics/DAT/INV.DBF'

def importSupplier():
    conn = psycopg2.connect("postgresql://felino:felino@localhost/databaru")
    cur = conn.cursor()
    cari = conn.cursor()
    for item in DBF('/mnt/poserver/ics/DAT/SUP.DBF',encoding='iso-8859-1'):
        print(item['DESC'],item['CODE'])
        SQ="UPDATE res_partner SET name='%s',display_name='%s',phone='%s' WHERE ID=%s"
         
        cur.execute(SQ %(item['DESC'].replace("'",""),item['DESC'].replace("'",""),item['TELP'],item['CODE'])) 
        conn.commit()
              
    return 0

def searchbutton():
    htm="""
    <script>
    function showResult(str) {
            $("#result").html(str);
            $.ajax({type:"get",url:"/felino/data/"+str,
            success:function(html){$("#result").html(html).show()}
            })
            }; 
    </script> 
    <input class="form-control" type="text" placeholder="Search" 
    aria-label="Search" onkeyup="showResult(this.value)"/>
       
    <div id="result" style="padding:4px"></div>
        

    """
    return htm

def importRcv():
    X=0
    sumber='/mnt/poserver/ics/DAT/'
    db = dataset.connect('sqlite:///:memory:')
    #db = dataset.connect('sqlite:///datalama.db')
    terima = db['receiving']
    http.request.cr.execute('delete from felino_receive;delete from felino_receivedetail')
    http.request.cr.commit() 
    for record in DBF(sumber+'RCV2.DBF',encoding='iso-8859-1'):
        terima.insert(record)
    for item in DBF(sumber+'RCV1.DBF',encoding='iso-8859-1'):
        rcv=http.request.env['felino.receive'].browse([int(item['PONUM'])])
        detail_ids=[]
        cari=terima.find(PONUM=item['PONUM'])
        for rec in cari:
            data={'ponum':rec['PONUM'],'qty':rec['QTY'],'barcode':rec['INVCODE'],'podate':rec['PODATE'],'price':rec['PRICE']}
            detail_ids.append(data)
            http.request.env['felino.receivedetail'].create(data)
        if not rcv.exists():
           print("app-------------------------------") 
           rcv.create({'id':int(item['PONUM']),'name':item['PONUM'],'ponum':item['PONUM'],'podate':item['PODATE'],'receive':item['TOTALRCV'],'total':item['TOTAL'],'supplier':item['SUPLIER']
           #,'detail_ids':(0,0,[{'qty':10}])
           #,'detail_ids':(0,0,[detail_ids])
           })
           print(*detail_ids)
           #rcv.update(detail_ids)
    return 0 

def sql2table(record):
    hasil=''
    hasil='<table id="kiri" class="table">'
    hasil=hasil+'<thead><tr><th>1</th><th>1</th></tr>'
    hasil=hasil+'</thead>'
    hasil=hasil+'<tbody>'
    for rec in record:
        hasil=hasil+'<tr>'
        for fld in rec:
            #print(type(fld),fld)
            #if type(fld)=='str':
            hasil=hasil+'<td>'+str(fld)+'</td>'          
        hasil=hasil+'</tr>'
    hasil=hasil+'</tbody>'    
    return hasil+'</table>'
def sql2datatable(record,headers):
    hasil=''
    hasil='<table id="kiri" class="table">'
    hasil=hasil+'<thead><tr>'
    for headi in headers:
        hasil=hasil+'<th>'+headi+'</th>'
    hasil=hasil+'</thead>'
    hasil=hasil+'<tbody>'
    for rec in record:
        hasil=hasil+'<tr>'
        for fld in rec:
            #print(type(fld),fld)
            #if type(fld)=='str':
            hasil=hasil+'<td>'+str(fld)+'</td>'          
        hasil=hasil+'</tr>'
    hasil=hasil+'</tbody>'    
    return hasil+'</table>'
def sidebar(isi):
    hasilnya=''
    for ha in isi:
        hasilnya=hasilnya+'<li>'+ha[0]+'</li>'
    return hasilnya  
def feltree(data):
    isi=''
    isi=isi+'<ul>'
    #isi=isi+'<li>'+data+'</li>'
    for dt in data:
        isi=isi+'<li><a href="/felino/eod">'+dt[0]+'</a></li>'
    isi=isi+'</ul>'
    hasil='<div id="jstree">'+isi+'</div>'
    return hasil  
def sidebar3(isi):
    hasilnya='<div class="btn-group-vertical">'
    for ha in isi:
        hasilnya=hasilnya+'<li width="100px"><a href="'+ha[1]+'" class="dropdown-item" >'+ha[0]+'</a></li>'
    return hasilnya+'</div>'    



def ninofelinosql(semua):
    http.request.cr.execute(semua)
    return http.request.cr.fetchall()

def fel_product_template(detail):
    table =ET.Element('table')
    table.attrib['class']='table table-striped' 
    body  =ET.SubElement(table,'tbody')
    kol=['vendor','name','list_price','standard_price','product_variant_ids']
    for rec in detail:
        baris=ET.SubElement(body,'tr')
        kolom=ET.SubElement(body,'td') 
        link=ET.SubElement(kolom,'a') 
        link.attrib['href']='/felino/loadimage/'+str(rec['id'])   
        gambar=ET.SubElement(link,'img')
        try:
           gambar.attrib['src']="data:image/png;base64,%s" %(rec.image_small.decode("utf-8"))
        except:
           gambar.attrib['src']="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAAAAACPAi4CAAAACXZwQWcAAABAAAAAQADq8/hgAAAEWklEQVRYw9WX6XKjRhCAef8HiySQvGt5vfZuEselOUAcEpe4GdI9MAgQOjb5k3SVyzY1801PX9OtNf9StP80QJR5miRpXtb/AFCnvmMySgmhlJn2Mal+BSBSj1NCGeNSGAMOd0/iQYCI95TAXnm+FCr/I2ZYPwJILEJhPaGm7flBFIW+Z5sUvwEivguovG7pMR0cV2e+BbYArF3cBqQclKfEvryvSB2KaHa6BYhgDSP7ZN7gmUNQCf86wCdgcBaKq04/cTzAuwbA/czKb8VdZYMSI8IAEOJ+XjTiFkF4SDjOARIIHLiBK+4E/xHOIdEloMSAAwZx7hEOBKIquwA4lFPbR/3uEhzCqSUmgBiwrGgeIlQm5b0zO0CN3yKw34QgQC4JKZqrGAFC0MpWvuwJ3V6hWD3BI5wchoDaBAumzYQgmsrd7ewZx5bosHIAAAtQp4+nXUuA+2yXy9Xyi4OsIorjauBLZQWtd0Gqrt3EvCXQlb4BMZYfsPP7cr0gvS4FaNw6Qus0ovtez8DZcYyHt8Wmk9XWdF+Mjf570Ke4q46UgAgUCtX55mKl/wSbsD83hrEE0VGJ1RrEWHz2aaXuIAEe7b3SNG/601oSzL/W20/T2r2uDNACARvjWelZQTTaCiCg2vSR1bzrsFgSQMk8SbPi8FWX+0GFbX2OXMarDoAmOGfo+wpXt7cwj4Hv+1n+rSMYW3HOfS4TAgHZIDIVYG38wNzchyB+kj4ZUwB4npw6ABokmgA2qz9kfbIkoWDLzQSQ0tbw2gA20kA/nmyqCHG8nmqQd2prbSKQZAIwnk5B5PSE/EWfACCUZGFSgHQKeE6DsCcExfc5wKEDRLMaJHBwTwA/zFzhOLBBPGODoCfEyYUb0XVBB1AGHXvho/SVDsSjF15QrtMG1xlpsDbCrCewj7UxAWAJSjsAlJOuHI0AX9Mi8IMgsJnMC2MMOJA2f7RhXI8AG/2LVxZZVlQWmKElnAFiT5nMH62L67Mb3lTmbIzVK3Uc9r6GvJAEyMa6d0KXP1oXliqbRPPzN0NvBcrBAmSpr37wlrB8GeRS6zkJECZVNRKeuLfty1C+wc/zp7TD9jVQN7DUDq2vkUEzfAymIl9uZ5iL1B0U1Rw7surmc4SE/sUBE3KaDB8Wd1QS7hJQga4Kayow2aAsXiV0L458HE/jx9UbPi33CIf+ITwDSnxM/IcIcAGIrHzaH+BX8Ky4awdq41nBZYsjG4/kEQLjg9Q5A9A1jJ7u3CJEa1OzmuvSKgubwPA24IT7WT7fJ5YmEtwbASWO2AkP94871WpPOCc8vmYHaORhv5lf75VrV3bD+9nZIrUJamhXN9v9kMlu3wonYVlGe9msU1/cGTgKpx0YmO2fsrKq66rMk8Bh7dd99sDIk+xxxsE5icqhqfsLflkz1pkbukSCBzI5bqG0EGrPGvfK2FeGDseRi1I5eVFuB8WvDp51FvsH13Fcz4+y6n86Oz8kfwPMD02INEiadQAAAABJRU5ErkJggg==" 
        link=ET.SubElement(kolom,'td') 
        link.text=rec.categ_id.name
        for kl in kol:
            kolom=ET.SubElement(body,'td')
            if type(rec[kl]) is float:
               kolom.text="{:,}".format(rec[kl])
               kolom.attrib['align']='right'
            elif type(rec[kl]) is int:
               kolom.text=str(rec[kl])
               kolom.attrib['align']='right'    
            elif type(rec[kl]) is str :    
               kolom.text=rec[kl]
            else:
                isinya=rec[kl]
                #kolom.text=type(rec[kl]).__name__  
                child=ET.SubElement(kolom,'table') 
                #child.attrib['class']='table table-bordered'
                tabelkecil=ET.SubElement(child,'td')
                for isi in isinya:
                    childcolumn=ET.SubElement(tabelkecil,'td')
                    childcolumn.attrib['width']='20px'
                    childcolumn.attrib['bgcolor']='grey'
                    childcolumn.text=isi.attribute_value_ids.name
                baris=ET.SubElement(child,'tr')    
                for isi in isinya:
                    childcolumn=ET.SubElement(tabelkecil,'td')
                    childcolumn.attrib['width']='20px'
                    childcolumn.attrib['bgcolor']='green'
                    childcolumn.text=isi.qty_available  

    kanan= ET.tostring(table)
    return kanan


  

def dbf2eod(filepath,obj):
    hasil=[]
    gagal=0
    JML=0
    DQTY=0
    DTTL=0    
    filename=os.path.basename(filepath)
    linking='<a href="/felino/eod/'+filename+'">'+filename+'</a>'
    
    objects= http.request.env['felino.eoddetail'].search([],limit=30)
    for item in DBF(filepath,encoding='iso-8859-1'):
        bisa=['PLU','D%1','RTN','VOD','DS1']
        tampil=False
        toko=filename[0:4]
        tanggal=filename[4:8]+'-2019'
        tgl=datetime.strptime(tanggal,'%m%d-%Y')
        print(tgl)
        if item['FLAG'] in bisa:
           tampil=True
           JML=JML+1
           idx=bisa.index(item['FLAG'])
           if item['FLAG']=='RTN':
              QTY=-1*item['QTY'] 
           elif  item['FLAG']=='D%1':
              QTY=0 
           elif  item['FLAG']=='DS1':
              QTY=0    
           else:
              QTY=item['QTY'] 
           DQTY=DQTY+QTY    
           DTTL=DTTL+(QTY*item['PRICE'])
           product= http.request.env['felino.felino'].search([('barcode','=',item['CODE'])])
           eod={'name':filename,'code':item['CODE'],'barcode':item['CODE'],'desc':item['DESC'],'qty':QTY,'price':item['PRICE'],'norcp':item['NORCP'],'etype':item['ETYPE'],'flag':item['FLAG'],'cprice':item['CPRICE'],'hide':tampil,'category':product['catagory'],'toko':toko,'loc':tanggal,'tanggal':tgl,'periode':filename[4:6]+'2019'}
           objects.sudo().create(eod)
           hasil.append(eod)  
           
    eod={'name':filename,'link':linking,'Child':JML,'Child1':DQTY,'totalsales':DTTL,'toko':toko}
    obj.sudo().create(eod)
    return hasil 

def importInv():
    conn = pg.connect("postgresql://felino:felino@localhost/nuansabaru")
    cur = conn.cursor()
    pesanerror=''
    gagal=0
    cur.execute("delete from felino_felino;")
    SQ=''
    uk=['ALL','01','2','3','4','5','O','S','M','L','XL','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42','43','44','45']
    X=0
    print(type(uk))
    err=''    
    for item in DBF('/mnt/poserver/ics/DAT/INV.DBF',encoding='iso-8859-1'):
        SQL="insert into felino_felino(id,barcode,article,ukuran,list_price,sale_price,index,ondhand,catagory,description) values(%s,'%s','%s','%s',%s,%s,%s,%s,'%s','%s') ON CONFLICT ON CONSTRAINT felino_felino_pkey DO NOTHING;"
   
        list=item['DESC1'].split(" ")
        article= article=item['DESC1'].replace("'"," ")
        index=0;
        ukuran=''
        for lst in list:
            for u in uk :
                if lst==u:
                   print(item['DESC1'])
                   print(list.index(lst))  
                   ukuran=lst
                #print(ukuran)
                   print("-------------------")
                   print(list)
                   index=uk.index(u)
                   list.pop(list.index(lst))
                   print(list)
            article=''
            for ls in list:
                article=article+' '+ls
                print(article)                        
            article=article.replace("'"," ").lstrip()

        ukuran=ukuran.replace("'"," ")       
        try:
           
           #cur.execute(SQL %(item['CODE'],item['CODE'],article.replace("'"," "),ukuran,item['COSTPRC'],item['SELLPRC'],index,item['LQOH'],item['MCLSCODE'],item['DESC1'].replace("'"," ")))
           #conn.commit()
           http.request.cr.execute((SQL %(item['CODE'],item['CODE'],article.replace("'"," "),ukuran,item['COSTPRC'],item['SELLPRC'],index,item['LQOH'],item['MCLSCODE'],item['DESC1'].replace("'"," "))))
           http.request.cr.commit()       
        except :
           print("ERROR")
           conn.rollback()   
           print("--------------------ERR--------------------------------")
           print(article)
           pesanerror=pesanerror+':'+item['CODE']+':'+item['DESC1']
           gagal=gagal+1
    #f = open("err.log","a")        
    #f.write(err)
    print(pesanerror)
    return str(gagal)+pesanerror

def inv2odoo():
    #mulai=datetime.datetime.now()
    http.request.cr.execute('select * from felino_dbinv order by idx ') 
    data = http.request.cr.fetchall() 
    objects= http.request.env['product.template']
    attr_test= http.request.env['product.attribute'].browse([1])
    for record in data:
        catid=record[9]
        if record[9] is None:
           catid=0
                 
        if record[9] is None:
           nilai=1
        else:
           nilai=record[9]  
        SQL="insert into product_template(tracking,responsible_id,id,name,sequence,type,rental,list_price,sale_ok,purchase_ok,uom_id,uom_po_id,company_id,active,default_code,create_uid,write_uid,available_in_pos,create_date,categ_id)\
             values('none',1,%s,'%s',1,'consu',FALSE,%s,TRUE,TRUE,1,1,1,TRUE,'%s',1,1,TRUE,now(),%s) ON CONFLICT ON CONSTRAINT product_template_pkey DO NOTHING"
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print(SQL %(record[0],record[1],record[3],record[0],nilai))
        http.request.cr.execute(SQL %(record[0],record[1],record[3],record[0],nilai))
        http.request.cr.commit()
        SQL="insert into product_attribute_line(product_tmpl_id,attribute_id) values(\
                  %s,%s) ON CONFLICT DO NOTHING"
        http.request.cr.execute(SQL %(record[0],1) )
        http.request.cr.commit() 
        ls=record[5]
        print(type(ls))
        for isi in ls:
            print(isi['default_code'])
            SQL="insert into product_product(id,product_tmpl_id,default_code,active,create_uid,write_uid)\
            values(%s,%s,'%s',TRUE,1,1) ON CONFLICT DO NOTHING"
            print(SQL %(int(isi['default_code']),record[0],isi['default_code']))
            http.request.cr.execute(SQL %(isi['default_code'],record[0],isi['default_code']) )
            print("----------------kkkk")
            print(id)
            http.request.cr.commit()
            SQL="insert into product_attribute_value_product_product_rel(product_product_id, product_attribute_value_id)\
            values(%s,%s)"
            try:
                http.request.cr.execute(SQL %(isi['default_code'],isi['attribute_value_ids']) )
                http.request.cr.commit()
            except:
                http.request.cr.rollback() 
                  
              
    return         

def carigambar(id):
    gb=http.request.env['product.template'].browse(id)
    x=0
    lokasi=glob.glob('/mnt/poserver/images/**/'+str(id)+'.jpg', recursive=True)
    for nfile in lokasi:
        x=x+1
        if x==1: 
           encoded = base64.b64encode(open(nfile, "rb").read())
           gb.write({'image':encoded,'image_medium':encoded}) 
    return x
class Felino(http.Controller):
      
              
      @http.route('/felino/', auth='public',website=True,type='http')
      def index(self, **kw):
          #objects= http.request.env['felino.felino'].search([],limit=30)
          menu="""
          <div class="panel panel-default" style="margin:4px">
          <ul class="tree">
              <li>
              <input type="checkbox" checked="checked" id="c2" />
              <label class="tree_label" for="c2">Product</label>
                  <ul>
                  <li><span >Per Mclass</span></li>
                  <li><span class="tree_label"><a href="/felino/inv" >Per Mclass</a></span></li>
                  <li><span class="tree_label"><a href="/felino/vendor" >Vendor/Supplier</a></span></li>
                  </ul>
              </li>


              <li>
              <input type="checkbox" checked="checked" id="c3" />
              <label class="tree_label" for="c3">Pembelian</label>
              <ul>
                 <li><span class="tree_label"><a href="/felino/receive" >Harian</span></a></li>
                 <li><span class="tree_label"><a href="/felino/receive/vendor/1">Vendor</a></span></li>
              </ul>
              </li>
            

              <li>
              <input type="checkbox" checked="checked" id="c5" />
              <label class="tree_label" for="c5">Penjualan</label>
              <ul>
                  <li><span class="tree_label"><a href="/felino/analisa">Rekapan EOD </a></span></li>
                  <li><span class="tree_label"><a href="/felino/eod">EOD Dari Toko</a></span></li>
              </ul>
              </li>
                  
              <li>
              <input type="checkbox" checked="checked" id="c6" />
              <label class="tree_label" for="c6">Stock</label>
              <ul> 
                  <li><span class="tree_label"><a href="/felino/analisa">Stock</a></span></li>
              </ul>  
              </li>
              <li> 
              <input type="checkbox" checked="checked" id="c7" />
              <label class="tree_label" for="c7">gateway</label> 
              <ul>
                <li><a href="/felino/gateway/inv">Import Data INV.DBF</a></li>
                <li><a href="/felino/gateway/rcv">Import Data RCV.DBF</a></li>
                <li><a href="/felino/gateway/poserver">Import Master data</a></li>
                <li><a href="/felino/analisa">Transfer Master Data</a></li>
                <li><a href="/felino/analisa">Import Stock Opname(XLS)</a></li>
                <li><span class="tree_label"><a href="/felino/gateway/supplier">supplier</a></span></li>
               </ul>  
              </li> 
          </ul>   
       
          </div>   
          <style>
          .tree { margin: 1em; }

            .tree input {
            position: absolute;
            clip: rect(0, 0, 0, 0);
            }

            .tree input ~ ul { display: none; }

            .tree input:checked ~ ul { display: block; }

            /* ————————————————————–
            Tree rows
            */
            .tree li {
            line-height: 1.2;
            position: relative;
            padding: 0 0 1em 1em;
            }

            .tree ul li { padding: 1em 0 0 1em; }

            .tree > li:last-child { padding-bottom: 0; }

            /* ————————————————————–
            Tree labels
            */
            .tree_item  {
              background: #fdd;
              margin:0
            }
            .tree_label {
            position: relative;
            display: inline-block;
            background: #fff;
            }

            label.tree_label { cursor: pointer; }

            label.tree_label:hover { color: #666; }

            /* ————————————————————–
            Tree expanded icon
            */
            label.tree_label:before {
            background: #000;
            color: #fff;
            position: relative;
            z-index: 1;
            float: left;
            margin: 0 1em 0 -2em;
            width: 1em;
            height: 1em;
            border-radius: 1em;
            content: '+';
            text-align: center;
            line-height: .9em;
            }

            :checked ~ label.tree_label:before { content: '–'; }

            /* ————————————————————–
            Tree branches
            */
            .tree li:before {
            position: absolute;
            top: 0;
            bottom: 0;
            left: -.5em;
            display: block;
            width: 0;
            border-left: 1px solid #777;
            content: "";
            }

            .tree_label:after {
            position: absolute;
            top: 0;
            left: -1.5em;
            display: block;
            height: 0.5em;
            width: 1em;
            border-bottom: 1px solid #777;
            border-left: 1px solid #777;
            border-radius: 0 0 0 .3em;
            content: '';
            }

            label.tree_label:after { border-bottom: 0; }

            :checked ~ label.tree_label:after {
            border-radius: 0 .3em 0 0;
            border-top: 1px solid #777;
            border-right: 1px solid #777;
            border-bottom: 0;
            border-left: 0;
            bottom: 0;
            top: 0.5em;
            height: auto;
            }

            .tree li:last-child:before {
            height: 1em;
            bottom: auto;
            }

            .tree > li:last-child:before { display: none; }

            .tree_custom {
            display: block;
            background: #eee;
            padding: 1em;
            border-radius: 0.3em;
            }
          </style> 
     
          """
          data=[]
          data.append(['Debug   ','/felino/felino'])
          return http.request.render('felino.mclass',{"kanan":searchbutton(),"kiri":menu})

      @http.route(['/felino/gateway/<id>'], auth='public',website=True,type='http')
      def felinotools(self,id=None, **kw):
          st=stock.Stock()
          #st.poserver()
          #st.inv2odoo()
          
          if id=='rcv':
             st.importStock()    
          if id=='inv':
             st.inv2odoo()
          if id=='poserver':
             st.poserver() 
          if id=='supplier':
             data='' 
             http.request.cr.execute('select "CODE"::int as id,"DESC" as name from "SUP"')
             data=http.request.cr.fetchall()
             for da in data:
                 print(da[1])
                 supplier = http.request.env['res.partner'].browse([da[0]])
                 supplier.write({'name':da[1],'display_name':da[1]})




          return http.request.render('felino.mclass',{"kanan":sidebar3(data),"kiri":feltree(data),'judul':judul})

      @http.route(['/felino/analisa','/felino/analisa/<periode>'], auth='public',website=True,type='http')
      def felinoanalisa(self,periode=None, **kw):
          if periode is None:
             periode='022019'   
          sql="""
             select concat('<a href="/felino/analisa/',periode,'">',to_char(to_date(periode,'mmyyyy'),'Month YYYY'),'</a>') 
             from
             (select periode from felino_eoddetail group by 1) t
          """
          http.request.cr.execute(sql)
          kiri=http.request.cr.fetchall()
          sql="""
              select name,toko,periode,date_in,ttl::float
              from (
              select name,toko,periode,tanggal as date_in,sum(qty*price) as ttl from felino_eoddetail
              group by 1,2,3,4 order by 4,1) t
          """

          http.request.cr.execute(sql+" where periode='"+periode+"'")
          tupleFromCursor = http.request.cr.fetchall()
          my_DF = pd.DataFrame(data=list(tupleFromCursor), columns=('name','store','periode','date_in','ttl')).pivot_table(index='store',columns='date_in')
         
          htmldf=my_DF.to_html(justify='right',float_format=lambda x: '{:,.0f}'.format(x),classes='table table-stripped')
          
          return http.request.render('felino.gateway',{'kiri':sidebar(kiri),'kanan':htmldf})

      @http.route(['/felino/analisamclass','/felino/analisamclass/<periode>'], auth='public',website=True,type='http')
      def felino(self,periode=None, **kw):
          if periode is None:
             periode='022019'   
          sql="""
             select concat('<a href="/felino/analisa/',periode,'">',to_char(to_date(periode,'mmyyyy'),'Month YYYY'),'</a>') 
             from
             (select periode from felino_eoddetail group by 1) t
          """
          http.request.cr.execute(sql)
          kiri=http.request.cr.fetchall()
          sql="""
              select name,toko,periode,date_in,ttl::float
              from (
              select name,toko,periode,tanggal as date_in,sum(qty*price) as ttl from felino_eoddetail
              group by 1,2,3,4 order by 4,1) t
          """

          http.request.cr.execute(sql+" where periode='"+periode+"'")
          tupleFromCursor = http.request.cr.fetchall()
          my_DF = pd.DataFrame(data=list(tupleFromCursor), columns=('name','store','periode','date_in','ttl')).pivot_table(index='store',columns='date_in')
         
          htmldf=my_DF.to_html(justify='right',float_format=lambda x: '{:,.0f}'.format(x),classes='table table-stripped')
          
          return http.request.render('felino.gateway',{'kiri':sidebar(kiri),'kanan':htmldf})      
      
            
      @http.route('/felino/sales',  website=True,type='http',auth='public')
      def gatew(self, **kw):
          semua="""
             select * from
             (
             select left(name,4)  as store ,to_date(substr(name,5,4)||'2018','MMDDYYYY') AS Date
             ,totalsales from felino_eodmaster
             ) t order by 2,1 
             """
          http.request.cr.execute(semua)
          data = http.request.cr.fetchall()
          menu=[{'<a href="/felino/salesall">Total Penjualan</a>'},
                {'<a>Total Penjualan per Catagory</a>'},
                {'<a>Total Penjualan per Hari</a>'},
                {'<a>Total Penjualan per Perbulan</a>'},
          ]     
          return http.request.render('felino.gateway',{"kiri":sql2table(menu),"kanan":sql2datatable(data,('11','22','23'))})

      @http.route('/felino/sales/all',  website=True,type='http',auth='public')
      def gatewalls(self, **kw):
          semua="""
             select * from
             (
             select left(name,4)  as store ,to_date(substr(name,5,4)||'2018','MMDDYYYY') AS Date
             ,totalsales from felino_eodmaster
             ) t order by 2,1 
             """
          http.request.cr.execute(semua)
          data = http.request.cr.fetchall()
      @http.route('/felino/sales',  website=True,type='http',auth='public')
      def gatew(self, **kw):
          semua="""
             select * from
             (
             select left(name,4)  as store ,to_date(substr(name,5,4)||'2018','MMDDYYYY') AS Date
             ,totalsales from felino_eodmaster
             ) t order by 2,1 
             """
          http.request.cr.execute(semua)
          data = http.request.cr.fetchall()
          menu=[{'<a href="/felino/salesall">Total Penjualan</a>'},
                {'<a>Total Penjualan per Catagory</a>'},
                {'<a>Total Penjualan per Hari</a>'},
                {'<a>Total Penjualan per Perbulan</a>'},
          ]     
          return http.request.render('felino.gateway',{"kiri":sql2table(menu),"kanan":sql2table(data)})

      @http.route(['/felino/customer'],  website=True,type='http',auth='public')
      def salescustomer(self, **kw):
          judul='data custumer beserta jumlah pembelian'
          semua="""
              select id,name,phone,concat('</a>',product,'</a>') as product from
              (
              select id,left(name,10) as name,phone,(select count(*) from product_template where left(default_code,3)::int=a.id) as product from res_partner a
              where a.customer=True
              ) t 
                """
          data = ninofelinosql(semua)
          return http.request.render('felino.gateway',{"judul":judul,"kanan":sql2datatable(data,('1.Code','2.Nama','Telp','Product'))})    



      @http.route(['/felino/vendor','/felino/vendor/<id>'],  website=True,type='http',auth='public')
      def salesvendors(self,action=None,id=None,product=None, **kw):
          DF=None
          print("VENDOR-----------------------------------")
          judul='data vendor beserta jumlah product <a href="/felino/receive/upload">Import Rcv<a><a href="/felino/process/vendor">Import Vendor<a>'
          semua="""
          select concat('<li><a href="/felino/vendor/',partner_id,'">',names,'</a></li>')  
          from(
          select (select name from res_partner where id=partner_id) AS names,partner_id from stock_picking group by 1,2
          ) t 
          """
          http.request.cr.execute(semua)
          dat=http.request.cr.fetchall()
          data=''
          for rec in dat:
              data=data+rec[0] 
                 #http.request.cr.execute(sql)
                 #tupleFromCursor = http.request.cr.fetchall()
                 #DF = pd.DataFrame(data=list(tupleFromCursor), columns=('supplier','podate','total','receive')).pivot_table(index=['supplier'],columns='podate',values=['total','receive']).to_html(justify='right',float_format=lambda x: '{:,.0f}'.format(x),classes='table table-stripped')
          
          if not id is None:
             detail=http.request.env['product.template'].search([("vendor","=",int(id))])
             DF=fel_product_template(detail)
            
          return http.request.render('felino.vendor',{"judul":judul,"kiri":data,"kanan":DF})    
   
      @http.route('/felino/store',  website=True,type='http',auth='public')
      def salesstore(self, **kw):
          judul='rekapan data eod perbulan'
          semua="""
                select id,name,code,
                (select count(*) from felino_eoddetail where left(name,4)=t.code and substr(name,5,2)='01') as jan,
                (select count(*) from felino_eoddetail where left(name,4)=t.code and substr(name,5,2)='02') as feb,
                (select count(*) from felino_eoddetail where left(name,4)=t.code and substr(name,5,2)='03') as mar,
                (select count(*) from felino_eoddetail where left(name,4)=t.code and substr(name,5,2)='04') as apr
                
                from 
                (select id,name,code from stock_warehouse) t 
                """
          http.request.cr.execute(semua)
          data = http.request.cr.fetchall()
          return http.request.render('felino.gateway',{"judul":judul,"kanan":sql2datatable(data,('id','Name','code','Jan','feb','mar','appr'))})    

      @http.route(['/felino/customer'],  website=True,type='http',auth='public')
      def salescustomer(self, **kw):
          judul='data custumer beserta jumlah pembelian'
          semua="""
              select id,name,phone,concat('</a>',product,'</a>') as product from
              (
              select id,left(name,10) as name,phone,(select count(*) from product_template where left(default_code,3)::int=a.id) as product from res_partner a
              where a.customer=True
              ) t 
                """
          data = ninofelinosql(semua)
          return http.request.render('felino.gateway',{"judul":judul,"kanan":sql2datatable(data,('1.Code','2.Nama','Telp','Product'))})   
 
#- stock
    
#---------------------------------------------------

      @http.route(['/felino/receive','/felino/receive/<day>','/felino/receive/print/<id>'],  website=True,type='http',auth='public')
      def salesreceive(self,day=None,id=None ,**kw):
          sql="""
          select 
            concat('<li><input type="checkbox" checked="checked" id="C',ROW_NUMBER() OVER(ORDER BY date_trunc),'" />',
            '<label for="c',ROW_NUMBER() OVER(ORDER BY date_trunc),'" class="tree_label">',
            to_char(date_trunc,'Month YYYY'),
            '</label>',
            '</li>'),
            json_agg
            from
            (
            select date_trunc
            ,json_agg(json_build_object('tgl',scheduled_date,'link',
            concat('<li><span class="tree_label"><a href="/felino/receive/',scheduled_date,'">', to_char(scheduled_date,'day DD'),'</a></span></li>')
            ) order by  1)
            from
            (
            select date_trunc('month',a.scheduled_date),b.scheduled_date 
            from stock_picking a
            left outer join stock_picking b 
            on date_trunc('month',a.scheduled_date)=date_trunc('month',b.scheduled_date)
            group by 1,2 
            order by 1,2 
            ) t group by 1
            ) z            
          """
          script="""
          <script>
                 
         $(".cetak").click(function() {
            console.log(this.id); 
            alert(this.id);
            var DocumentContainer = document.getElementById('X'+this.id);
            var WindowObject = window.open('');
            WindowObject.document.writeln(DocumentContainer.outerHTML);
            $.ajax({
                    type: "GET",
                    url: "/felino/print",
                    data: JSON.stringify(xmlToJson(DocumentContainer.outerHTML)),
                    contentType: "application/xml",
                    dataType: "xml",
                    cache: false,
                   });

            WindowObject.print()
            WindowObject.close()

         });
         function xmlToJson(xml) {
	
	// Create the return object
	var obj = {};

	if (xml.nodeType == 1) { // element
		// do attributes
		if (xml.attributes.length > 0) {
		obj["@attributes"] = {};
			for (var j = 0; j < xml.attributes.length; j++) {
				var attribute = xml.attributes.item(j);
				obj["@attributes"][attribute.nodeName] = attribute.nodeValue;
			}
		}
	} else if (xml.nodeType == 3) { // text
		obj = xml.nodeValue;
	}

	// do children
	if (xml.hasChildNodes()) {
		for(var i = 0; i < xml.childNodes.length; i++) {
			var item = xml.childNodes.item(i);
			var nodeName = item.nodeName;
			if (typeof(obj[nodeName]) == "undefined") {
				obj[nodeName] = xmlToJson(item);
			} else {
				if (typeof(obj[nodeName].push) == "undefined") {
					var old = obj[nodeName];
					obj[nodeName] = [];
					obj[nodeName].push(old);
				}
				obj[nodeName].push(xmlToJson(item));
			}
		}
	}
	return obj;
};
         function tableToJson(table) { 
            var data = []; // first row needs to be headers var headers = []; 
            for (var i=0; i<table.rows[0].cells.length; i++) {
            headers[i] = table.rows[0].cells[i].innerHTML.toLowerCase().replace(/ /gi,''); 
            } 
            // go through cells 
            for (var i=1; i<table.rows.length; i++) { 
            var tableRow = table.rows[i]; var rowData = {}; 
            for (var j=0; j<tableRow.cells.length; j++) { 
            rowData[ headers[j] ] = tableRow.cells[j].innerHTML; 
            } data.push(rowData); 
            } 
            return data; 
            }
                 
          </script>
          """
          if not id is None:
             sql=""" 
             select concat(extract(year from scheduled_date)) as tahun
            ,json_agg(json_build_object('link',concat('<li><a href="/felino/receive/vendor/',partner_id,'">',(select name from res_partner where id=partner_id),'</a></li>'))) as link
            from stock_picking
            group by 1
             """

          http.request.cr.execute(sql)
          data = http.request.cr.fetchall()
          kiri='<h3>Penerimaan Barang</h3><ul class="tree"><li>'
          kanan=''
         
          
          for record in data: 
              kiri=kiri+record[0]
              childtext=''
              print(";llllllllllllllllllllllllllllllllllllllllllll")
              isinya=record[1]
              print(isinya)
              for chi in isinya:
                  #childtext=childtext+json.dumps(chi)
                  childtext=childtext+str(chi['link'])
              kiri=kiri+childtext        
          kiri=kiri+'</li></ul>'
          html=[]
          tabelkolom=['name','partner_id','move_lines'] 
          objects= http.request.env['stock.picking'].search([('partner_id','=',id)]) 
             
          html.append('<table class="table">')
          for rec in objects:
              html.append('<tr id="XT'+str(rec.id)+'">')
              html.append('<td>%s<br><small><a href="#" class="cetak" id="T%s">%s</a></small><a href="/felino/receive/print/%s" class="btn btn-info btn-xs">Print</a><button class="btn btn-primary btn-xs" onclick="cetak()">Barcode</button</td>' %(rec.name,rec.id,rec.partner_id.name,rec.id))
               
              listpanda=[]
              dictpanda={}
              idx=0
              rec.move_lines.sorted(key=lambda r: r.product_id.categ_id)
              for isimlines in rec.move_lines:
                  idx=idx+1
                  row={'id':idx,'article':'['+isimlines.product_id.categ_id.name+'] '+isimlines.product_id.name,'size':isimlines.product_id.attribute_value_ids.name,'qty':isimlines.move_line_ids.qty_done}
                  listpanda.append(row)
                     #print(isimlines.product_id.)
                  if idx>0:
                     df=pd.DataFrame(listpanda)
                     pv=pd.pivot_table(df,index=["article"],columns='size',values='qty',fill_value='')
                     pv.fillna(0)
                     html.append('<td>%s</td>' %(pv.to_html(justify='right',float_format=lambda x: '{:,.0f}'.format(x),classes='table table-stripped table-hover')) )
                 #print(type(rec[ko]))  
                     html.append('</tr>')       
                  kanan=kanan+rec.name
                  print(kanan)
          html.append('</table>')    
          kanan=''.join(str(e) for e in html)



          if not id is None:
             return  http.request.render('felino.print')    
          if not day is None:
             html=[]
             tabelkolom=['name','partner_id','move_lines'] 
             objects= http.request.env['stock.picking'].search([('scheduled_date','=',day)]) 
             
             html.append('<table class="table">')
             for rec in objects:
                 html.append('<tr id="XT'+str(rec.id)+'">')
                 html.append('<td>%s<br><small><a href="#" class="cetak" id="T%s">%s</a></small><a href="/felino/receive/print/%s" class="btn btn-info btn-xs">Print</a><button class="btn btn-primary btn-xs" onclick="cetak()">Barcode</button</td>' %(rec.name,rec.id,rec.partner_id.name,rec.id))
                 
                 listpanda=[]
                 dictpanda={}
                 idx=0
                 rec.move_lines.sorted(key=lambda r: r.product_id.categ_id)
                 for isimlines in rec.move_lines:
                     idx=idx+1
                     row={'id':idx,'article':'['+isimlines.product_id.categ_id.name+'] '+isimlines.product_id.name,'size':isimlines.product_id.attribute_value_ids.name,'qty':isimlines.move_line_ids.qty_done}
                     listpanda.append(row)
                     #print(isimlines.product_id.)
                 if idx>0:
                    df=pd.DataFrame(listpanda)
                    pv=pd.pivot_table(df,index=["article"],columns='size',values='qty',fill_value='')
                    pv.fillna(0)
                    html.append('<td>%s</td>' %(pv.to_html(justify='right',float_format=lambda x: '{:,.0f}'.format(x),classes='table table-stripped table-hover')) )
                 #print(type(rec[ko]))  
                 html.append('</tr>')       
                 kanan=kanan+rec.name
                 print(kanan)
             html.append('</table>')    
             kanan=''.join(str(e) for e in html)

          return http.request.render('felino.mclass',{"kiri":kiri,"kanan":kanan,"script":script})
   
      
      
      @http.route(['/felino/mclass','/felino/mclass/<mcla>'],  website=True,type='http',auth='public')
      def salesmclasss(self,mcla=None, **kw):
          kanan=''
          semua=receive.Receive.new_catagory_mclass
          http.request.cr.execute(semua)
          data = http.request.cr.fetchall()
          return http.request.render('felino.mclass',{"kiri":receive.Receive.new_tree_mclass %(data)})  

      @http.route('/felino/sales/cat',  website=True,type='http',auth='public')
      def gatewall(self, **kw):
          semua="""
             select * from felino_eoddetail limit 100
             
             """
          http.request.cr.execute(semua)
          data = http.request.cr.fetchall()
              
          return http.request.render('felino.gateway',{"kiri":sql2table(sidemenu()),"kanan":sql2table(data)})
         

      @http.route('/felino/data/<cari>', auth='public')
      def invdbfcari(self,cari=None,**kw):
          tampil=['id','vendor','image','name','categ_id','qty_available','list_price','standard_price','product_variant_ids']
          products= http.request.env['product.template'].search([('name','like',cari)],limit=30)
          
          sumber=ET.Element('table')
          sumber.attrib['class']="table table-striped"
          sumber.attrib['id']="kanan"
          root = ET.SubElement(sumber,'thead')
          root.text="header"
          judul= ET.SubElement(root,'tr')
          for jd in tampil:
              ET.SubElement(judul,'th').text=jd

          body = ET.SubElement(sumber,'tbody')
          

          for rec in products:
              print('-------------------------') 
              baris=ET.SubElement(body,'tr')
              for kol in tampil:
                  kolom=ET.SubElement(baris,'td')
                  if type(rec[kol]) is str:
                       kolom.text=rec[kol]
                       kolom.attrib['style']='text-align:left;'
                  elif type(rec[kol]) is int:
                       
                       if kol =='id':
                          detail=ET.SubElement(kolom,'a')
                          detail.attrib['href']='/felino/product_template/'+str(rec[kol])
                          detail.text= str(rec[kol])
                       else:
                           kolom.text=(str(rec[kol])) 
                  elif type(rec[kol]) is float:

                       #kolom.text=str(rec[kol])
                       kolom.text="{0:,}".format(rec[kol])
                  else :
                       kolom.text="rec."
                       #print(type(rec[kol])
                  print(type(rec[kol]))
                  #print(isinstance(rec[kol],'odoo.api.product.category' )) 
          return ET.tostring(sumber)

       

      @http.route('/felino/debugsql/<sql>', auth='public')
      def debugsql(self,sql=None,**kw):
          data=ninofelinosql(sql)
          print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
          con= http.request.db
          #print(dir(sudo().conn))
          #dataframe = psql.read_sql(sql,con)
          #pd.DataFrame(data=list(tupleFromCursor), columns=('name','store','date_in','ttl')).pivot_table(index='store',columns='date_in')

          #return ''.join((map(str,data)))   
          return json.dumps(data)
          #return data
      @http.route('/felino/print', auth='public', methods=['GET'],website=True, csrf=False)    
      def cetak(self, **kw):
          print("<<request----------------------------->>>",kw)
          data=json.dumps(kw)
          print(data)

          return "Print"     
      @http.route('/felino/product', auth='public')
      def inv(self, **kw):
          #http.request.cr.execute('delete from product_product;delete from product_template;')
          #http.request.cr.execute('select * from felino_dbinv order by idx ') 
          data = http.request.cr.fetchall() 
          objects= http.request.env['product.template']
          attr_test= http.request.env['product.attribute'].browse([389])
          print(attr_test.value_ids.ids)
          for record in data:
              px=[]
              attx=[]
              print(record[6])
              attx=record[6]
              #attx=record[5]
              for data in record[5]:
                  px.append((0,0,data))
                  #px.append([0,0,data])
              
              print("------------------------------")
              print(attx)
              print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

              productlist = {'id':record[0],'name':record[1],'list_price':record[3],'standard_price':record[2],
              'product_variant_ids':px,          
              #'attribute_line_ids': [(0, 0, {'attribute_id': 1,'value_ids':[(6, 0,attx)],}),
              'attribute_line_ids': [(0, 0, {'attribute_id': 1,'value_ids':[(4,0,attx)],}),
              
              ] ,
              
              #attribute_value_ids,
              #'qty_availab
              } 
              #try:
              objects.sudo().create(productlist)
              http.request.cr.commit()
             
              
          return http.request.render('felino.listing')  


     

# ------------------------------------------ EOD -------------
      @http.route('/felino/uploadfile',type='http',auth='public',methods=['GET', 'POST'],website=True, csrf=False)
      def image_handle(self, **post): 
        fname= post.get('attachment').filename
        files = post.get('attachment').stream.read()
        filename='/var/tmp/'+fname
        fp =open(filename,'wb')        
        fp.write(files)        
        fp.close()        
        objeod= http.request.env['felino.eodmaster']
        dbf2eod(filename,objeod)
        return http.request.redirect('/felino/eod/'+fname)       
     
      @http.route(['/felino/eod/<soday>','/felino/eod'],type='http',auth='public',website=True)
      def eodsearch(self,soday=None, **kw): 
          filenames= http.request.env['felino.eodmaster'].sudo().search([]) 
          detail= http.request.env['felino.eoddetail'].sudo().search([("name","=",soday)]) 
          #detail.filtered('hide'==True)
          return http.request.render('felino.byeod',{'fnames':filenames,'detail':detail})  

      @http.route('/felino/eod/upload', auth='public',type='http',website=True)
      def eodupload(self, **kw):
          fnames=glob.glob('/mnt/poserver/SALES/*.DBF')
          http.request.cr.execute("delete from felino_eoddetail;SELECT setval('felino_eoddetail_id_seq', 1, FALSE);")
          http.request.cr.execute("delete from felino_eodmaster;SELECT setval('felino_eodmaster_id_seq', 1, FALSE);")
          http.request.cr.commit()
          objeod= http.request.env['felino.eodmaster']
          for filepath in fnames:
              isi=dbf2eod(filepath,objeod)
              print(isi)       
          return http.request.redirect('/felino/eod')

      @http.route('/felino/pgproduct', auth='public',website=True,type='http')
      def invpro(self, **kw):
          http.request.cr.execute('select * from felino_dbinv')
          data = http.request.cr.fetchall() 
          
          return http.request.render('felino.gateway',{'kanan':data}) 

        
# ****************************************  EOD *******************
# === INV
      @http.route(['/felino/inv','/felino/inv/cat/<cat>'], auth='public',type='http',website=True)
      def invdbflama(self,cat=None, **kw):
          sql="""
        select category,JML,json_agg(json_build_object('name',name
        ,'link',concat('<li><span class="tree_label"><a href="/felino/inv/cat/',id,'">',name,'</a></span></li>')
        ) ORDER BY 1) ,concat('<li><input type="checkbox" checked="checked" id="c',
        row_number() over (order by category),'"/><label class="tree_label" for="c',
        row_number() over (order by category),'">'
        ,category,'</label></li>')
        from(

        select left(name,2) as category,count(*) as JML from product_category
        GROUP BY 1
        ) t
        left outer join product_category c on left(t.category,2)=left(c.name,2)
        group by 1,2;
          """
          kanan=''
          if not cat is None:
             detail= http.request.env['product.template'].sudo().search([('categ_id','=',int(cat))])
             kanan='' 
             table =ET.Element('table')
             table.attrib['class']='table table-striped' 
             body  =ET.SubElement(table,'tbody')
             kol=['vendor','name','list_price','standard_price','product_variant_ids']
             for rec in detail:
                 #carigambar(rec.id)
                 baris=ET.SubElement(body,'tr')
                 kolom=ET.SubElement(body,'td') 
                 link=ET.SubElement(kolom,'a') 
                 link.attrib['href']='/felino/loadimage/'+str(rec['id'])   
                 gambar=ET.SubElement(link,'img')
                 try:
                     gambar.attrib['src']="data:image/png;base64,%s" %(rec.image_small.decode("utf-8"))
                 except:
                     gambar.attrib['src']="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAAAAACPAi4CAAAACXZwQWcAAABAAAAAQADq8/hgAAAEWklEQVRYw9WX6XKjRhCAef8HiySQvGt5vfZuEselOUAcEpe4GdI9MAgQOjb5k3SVyzY1801PX9OtNf9StP80QJR5miRpXtb/AFCnvmMySgmhlJn2Mal+BSBSj1NCGeNSGAMOd0/iQYCI95TAXnm+FCr/I2ZYPwJILEJhPaGm7flBFIW+Z5sUvwEivguovG7pMR0cV2e+BbYArF3cBqQclKfEvryvSB2KaHa6BYhgDSP7ZN7gmUNQCf86wCdgcBaKq04/cTzAuwbA/czKb8VdZYMSI8IAEOJ+XjTiFkF4SDjOARIIHLiBK+4E/xHOIdEloMSAAwZx7hEOBKIquwA4lFPbR/3uEhzCqSUmgBiwrGgeIlQm5b0zO0CN3yKw34QgQC4JKZqrGAFC0MpWvuwJ3V6hWD3BI5wchoDaBAumzYQgmsrd7ewZx5bosHIAAAtQp4+nXUuA+2yXy9Xyi4OsIorjauBLZQWtd0Gqrt3EvCXQlb4BMZYfsPP7cr0gvS4FaNw6Qus0ovtez8DZcYyHt8Wmk9XWdF+Mjf570Ke4q46UgAgUCtX55mKl/wSbsD83hrEE0VGJ1RrEWHz2aaXuIAEe7b3SNG/601oSzL/W20/T2r2uDNACARvjWelZQTTaCiCg2vSR1bzrsFgSQMk8SbPi8FWX+0GFbX2OXMarDoAmOGfo+wpXt7cwj4Hv+1n+rSMYW3HOfS4TAgHZIDIVYG38wNzchyB+kj4ZUwB4npw6ABokmgA2qz9kfbIkoWDLzQSQ0tbw2gA20kA/nmyqCHG8nmqQd2prbSKQZAIwnk5B5PSE/EWfACCUZGFSgHQKeE6DsCcExfc5wKEDRLMaJHBwTwA/zFzhOLBBPGODoCfEyYUb0XVBB1AGHXvho/SVDsSjF15QrtMG1xlpsDbCrCewj7UxAWAJSjsAlJOuHI0AX9Mi8IMgsJnMC2MMOJA2f7RhXI8AG/2LVxZZVlQWmKElnAFiT5nMH62L67Mb3lTmbIzVK3Uc9r6GvJAEyMa6d0KXP1oXliqbRPPzN0NvBcrBAmSpr37wlrB8GeRS6zkJECZVNRKeuLfty1C+wc/zp7TD9jVQN7DUDq2vkUEzfAymIl9uZ5iL1B0U1Rw7surmc4SE/sUBE3KaDB8Wd1QS7hJQga4Kayow2aAsXiV0L458HE/jx9UbPi33CIf+ITwDSnxM/IcIcAGIrHzaH+BX8Ky4awdq41nBZYsjG4/kEQLjg9Q5A9A1jJ7u3CJEa1OzmuvSKgubwPA24IT7WT7fJ5YmEtwbASWO2AkP94871WpPOCc8vmYHaORhv5lf75VrV3bD+9nZIrUJamhXN9v9kMlu3wonYVlGe9msU1/cGTgKpx0YmO2fsrKq66rMk8Bh7dd99sDIk+xxxsE5icqhqfsLflkz1pkbukSCBzI5bqG0EGrPGvfK2FeGDseRi1I5eVFuB8WvDp51FvsH13Fcz4+y6n86Oz8kfwPMD02INEiadQAAAABJRU5ErkJggg==" 
                  
                 for kl in kol:
                     kolom=ET.SubElement(body,'td')
                     if type(rec[kl]) is float:
                         kolom.text="{:,}".format(rec[kl])
                         kolom.attrib['align']='right'
                     elif type(rec[kl]) is int:
                         kolom.text=str(rec[kl])
                         kolom.attrib['align']='right'    
                     elif type(rec[kl]) is str :    
                         kolom.text=rec[kl]
                     else:
                         isinya=rec[kl]
                         #kolom.text=type(rec[kl]).__name__  
                         child=ET.SubElement(kolom,'table') 
                         #child.attrib['class']='table table-bordered'
                         for isi in isinya:
                             childcolumn=ET.SubElement(child,'td')
                             childcolumn.attrib['width']='20px'
                             childcolumn.attrib['bgcolor']='grey'
                             childcolumn.text=isi.attribute_value_ids.name

                             print(isi.attribute_value_ids.name)
                         
                     print(type(rec[kl]))
             kanan= ET.tostring(table)                    
             #return ET.tostring(table)
          http.request.cr.execute('''
          select 
          concat('<li><a href="/felino/inv/cat/',categ_id,'">',
          (select name from product_category where id=t.categ_id),'<span class="badge badge-secondary">',j,'</span>','</a></li>') 
          from
          (
          select categ_id,count(*) as j from product_template group by 1 order by 1
          ) t
          ''')
          http.request.cr.execute(sql)
          data = http.request.cr.fetchall() 
          kiri=''
          detail=''
          childtext=''
          kiri='<ul class="tree">'
          i=0 
          for rec in data:
              i=i+1
              kiri=kiri+'<li><input type="checkbox" checked="checked" id="c'+str(i)+'"/><label class="tree_label" for="c'+str(i)+'">'+rec[0]+'</label></li>'
              child=rec[2]
              childtext=''
              for rw in child:
                  childtext=childtext+rw['link']
                  #'<li><span class="tree_label">'+rw['link']+'</span></li>'
              kiri=kiri+'<ul>'+childtext+'</ul>'   
          kiri=kiri+'</ul>'  

          return http.request.render('felino.mclass',{'kiri':kiri,'detail':detail,'kanan':kanan}) 
       
      @http.route('/felino/loadimage/<id>',type='http',auth='public',website=True)
      def loadimage(self,id=None, **kw):
          gb=http.request.env['product.template'].sudo().search([('categ_id','=',7103)])
          for g in gb:
              print(g)
              carigambar(g.id)
          return "encoded"
      @http.route('/felino/pindahimage',type='http',auth='public',website=True)
      def pindahimage(self,id=None, **kw):
          gb=http.request.env['product.template'].sudo().search([('company_id','=',1)])
          for g in gb:
              print(g)
              carigambar(g.id)
          return "encoded"    

      

         
      @http.route('/felino/sales/<cat>',type='http',auth='public',website=True)
      def salesbyvendor(self,cat=None, **kw):
          http.request.cr.execute('select concat(name) from felino_sales_top')
          data = http.request.cr.fetchall() 
          #detail= http.request.env['felino.felino'].sudo().search([('catagory','=',cat)]) 
          SQL="""
          select * from felino_eoddetail where left(barcode,3)='%s'
          """
          http.request.cr.execute(SQL %(cat))
          product=http.request.cr.fetchall() 
         
          return http.request.render('felino.gateway',{'kiri':data,'kanan':sql2table(product)})     
      

      @http.route('/felino/process/<cari>', auth='public')
      def felpro(self,cari=None,**kw):
          st=stock.Stock() 
          if cari=="poserver":
             st.poserver() 
          if cari=="inv2odoo":
             st.inv2odoo()
          if cari=="stock":
             st.inv2odoo()
          if cari=="getpict":
             st.inv2odoo()
          if cari=="vendor":
             print("import vendor-----------------------------------------") 
             st.importVendor()
             http.request.cr.execute('select "CODE"::int as id ,"DESC" as name from "SUP"')
             data = http.request.cr.fetchall() 
             for rec in data:
                 gb=http.request.env['res.partner'].browse([int(rec[0])])
                 gb.write({'name':rec[1]})




          return "proces"

      @http.route('/felino/stock', auth='public')
      def felstock(self,cari=None,**kw):
          st=stock.Stock()
          thread6.run_threaded(st.poserver())
          thread6.run_threaded(st.importStock())
          thread6.run_threaded(st.inv2odoo())  
          return "http.request.render('point_of_sale.index')"

      @http.route('/felino/saveimage',type='http',auth='public',methods=['GET', 'POST'],website=True, csrf=False)
      def saveimage(self,**post):

          return "save"
      @http.route('/felino/poserverimage',type='http',auth='public',methods=['GET', 'POST'],website=True, csrf=False)
      def poserverimage(self,**post):
          print("ppppppppppppppppppppppppppppppppppppp")
          for filename in glob.iglob('/mnt/poserver/IMAGES/*.*', recursive=True):
              print(filename)
          return "poserverimage" 
      @http.route('/felino/rest/mclass/<id>',  website=True,type='http',auth='public')
      def rests(self,id=None,**kw):
          record={'image','default_code','name','lst_price','product_variant_ids','price','qty_available','seller_ids'}
          ninobar="""
          <img src="/felino/imagess></img>
          """
          hasil=''
          pro= http.request.env['product.template'].search([["categ_id","=",int(id)]])
          sumber=ET.Element('div')
          menu=ET.SubElement(sumber,'div')
          menu.attrib['class']="pagination"
          tombol=ET.SubElement(menu,'li')
          isi=ET.SubElement(tombol,'a')
          isi.attrib['class']='page-item'
          isi.text='CSV'
          
          tombol=ET.SubElement(menu,'li')
          isi=ET.SubElement(tombol,'a')
          isi.attrib['class']='page-item'
          isi.text='Print'
           
          tombol=ET.SubElement(menu,'input')
          tombol.attrib['class']='page-item'
          tombol.attrib['place-holder']='Search'

          tombol=ET.SubElement(menu,'li')
          isi=ET.SubElement(tombol,'a')
          isi.attrib['class']='page-item'
          isi.text='Upload Stock'
          
           

          table =ET.SubElement(sumber,'table')
          table.set('class','table table-striped')
          judul = ET.SubElement(table,'thead')
          #judu=ET.SubElement(judul,'tr')         
          for rec in record:
              pass
              th=ET.SubElement(judul,'th')
              th.text=rec

          data = ET.SubElement(table,'tbody') 
          for product in pro:
              baris = ET.SubElement(data, 'tr')
              #items = ET.SubElement(baris, 'td')
              print(product)
              print('lllllllllllllllllllllllllllllllllllllllllll')
              
              hasil=''
              for re in record:
                  items = ET.SubElement(baris, 'td')
                  #items.set('name',re) 
                  #items.set('id',re) 
                  print(type(product[re]))
                  if   type(product[re]) is str:
                       items.text = product[re]
                  elif type(product[re]) is float:
                       items.text =str(product[re]) 
                  #elif type(product[re]) is bool:
                  #     gb = ET.SubElement(items, 'img')
                  #     gb.attrib['src']='http://localhost:8069/web/image?model=product.template&id=%s&field=image_medium&unique=02182019155046' %(product.id)
                  #     print('image--------------------image')
                      
                  else:
                      if re=='image':
                         gb = ET.SubElement(items, 'img')
                         gb.attrib['src']='http://localhost:8069/web/image?model=product.template&id=%s&field=image_medium' %(product.id)
                         url=http.request.env['ir.config_parameter'].get_param('web.base.url')
                         print('url---------------------------->')
                         print(url) 
                         #gb.attrib['src']=url+'/web/image?model=product.template&id=%s&field=image_medium' %(product.id)
                         #&unique=02182019155046
                         gb = ET.SubElement(items, 'a')
                         gb.text='Edit'
                         gb.attrib['href']='http://localhost:8069/web#id=%s&view_type=form&model=product.template&menu_id=290&action=345' %(product.id)
                        
                        
                         frm = ET.SubElement(items, 'form')
                         #frm.attrib['name']='attachment'
                         frm.attrib['action']='/felino/saveimage'
                         frm.attrib['method']='POST'
                         frm.attrib['enctype']='multipart/form-data'
                         frm.attrib['target']='fileframe'
                         frm.attrib['id']=str(product.id)
                         ul = ET.SubElement(frm, 'div')
                         ul.attrib['class']='input-group-prepend'
                         gb = ET.SubElement(ul, 'input')                        
                         gb.attrib['type']="hidden"
                         gb.attrib['id']='id'
                         gb.attrib['value']=str(product.id)                       
                         gb = ET.SubElement(ul, 'input')                        
                         gb.attrib['type']="file"
                         gb.attrib['name']='attachment'
                         gb.attrib['accept']="image/*"
                         gb = ET.SubElement(ul, 'input')
                         gb.attrib['type']="submit"
                         


                      if re=='product_variant_ids':
                         #itemsd=ET.SubElement(baris,'td')
                         ukuran=product['product_variant_ids']
                         tb = ET.SubElement(items, 'table')
                         tb.attrib['bgcolor']='#009900'
                         tb.attrib['border']='1'
                         for ukur in ukuran:
                             itemsdetail = ET.SubElement(tb,'td')
                             itemsdetail.attrib['bgcolor']='#009900'
                             itemsdetail.attrib['width']='30px'
                             itemsdetail.attrib['align']='center'

                             #itemsdetail.attrib['padding']='1px'
                             itemsdetail.set('name','variant') 
                             subitemsdetail = ET.SubElement(itemsdetail,'small')
                             subitemsdetail.text=ukur.attribute_value_ids.name

                 
              
              hasil= ET.tostring(sumber)  
             
          return hasil



# === INV
      
      @http.route('/felino/debug', website=True,type='http',auth='public')
      def fdebuge(self, **kw):
          sqlclas="""
          select t.name,json_agg(json_build_object('name',b.name)) from
          (
          select left(name,2) as name from product_category 
          group by 1 order by 1
          ) t 
          left outer join product_category b on t.name=left(b.name,2)
          group by 1  
          """
          #where t.name like'M%'
        
          
          cari=http.request.cr.execute(sqlclas)
          results=http.request.cr.fetchall()
          print("JJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ")
          print(results)
          root =ET.Element('root')
          for re in results:
              #print(re)
              baris=ET.SubElement(root,'li')
              baris
              baris.text=re[0]
              
              #
              print(re[1])
              kolom=re[1]
              for kol in kolom:
                  kolom=ET.SubElement(root,'ul')
                  kolom.attrib['class']='jqtree-tree jqtree-toggler'
                  kolom.text=kol['name']
                  print(kol['name'])
          css="""

          <style>
          .detail color=red;
          </style>
          """    
              

          return http.request.render('felino.mclass',{'kiri':ET.tostring(root)})
      @http.route('/felino/template', auth='public')
      def invsupload(self, **kw):
          #http.request.cr.execute('delete from product_product;delete from product_template;DELETE FROM product_attribute_line')
          http.request.cr.execute('select * from felino_dbinv order by idx ') 
          print("-startrrrrrrrrrrrrrrrrrrrrrrrrrr") 
          data = http.request.cr.fetchall() 
          objects= http.request.env['product.template']
          attr_test= http.request.env['product.attribute'].browse([1])
          # INSERT INTO public.product_attribute(
          # id, name, sequence, create_variant, create_uid, create_date, 
          # write_uid, write_date)
          print(attr_test.value_ids.ids)
          for record in data:
              catid=record[9]
              if record[9] is None:
                 catid=0
                 
              print("------------------------------")
              print(record[9],record[1])
              print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
              if record[9] is None:
                 nilai=1
              else:
                 nilai=record[9]  
              SQL="insert into product_template(tracking,responsible_id,id,name,sequence,type,rental,list_price,sale_ok,purchase_ok,uom_id,uom_po_id,company_id,active,default_code,create_uid,write_uid,available_in_pos,create_date,categ_id)\
               values('none',1,%s,'%s',1,'consu',FALSE,%s,TRUE,TRUE,1,1,1,TRUE,'%s',1,1,TRUE,now(),%s) ON CONFLICT ON CONSTRAINT product_template_pkey DO NOTHING"
              print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
              print(SQL %(record[0],record[1],record[3],record[0],nilai))
              http.request.cr.execute(SQL %(record[0],record[1],record[3],record[0],nilai))
              http.request.cr.commit()
              SQL="insert into product_attribute_line(product_tmpl_id,attribute_id) values(\
                  %s,%s) ON CONFLICT DO NOTHING"
              http.request.cr.execute(SQL %(record[0],1) )
              http.request.cr.commit() 
              ls=record[5]
              print(type(ls))
              for isi in ls:
                  print(isi['default_code'])
                  SQL="insert into product_product(id,product_tmpl_id,default_code,active,create_uid,write_uid)\
                  values(%s,%s,'%s',TRUE,1,1) ON CONFLICT DO NOTHING"
                  print(SQL %(int(isi['default_code']),record[0],isi['default_code']))
                  http.request.cr.execute(SQL %(isi['default_code'],record[0],isi['default_code']) )
                  print("----------------kkkk")
                  print(id)
                  http.request.cr.commit()
                  SQL="insert into product_attribute_value_product_product_rel(product_product_id, product_attribute_value_id)\
                  values(%s,%s)"
                  try:
                      http.request.cr.execute(SQL %(isi['default_code'],isi['attribute_value_ids']) )
                  
                      http.request.cr.commit()
                  except:
                      http.request.cr.rollback() 
                  
              
              
          return http.request.render('felino.listing')  
      


    





