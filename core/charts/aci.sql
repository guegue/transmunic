SELECT ROW_NUMBER() OVER(ORDER BY anio) AS id, periodo.anio,
    (
        (
        ( SELECT sum(core_ingresodetalle.ejecutado) AS sum
           FROM core_ingresodetalle
             JOIN core_ingreso ON core_ingresodetalle.ingreso_id = core_ingreso.id
             JOIN core_tipoingreso ON core_ingresodetalle.tipoingreso_id::text = core_tipoingreso.codigo::text
          WHERE core_ingreso.anio = periodo.anio AND core_tipoingreso.clasificacion = 0)
        - 
        ( SELECT sum(core_gastodetalle.ejecutado) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN core_tipogasto ON core_gastodetalle.tipogasto_id::text = core_tipogasto.codigo::text
          WHERE core_gasto.anio = periodo.anio AND core_tipogasto.clasificacion = 0)
        )
        / 
        ( SELECT sum(core_ingresodetalle.ejecutado) AS sum
           FROM core_ingresodetalle
             JOIN core_ingreso ON core_ingresodetalle.ingreso_id = core_ingreso.id
             JOIN core_tipoingreso ON core_ingresodetalle.tipoingreso_id::text = core_tipoingreso.codigo::text
          WHERE core_ingreso.anio = periodo.anio AND core_tipoingreso.clasificacion = 0)
    ) * 100::numeric AS ejecutado,
    (
        (
        ( SELECT sum(core_ingresodetalle.asignado) AS sum
           FROM core_ingresodetalle
             JOIN core_ingreso ON core_ingresodetalle.ingreso_id = core_ingreso.id
             JOIN core_tipoingreso ON core_ingresodetalle.tipoingreso_id::text = core_tipoingreso.codigo::text
          WHERE core_ingreso.anio = periodo.anio AND core_tipoingreso.clasificacion = 0)
        - 
        ( SELECT sum(core_gastodetalle.asignado) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN core_tipogasto ON core_gastodetalle.tipogasto_id::text = core_tipogasto.codigo::text
          WHERE core_gasto.anio = periodo.anio AND core_tipogasto.clasificacion = 0)
        )
        / 
        ( SELECT sum(core_ingresodetalle.asignado) AS sum
           FROM core_ingresodetalle
             JOIN core_ingreso ON core_ingresodetalle.ingreso_id = core_ingreso.id
             JOIN core_tipoingreso ON core_ingresodetalle.tipoingreso_id::text = core_tipoingreso.codigo::text
          WHERE core_ingreso.anio = periodo.anio AND core_tipoingreso.clasificacion = 0)
    ) * 100::numeric AS asignado
   FROM core_ingreso periodo WHERE anio = ANY( %s )
  GROUP BY periodo.anio
