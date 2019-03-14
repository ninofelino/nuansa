CREATE OR REPLACE FUNCTION public.felino_mcla()
  RETURNS json AS
$BODY$SELECT json_agg(json_build_object('text',name)) FROM product_category
where parent_id=3
$BODY$
  LANGUAGE sql VOLATILE
  COST 100;
ALTER FUNCTION public.felino_mcla()
  OWNER TO postgres;