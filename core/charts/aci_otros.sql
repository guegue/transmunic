SELECT muni.nombre, (
        (
        ( SELECT SUM(core_ingresodetalle.{quesumar}) AS sum
           FROM core_ingresodetalle
             JOIN core_ingreso ON core_ingresodetalle.ingreso_id = core_ingreso.id
             JOIN core_tipoingreso ON core_ingresodetalle.tipoingreso_id = core_tipoingreso.codigo
          WHERE core_ingreso.anio = {year} AND core_Ingreso.periodo='{periodo}' AND core_tipoingreso.clasificacion = {tipoingreso} AND core_Ingreso.municipio_id=muni.id)
        - 
        ( SELECT SUM(core_gastodetalle.{quesumar}) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN core_tipogasto ON core_gastodetalle.tipogasto_id = core_tipogasto.codigo
          WHERE core_gasto.anio = {year} AND core_Gasto.periodo='{periodo}' AND core_tipogasto.clasificacion = {tipoingreso} AND core_Gasto.municipio_id=muni.id)
        )
        / 
        NULLIF( (SELECT SUM(core_ingresodetalle.{quesumar}) AS sum
           FROM core_ingresodetalle
             JOIN core_ingreso ON core_ingresodetalle.ingreso_id = core_ingreso.id
             JOIN core_tipoingreso ON core_ingresodetalle.tipoingreso_id = core_tipoingreso.codigo
          WHERE core_ingreso.anio = {year} AND core_Ingreso.periodo='{periodo}' AND core_tipoingreso.clasificacion = {tipoingreso} AND core_Ingreso.municipio_id=muni.id), 0)
    ) * 100 AS {quesumar}  FROM lugar_municipio AS muni 
             JOIN lugar_clasificacionmunicano ON muni.id=lugar_clasificacionmunicano.municipio_id AND
         lugar_clasificacionmunicano.anio = {year}
WHERE lugar_clasificacionmunicano.clasificacion_id={mi_clase}
ORDER BY muni.nombre;
