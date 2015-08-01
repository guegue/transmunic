SELECT clasificacion, (
        ( SELECT SUM(core_ingresodetalle.{quesumar}) AS sum
           FROM core_ingresodetalle
             JOIN core_ingreso ON core_ingresodetalle.ingreso_id = core_ingreso.id
             JOIN core_tipoingreso ON core_ingresodetalle.tipoingreso_id = core_tipoingreso.codigo
             JOIN lugar_clasificacionmunicano ON core_Ingreso.municipio_id=lugar_clasificacionmunicano.municipio_id AND
         core_Ingreso.anio=lugar_clasificacionmunicano.anio                 
          WHERE core_ingreso.anio = {year} AND core_Ingreso.periodo='{periodo}' AND core_tipoingreso.clasificacion = {tipoingreso} AND core_tipoingreso.codigo <> '{notipoingreso}' AND lugar_clasificacionmunicano.clasificacion_id=clase.id)
        / 
        NULLIF( (SELECT SUM(core_gastodetalle.{quesumar}) AS sum
           FROM core_gastodetalle
             JOIN core_gasto ON core_gastodetalle.gasto_id = core_gasto.id
             JOIN core_tipogasto ON core_gastodetalle.tipogasto_id = core_tipogasto.codigo
             JOIN lugar_clasificacionmunicano ON core_Gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND
         core_Gasto.anio=lugar_clasificacionmunicano.anio                 
          WHERE core_gasto.anio = {year} AND core_Gasto.periodo='{periodo}' AND core_tipogasto.clasificacion = {tipoingreso} AND lugar_clasificacionmunicano.clasificacion_id=clase.id)
          , 0)
    -1 ) * 100 AS {quesumar}  FROM lugar_clasificacionmunic AS clase ORDER BY clasificacion;
