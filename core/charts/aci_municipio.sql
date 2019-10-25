SELECT ROW_NUMBER() OVER(ORDER BY anio) AS id, periodo.anio,
    (
        (
        ( SELECT sum(core_ingresodetalle.ejecutado) AS sum
           FROM core_ingresodetalle
             JOIN core_ingreso ON core_ingresodetalle.ingreso_id = core_ingreso.id
             JOIN core_tipoingreso ON core_ingresodetalle.tipoingreso_id = core_tipoingreso.codigo
             JOIN lugar_municipio ON core_ingreso.municipio_id = lugar_municipio.id
             JOIN core_anio ON core_anio.anio = core_ingreso.anio
          WHERE core_ingreso.anio = periodo.anio AND core_ingreso.periodo = core_anio.periodo AND core_tipoingreso.clasificacion = 0 AND lugar_municipio.slug = '{municipio}')
        - 
        ( SELECT sum(core_gastodetalle.ejecutado) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN core_tipogasto ON core_gastodetalle.tipogasto_id = core_tipogasto.codigo
             JOIN lugar_municipio ON core_gasto.municipio_id = lugar_municipio.id
             JOIN core_anio ON core_anio.anio = core_gasto.anio
          WHERE core_gasto.anio = periodo.anio AND core_gasto.periodo = core_anio.periodo AND core_tipogasto.clasificacion = 0 AND lugar_municipio.slug = '{municipio}')
        )
        / 
        NULLIF( (SELECT sum(core_ingresodetalle.ejecutado) AS sum
           FROM core_ingresodetalle
             JOIN core_ingreso ON core_ingresodetalle.ingreso_id = core_ingreso.id
             JOIN core_tipoingreso ON core_ingresodetalle.tipoingreso_id = core_tipoingreso.codigo
             JOIN lugar_municipio ON core_ingreso.municipio_id = lugar_municipio.id
             JOIN core_anio ON core_anio.anio = core_ingreso.anio
          WHERE core_ingreso.anio = periodo.anio AND core_ingreso.periodo = core_anio.periodo AND core_tipoingreso.clasificacion = 0 AND lugar_municipio.slug = '{municipio}'), 0)
    ) * 100 AS ejecutado,
    (
        (
        ( SELECT sum(core_ingresodetalle.asignado) AS sum
           FROM core_ingresodetalle
             JOIN core_ingreso ON core_ingresodetalle.ingreso_id = core_ingreso.id
             JOIN core_tipoingreso ON core_ingresodetalle.tipoingreso_id = core_tipoingreso.codigo
             JOIN lugar_municipio ON core_ingreso.municipio_id = lugar_municipio.id
             JOIN core_anio ON core_anio.anio = core_ingreso.anio
          WHERE core_ingreso.anio = periodo.anio AND core_ingreso.periodo = 'I' AND core_tipoingreso.clasificacion = 0 AND lugar_municipio.slug = '{municipio}')
        - 
        ( SELECT sum(core_gastodetalle.asignado) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN core_tipogasto ON core_gastodetalle.tipogasto_id = core_tipogasto.codigo
             JOIN lugar_municipio ON core_gasto.municipio_id = lugar_municipio.id
             JOIN core_anio ON core_anio.anio = core_gasto.anio
          WHERE core_gasto.anio = periodo.anio AND core_gasto.periodo = 'I' AND core_tipogasto.clasificacion = 0 AND lugar_municipio.slug = '{municipio}')
        )
        / 
        NULLIF( (SELECT sum(core_ingresodetalle.asignado) AS sum
           FROM core_ingresodetalle
             JOIN core_ingreso ON core_ingresodetalle.ingreso_id = core_ingreso.id
             JOIN core_tipoingreso ON core_ingresodetalle.tipoingreso_id = core_tipoingreso.codigo
             JOIN lugar_municipio ON core_ingreso.municipio_id = lugar_municipio.id
             JOIN core_anio ON core_anio.anio = core_ingreso.anio
          WHERE core_ingreso.anio = periodo.anio AND core_ingreso.periodo = 'I' AND core_tipoingreso.clasificacion = 0 AND lugar_municipio.slug = '{municipio}'), 0)
    ) * 100 AS asignado
   FROM core_ingreso periodo WHERE anio = ANY( ARRAY[{year_list}] )
  GROUP BY periodo.anio
