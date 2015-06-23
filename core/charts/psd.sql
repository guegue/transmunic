SELECT ROW_NUMBER() OVER(ORDER BY anio) AS id, periodo.anio,
        (
        ( SELECT sum(core_gastodetalle.ejecutado) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN core_tipogasto ON core_gastodetalle.tipogasto_id = core_tipogasto.codigo
          WHERE core_gasto.anio = periodo.anio AND core_gastodetalle.tipogasto_id = '8000000')
        / 
        ( SELECT sum(core_gastodetalle.ejecutado) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN core_tipogasto ON core_gastodetalle.tipogasto_id = core_tipogasto.codigo
          WHERE core_gasto.anio = periodo.anio)
        ) * 100 AS ejecutado,
        (
        ( SELECT sum(core_gastodetalle.asignado) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN core_tipogasto ON core_gastodetalle.tipogasto_id = core_tipogasto.codigo
          WHERE core_gasto.anio = periodo.anio AND core_gastodetalle.tipogasto_id = '8000000')
        / 
        ( SELECT sum(core_gastodetalle.asignado) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN core_tipogasto ON core_gastodetalle.tipogasto_id = core_tipogasto.codigo
          WHERE core_gasto.anio = periodo.anio)
        ) * 100 AS asignado
   FROM core_gasto periodo WHERE anio = ANY( %s )
  GROUP BY periodo.anio
