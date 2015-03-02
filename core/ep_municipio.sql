SELECT ROW_NUMBER() OVER(ORDER BY fecha) AS id, periodo.fecha,
        (
        ( SELECT sum(core_gastodetalle.ejecutado) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN lugar_municipio ON core_gasto.municipio_id = lugar_municipio.id
          WHERE core_gasto.fecha = periodo.fecha AND lugar_municipio.slug = %s)
        / 
        ( SELECT sum(core_ingresodetalle.asignado) AS sum
           FROM core_ingresodetalle
             JOIN core_ingreso ON core_ingresodetalle.ingreso_id = core_ingreso.id
             JOIN lugar_municipio ON core_ingreso.municipio_id = lugar_municipio.id
          WHERE core_ingreso.fecha = periodo.fecha AND lugar_municipio.slug = %s)
        ) * 100 AS ejecutado
   FROM core_gasto periodo WHERE fecha = ANY( %s )
  GROUP BY periodo.fecha