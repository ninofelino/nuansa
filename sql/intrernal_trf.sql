select json_build_object('name',name,'detail',isi)
from
(
SELECT a."TRNUM" as  name ,a."TRDATE" as date ,
json_agg(json_build_object('a',1)) as isi
  FROM public."TRANS1" a
  LEFT OUTER JOIN public."TRANS2" b on a."TRNUM"=b."TRNUM"
  Group by 1,2 ORDER BY 1
)  t