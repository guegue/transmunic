SELECT lugar_municipio.nombre, lugar_municipio.slug, (
        ( SELECT SUM(core_{var}detalle.{quesumar1}) AS sum
           FROM core_{var}detalle
             JOIN core_{var} ON core_{var}detalle.{var}_id = core_{var}.id
             JOIN core_tipo{var} ON core_{var}detalle.tipo{var}_id = core_tipo{var}.codigo
          WHERE core_{var}.anio = {year} AND core_{var}.periodo='{periodo_inicial}' AND core_{var}.municipio_id=lugar_municipio.id)
        / 
        NULLIF( (SELECT SUM(core_{var}detalle.{quesumar2}) AS sum
           FROM core_{var}detalle
             JOIN core_{var} ON core_{var}detalle.{var}_id = core_{var}.id
             JOIN core_tipo{var} ON core_{var}detalle.tipo{var}_id = core_tipo{var}.codigo
          WHERE core_{var}.anio = {year} AND core_{var}.periodo='{periodo_final}' AND core_{var}.municipio_id=lugar_municipio.id)
          , 0)
    ) * 100 AS {var}  FROM lugar_municipio JOIN lugar_clasificacionmunicano ON 
    lugar_municipio.id=lugar_clasificacionmunicano.municipio_id AND lugar_clasificacionmunicano.anio={year}
    WHERE lugar_clasificacionmunicano.clasificacion_id={mi_clase} ORDER BY lugar_municipio.nombre;
