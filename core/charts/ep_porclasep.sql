SELECT clasificacion, (
        ( SELECT SUM(core_{var}detalle.{quesumar1}) AS sum
           FROM core_{var}detalle
             JOIN core_{var} ON core_{var}detalle.{var}_id = core_{var}.id
             JOIN core_tipo{var} ON core_{var}detalle.tipo{var}_id = core_tipo{var}.codigo
             JOIN lugar_clasificacionmunicano ON core_{var}.municipio_id=lugar_clasificacionmunicano.municipio_id AND
         core_{var}.anio=lugar_clasificacionmunicano.anio                 
          WHERE core_{var}.anio = {year} AND core_{var}.periodo='{periodo_inicial}' AND lugar_clasificacionmunicano.clasificacion_id=clase.id)
        / 
        NULLIF( (SELECT SUM(core_{var}detalle.{quesumar2}) AS sum
           FROM core_{var}detalle
             JOIN core_{var} ON core_{var}detalle.{var}_id = core_{var}.id
             JOIN core_tipo{var} ON core_{var}detalle.tipo{var}_id = core_tipo{var}.codigo
             JOIN lugar_clasificacionmunicano ON core_{var}.municipio_id=lugar_clasificacionmunicano.municipio_id AND
         core_{var}.anio=lugar_clasificacionmunicano.anio                 
          WHERE core_{var}.anio = {year} AND core_{var}.periodo='{periodo_final}' AND lugar_clasificacionmunicano.clasificacion_id=clase.id)
          , 0)
    ) * 100 AS {var}  FROM lugar_clasificacionmunic AS clase ORDER BY clasificacion;
