SELECT id,REGEXP_REPLACE(article,'\d\d\d.\d00|\d\d.\d00|RP.\d\d.\d\d\d','')
,ukuran
,substring(article from '\d\d\d.\d00|\d\d.\d00') as keterangan
,article,ukuran,"DESC1"
  FROM public."INV";