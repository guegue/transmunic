select round(Sum(asignado)/1000000, 2) as asignado, round( sum(ejecutado)/1000000, 2) as ejecutado, core_origenrecurso.nombre from
core_ingresodetalle, core_ingreso, core_subsubtipoingreso, core_origenrecurso
where core_ingresodetalle.ingreso_id = core_ingreso.id
and core_ingresodetalle.subsubtipoingreso_id= core_subsubtipoingreso.codigo
and core_subsubtipoingreso.origen_id = core_origenrecurso.id
and core_ingreso.periodo = 'A'
and core_ingreso.anio = 2015
and core_ingreso.municipio_id = 55
group by core_origenrecurso.nombre;

-- level 0 Totals
-- municipio Achuapa ID=55
select sum(sd.asignado)/1000000 as asignado, sum(sd.ejecutado)/1000000 as ejecutado
from (
select 
id.asignado, id.ejecutado, id.ingreso_id, id.subsubtipoingreso_id,
i.municipio_id, i.periodo, i.anio, ssti.subtipoingreso_id, ssti.origen_id
from core_ingresodetalle as id left join core_ingreso as i on id.ingreso_id = i.id
left join core_subsubtipoingreso as ssti on id.subsubtipoingreso_id=ssti.codigo
where i.anio = 2015
and i.periodo = 'A'
and i.municipio_id = 55
and origen_id is not null
) as sd
left join core_origenrecurso as o on sd.origen_id=o.id;

-- level 1 Sum per OrigenRecurso
select sum(sd.asignado)/1000000 as asignado, sum(sd.ejecutado)/1000000 as ejecutado, o.nombre, o.id 
from (select id.asignado, id.ejecutado, id.ingreso_id,
id.subsubtipoingreso_id, i.municipio_id, i.periodo, i.anio, ssti.subtipoingreso_id, ssti.origen_id
from core_ingresodetalle as id left join core_ingreso as i on id.ingreso_id = i.id
left join core_subsubtipoingreso as ssti on id.subsubtipoingreso_id=ssti.codigo
where i.anio = 2015
and i.periodo = 'F'
and i.municipio_id = 117
and origen_id is not null) as sd
left join core_origenrecurso as o on sd.origen_id=o.id
group by nombre, id;

-- level 2  Sum by OrigenIngreso

select sum(sd.asignado) as asignado, sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo
from (select id.asignado, id.ejecutado, id.ingreso_id, id.subsubtipoingreso_id,
i.municipio_id, i.periodo, i.anio, ssti.subtipoingreso_id as codigo, ssti.origen_id, sti.nombre
from core_ingresodetalle as id left join core_ingreso as i on id.ingreso_id = i.id
left join core_subsubtipoingreso as ssti on id.subsubtipoingreso_id=ssti.codigo
left join core_subtipoingreso as sti on sti.codigo= ssti.subtipoingreso_id
where i.anio = 2015
and i.municipio_id = 117
and ssti.origen_id = '') as sd
group by sd.nombre, sd.codigo

-- level 3 sum
select sum(sd.asignado) as asignado, sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo
from (select id.asignado, id.ejecutado, id.ingreso_id, id.subsubtipoingreso_id,
i.municipio_id, i.periodo, i.anio, ssti.subtipoingreso_id as codigo, ssti.nombre
from core_ingresodetalle as id left join core_ingreso as i on id.ingreso_id = i.id
left join core_subsubtipoingreso as ssti on id.subsubtipoingreso_id=ssti.codigo
where i.anio = %s
and i.municipio_id = %s
and ssti.subtipoingreso_id = %s) as sd
group by sd.nombre, sd.codigo


select sum(sd.asignado) as asignado, sum(sd.ejecutado) as ejecutado, sd.nombre, sd.codigo
from (select id.asignado, id.ejecutado, id.gasto_id, id.subsubtipogasto_id,
i.municipio_id, i.periodo, i.anio, ssti.subtipogasto_id as codigo, ssti.origen_id,
sti.nombre
from core_gastodetalle as id left join core_gasto as i on id.gasto_id = i.id
left join core_subsubtipogasto as ssti on id.subsubtipogasto_id=ssti.codigo
left join core_subtipogasto as sti on sti.codigo= to_char(ssti.subtipogasto_id,'9999999')
where i.anio = 2015
and i.periodo = 'A'
and i.municipio_id = 55
and ssti.origen_id = '3') as sd
group by sd.nombre, sd.codigo

select id.asignado, id.ejecutado, id.gasto_id, id.subsubtipogasto_id, i.municipio_id, i.periodo, i.anio, ssti.subtipogasto_id as codigo, ssti.origen_id
from core_gastodetalle as id left join core_gasto as i on id.gasto_id = i.id
left join core_subsubtipogasto as ssti on id.subsubtipogasto_id=ssti.codigo
left join core_subtipogasto as sti on sti.codigo= to_char(ssti.subtipogasto_id,'9999999')
where i.anio = 2015
and i.periodo = 'A'
and i.municipio_id = 55
and ssti.origen_id = '3'