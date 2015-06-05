SELECT ROW_NUMBER() OVER(ORDER BY year) AS id, periodo.year,
    (
        (
        ( SELECT sum(core_ingresodetalle.ejecutado) AS sum
           FROM core_ingresodetalle
             JOIN core_ingreso ON core_ingresodetalle.ingreso_id = core_ingreso.id
             JOIN core_tipoingreso ON core_ingresodetalle.tipoingreso_id::text = core_tipoingreso.codigo::text
             JOIN lugar_municipio ON core_ingreso.municipio_id = lugar_municipio.id
          WHERE core_ingreso.year = periodo.year AND core_tipoingreso.clasificacion = 0 AND lugar_municipio.slug = %s)
        - 
        ( SELECT sum(core_gastodetalle.ejecutado) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN core_tipogasto ON core_gastodetalle.tipogasto_id::text = core_tipogasto.codigo::text
             JOIN lugar_municipio ON core_gasto.municipio_id = lugar_municipio.id
          WHERE core_gasto.year = periodo.year AND core_tipogasto.clasificacion = 0 AND lugar_municipio.slug = %s)
        )
        / 
        NULLIF( (SELECT sum(core_ingresodetalle.ejecutado) AS sum
           FROM core_ingresodetalle
             JOIN core_ingreso ON core_ingresodetalle.ingreso_id = core_ingreso.id
             JOIN core_tipoingreso ON core_ingresodetalle.tipoingreso_id::text = core_tipoingreso.codigo::text
             JOIN lugar_municipio ON core_ingreso.municipio_id = lugar_municipio.id
          WHERE core_ingreso.year = periodo.year AND core_tipoingreso.clasificacion = 0 AND lugar_municipio.slug = %s), 0)
    ) * 100::numeric AS ejecutado,
    (
        (
        ( SELECT sum(core_ingresodetalle.asignado) AS sum
           FROM core_ingresodetalle
             JOIN core_ingreso ON core_ingresodetalle.ingreso_id = core_ingreso.id
             JOIN core_tipoingreso ON core_ingresodetalle.tipoingreso_id::text = core_tipoingreso.codigo::text
             JOIN lugar_municipio ON core_ingreso.municipio_id = lugar_municipio.id
          WHERE core_ingreso.year = periodo.year AND core_tipoingreso.clasificacion = 0 AND lugar_municipio.slug = %s)
        - 
        ( SELECT sum(core_gastodetalle.asignado) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN core_tipogasto ON core_gastodetalle.tipogasto_id::text = core_tipogasto.codigo::text
             JOIN lugar_municipio ON core_gasto.municipio_id = lugar_municipio.id
          WHERE core_gasto.year = periodo.year AND core_tipogasto.clasificacion = 0 AND lugar_municipio.slug = %s)
        )
        / 
        NULLIF( (SELECT sum(core_ingresodetalle.asignado) AS sum
           FROM core_ingresodetalle
             JOIN core_ingreso ON core_ingresodetalle.ingreso_id = core_ingreso.id
             JOIN core_tipoingreso ON core_ingresodetalle.tipoingreso_id::text = core_tipoingreso.codigo::text
             JOIN lugar_municipio ON core_ingreso.municipio_id = lugar_municipio.id
          WHERE core_ingreso.year = periodo.year AND core_tipoingreso.clasificacion = 0 AND lugar_municipio.slug = %s), 0)
    ) * 100::numeric AS asignado
   FROM core_ingreso periodo WHERE year = ANY( %s )
  GROUP BY periodo.year
