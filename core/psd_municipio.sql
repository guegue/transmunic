SELECT ROW_NUMBER() OVER(ORDER BY year) AS id, periodo.year,
        (
        ( SELECT sum(core_gastodetalle.ejecutado) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN core_tipogasto ON core_gastodetalle.tipogasto_id = core_tipogasto.codigo
             JOIN lugar_municipio ON core_gasto.municipio_id = lugar_municipio.id
          WHERE core_gasto.year = periodo.year AND core_gastodetalle.tipogasto_id = '8000000' AND lugar_municipio.slug = %s)
        / 
        ( SELECT sum(core_gastodetalle.ejecutado) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN core_tipogasto ON core_gastodetalle.tipogasto_id = core_tipogasto.codigo
             JOIN lugar_municipio ON core_gasto.municipio_id = lugar_municipio.id
          WHERE core_gasto.year = periodo.year AND lugar_municipio.slug = %s)
        ) * 100 AS ejecutado,
        (
        ( SELECT sum(core_gastodetalle.asignado) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN core_tipogasto ON core_gastodetalle.tipogasto_id = core_tipogasto.codigo
             JOIN lugar_municipio ON core_gasto.municipio_id = lugar_municipio.id
          WHERE core_gasto.year = periodo.year AND core_gastodetalle.tipogasto_id = '8000000' AND lugar_municipio.slug = %s)
        / 
        ( SELECT sum(core_gastodetalle.asignado) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN core_tipogasto ON core_gastodetalle.tipogasto_id = core_tipogasto.codigo
             JOIN lugar_municipio ON core_gasto.municipio_id = lugar_municipio.id
          WHERE core_gasto.year = periodo.year AND lugar_municipio.slug = %s)
        ) * 100 AS asignado
   FROM core_gasto periodo WHERE year = ANY( %s )
  GROUP BY periodo.year
