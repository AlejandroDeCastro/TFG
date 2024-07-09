-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 09-07-2024 a las 09:10:31
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `tfg`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `datos`
--

CREATE TABLE `datos` (
  `id` smallint(6) UNSIGNED NOT NULL,
  `ciudad` varchar(25) NOT NULL,
  `característica` varchar(100) NOT NULL,
  `enlace` varchar(10000) NOT NULL,
  `id_usuario` smallint(3) NOT NULL,
  `formato` varchar(8) NOT NULL,
  `periodicidad` int(250) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Volcado de datos para la tabla `datos`
--

INSERT INTO `datos` (`id`, `ciudad`, `característica`, `enlace`, `id_usuario`, `formato`, `periodicidad`) VALUES
(1, 'Valencia', 'Parkings', 'https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/parkings/records?limit=29', 1, 'JSON', 300),
(3, 'Madrid', 'Parkings', 'https://datos.madrid.es/egob/catalogo/202625-0-aparcamientos-publicos.json', 1, 'JSON', 60),
(4, 'Badajoz', 'Centros culturales', 'https://datosabiertos.dip-badajoz.es/dataset/e94c8e11-faff-4211-a999-3e16800e09ac/resource/7f697576-34e6-4104-96fb-d00656c76734/download/centrosculturales2023.json', 3, 'JSON', 60),
(7, 'Málaga', 'Desfibriladores', 'https://datosabiertos.malaga.eu/recursos/urbanismoEInfraestructura/equipamientos/da_desfibriladores-25830.geojson', 1, 'GEOJSON', 60),
(11, 'Lorca', 'Parkings', 'https://datos.lorca.es/catalogo/parkings/parkings.json', 1, 'JSON', 60),
(13, 'Gijón', 'Cajeros', 'https://opendata.gijon.es/descargar.php?id=748&tipo=JSON', 1, 'JSON', 60),
(14, 'Alicante', 'Vados', 'https://datosabiertos.alicante.es/sites/default/files/vados%202023.csv', 1, 'CSV', 0),
(15, 'Bilbao', 'Puntos de carga', 'https://www.bilbao.eus/aytoonline/srvDatasetParadas?tipo=electrolineras&formato=geojson', 1, 'JSON', 86400),
(16, 'San Sebastián', 'dbizi', 'https://www.donostia.eus/datosabiertos/recursos/bicicleta_dbizi/dbizi.json', 1, 'JSON', 60),
(17, 'Valencia', 'Puntos de carga', 'https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/carregadors-vehicles-electrics-cargadores-vehiculos-electricos/records', 1, 'JSON', 86400),
(18, 'Málaga', 'Centros comerciales', 'https://datosabiertos.malaga.eu/recursos/urbanismoEInfraestructura/equipamientos/da_centrosComerciales-4326.geojson', 1, 'GEOJSON', 60),
(23, 'Málaga', 'Parkings', 'https://datosabiertos.malaga.eu/recursos/aparcamientos/ubappublicosmun/da_aparcamientosPublicosMunicipales-25830.geojson', 3, 'GEOJSON', 0),
(24, 'Burgos', 'Parkings', 'Simulador', 1, 'NGSI', 0),
(25, 'Valencia', 'Expendedores ORA', 'https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/expendedors-ora-expendedores-ora/exports/json?lang=es&timezone=Europe%2FBerlin', 1, 'JSON', 86400),
(26, 'Gijón', 'Calidad aire', 'https://opendata.gijon.es/descargar.php?id=1&tipo=JSON', 1, 'JSON', 0),
(27, 'Gijón', 'Perros peligrosos', 'https://opendata.gijon.es/descargar.php?id=37&tipo=JSON', 1, 'JSON', 0),
(28, 'Barcelona', 'Puntos de carga', 'https://opendata-ajuntament.barcelona.cat/resources/auto/trimestral/2023_2T_Punts_Recarrega_Vehicle_Electric.json', 7, 'JSON', 0),
(32, 'Málaga', 'Comedores sociales', 'https://datosabiertos.malaga.eu/recursos/urbanismoEInfraestructura/equipamientos/higiali/da_higialim_comedores-25830.csv', 7, 'CSV', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `registros`
--

CREATE TABLE `registros` (
  `id` smallint(3) UNSIGNED NOT NULL,
  `id_usuario` smallint(3) NOT NULL,
  `Ciudad` varchar(25) NOT NULL,
  `Característica` varchar(100) NOT NULL,
  `Formato` varchar(8) NOT NULL,
  `Periodicidad` int(250) NOT NULL,
  `pid` int(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Volcado de datos para la tabla `registros`
--

INSERT INTO `registros` (`id`, `id_usuario`, `Ciudad`, `Característica`, `Formato`, `Periodicidad`, `pid`) VALUES
(71, 1, 'Valencia', 'Puntos de carga', 'JSON', 60, 13280),
(80, 1, 'Bilbao', 'Puntos de carga', 'JSON', 86400, 26200),
(83, 1, 'Gijón', 'Cajeros', 'JSON', 60, 9328);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `traducciones`
--

CREATE TABLE `traducciones` (
  `id` smallint(6) UNSIGNED NOT NULL,
  `original` varchar(100) NOT NULL,
  `traducción` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Volcado de datos para la tabla `traducciones`
--

INSERT INTO `traducciones` (`id`, `original`, `traducción`) VALUES
(1, 'Name', 'Nombre'),
(4, 'observacio', 'observaciones'),
(5, 'geo_point_2d', 'localizacion'),
(6, 'emplazamie', 'Dirección'),
(8, 'potenc_ia', 'potencia'),
(9, 'tipo_carga', 'tipo de carga'),
(10, 'availableSpotNumber', 'Plazas libres'),
(11, 'totalSpotNumber', 'Plazas totales');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` smallint(3) UNSIGNED NOT NULL,
  `usuario` varchar(20) NOT NULL,
  `contraseña` char(255) NOT NULL,
  `nombre_completo` varchar(50) NOT NULL,
  `favoritos` text NOT NULL,
  `rol` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `usuario`, `contraseña`, `nombre_completo`, `favoritos`, `rol`) VALUES
(1, 'JUAN', 'scrypt:32768:8:1$tzddfppapymlneuy$082fd4e9c1104c61b671cde8d27d1f450733359e26a24fe7eb4e50b4eba01abb55fc1abe7869485a06d54a08e9f8e7472c9abe5d3226471e93e4a2dfbf631d50', 'Juan Pérez', 'Valencia - Puntos de carga, Gijón - Perros peligrosos, Gijón - Cajeros', 'usuario'),
(7, 'Alejandro', 'scrypt:32768:8:1$bHalGcEbXmu9zlC5$0136f1ff846dc31538c3fbcc79dc9896e3afbda616891c35cb0e7fd2270d33199ec714573f5428943cd75318cbbba820c7cadda677f43941c76f96056fd242a1', 'Alejandro de Castro', 'Valencia - Puntos de carga', 'administrador');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `datos`
--
ALTER TABLE `datos`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `registros`
--
ALTER TABLE `registros`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `traducciones`
--
ALTER TABLE `traducciones`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `datos`
--
ALTER TABLE `datos`
  MODIFY `id` smallint(6) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT de la tabla `registros`
--
ALTER TABLE `registros`
  MODIFY `id` smallint(3) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=85;

--
-- AUTO_INCREMENT de la tabla `traducciones`
--
ALTER TABLE `traducciones`
  MODIFY `id` smallint(6) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` smallint(3) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
