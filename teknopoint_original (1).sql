-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 08-05-2024 a las 18:38:17
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
-- Base de datos: `teknopoint_original`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activity`
--

CREATE TABLE `activity` (
  `activity_id` int(11) NOT NULL,
  `activity` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `activity`
--

INSERT INTO `activity` (`activity_id`, `activity`) VALUES
(1, 'asset'),
(2, 'idle');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `articles`
--

CREATE TABLE `articles` (
  `id` int(11) NOT NULL,
  `art_nombre` varchar(255) NOT NULL,
  `art_precio` decimal(65,2) NOT NULL,
  `art_itbis` decimal(65,2) NOT NULL,
  `art_cantidad` bigint(20) NOT NULL,
  `catalogue` varchar(255) NOT NULL,
  `image` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `art_bill`
--

CREATE TABLE `art_bill` (
  `id` int(11) NOT NULL,
  `id_bills` int(11) NOT NULL,
  `decrition` varchar(255) NOT NULL,
  `price` decimal(65,2) NOT NULL,
  `itbis` decimal(65,2) NOT NULL,
  `amount` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `art_bill`
--

INSERT INTO `art_bill` (`id`, `id_bills`, `decrition`, `price`, `itbis`, `amount`) VALUES
(149, 1, 'PC Gamer HD full 4k rgb', 200.00, 18.00, 5),
(150, 1, 'PC Gamer HD', 23.00, 18.00, 5),
(151, 1, 'Nvidia RTX 4090', 500.00, 18.00, 5),
(152, 1, 'G. SKILL DDR4 SDRAM 8 GB ', 100.00, 12.00, 5),
(153, 1, 'Laptop DELL', 2000.00, 18.00, 5),
(154, 2, 'PC Gamer HD full 4k rgb', 200.00, 18.00, 5),
(155, 2, 'PC Gamer HD', 23.00, 18.00, 5),
(156, 2, 'Nvidia RTX 4090', 500.00, 18.00, 5),
(157, 2, 'G. SKILL DDR4 SDRAM 8 GB ', 100.00, 12.00, 5),
(158, 2, 'Laptop DELL', 2000.00, 18.00, 5),
(159, 3, 'PC Gamer HD full 4k rgb', 200.00, 18.00, 5),
(160, 3, 'PC Gamer HD', 23.00, 18.00, 5),
(161, 3, 'Nvidia RTX 4090', 500.00, 18.00, 5),
(162, 3, 'G. SKILL DDR4 SDRAM 8 GB ', 100.00, 12.00, 5),
(163, 3, 'Laptop DELL', 2000.00, 18.00, 5),
(164, 4, 'PC Gamer HD full 4k rgb', 200.00, 18.00, 5),
(165, 4, 'Nvidia RTX 4090', 500.00, 18.00, 1),
(166, 5, 'PC Gamer HD full 4k rgb', 200.00, 18.00, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `bills`
--

CREATE TABLE `bills` (
  `id` int(11) NOT NULL,
  `date` datetime NOT NULL,
  `number_bill` varchar(50) NOT NULL,
  `customer` varchar(255) NOT NULL,
  `discount` decimal(65,2) NOT NULL,
  `way_to_pay` varchar(255) NOT NULL,
  `paid` decimal(65,2) NOT NULL,
  `change` decimal(65,2) NOT NULL,
  `cashier` varchar(255) NOT NULL,
  `rnc_client_bill` int(11) NOT NULL,
  `ubicacion` varchar(255) NOT NULL,
  `contacto` varchar(255) NOT NULL,
  `total_general` decimal(65,2) NOT NULL,
  `estado` int(11) NOT NULL,
  `Itbisextra` decimal(65,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `bills`
--

INSERT INTO `bills` (`id`, `date`, `number_bill`, `customer`, `discount`, `way_to_pay`, `paid`, `change`, `cashier`, `rnc_client_bill`, `ubicacion`, `contacto`, `total_general`, `estado`, `Itbisextra`) VALUES
(1, '2024-04-28 00:34:50', '00001', 'David Almonte', 20.00, 'Efectivo', 90000.00, 73374.30, 'David Mena', 123124, 'Villa Maria C.4', 'davidbatista.db45@gmail.com', 9840.00, 1, 5.00),
(2, '2024-04-28 13:09:25', '00002', 'David Almonte', 90.00, 'Efectivo', 90000.00, 73374.30, 'David Mena', 123124, 'Villa Maria C.4', 'davidbatista.db45@gmail.com', 16625.70, 1, 10.00),
(3, '2024-04-28 13:10:03', '00003', 'David Almonte', 90.00, 'Efectivo', 90000.00, 73374.30, 'David Mena', 123124, 'Villa Maria C.4', 'davidbatista.db45@gmail.com', 2018.45, 1, 10.00),
(4, '2024-04-30 09:41:08', '00004', 'David Almonte', 0.00, 'Efectivo', 9000.00, 7230.00, 'David Mena', 123124, 'Villa Maria C.4', 'davidbatista.db45@gmail.com', 1770.00, 1, 0.00),
(5, '2024-05-02 07:53:04', '00005', 'David Almonte', 0.00, 'Efectivo', 9000.00, 8764.00, 'David Mena', 123124, 'Villa Maria C.4', 'davidbatista.db45@gmail.com', 236.00, 1, 0.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clients`
--

CREATE TABLE `clients` (
  `client_id` int(11) NOT NULL,
  `client_name` varchar(50) NOT NULL,
  `client_address` varchar(50) NOT NULL,
  `client_phone` varchar(50) NOT NULL,
  `client_email` varchar(255) NOT NULL,
  `activity_id` int(11) NOT NULL,
  `rnc_client` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `clients`
--

INSERT INTO `clients` (`client_id`, `client_name`, `client_address`, `client_phone`, `client_email`, `activity_id`, `rnc_client`) VALUES
(1, 'Jhoneymi David Batista Mena', 'Villa Maria C.4', '849-282-5457', 'slimerbatista27@gmail.com', 2, 343255),
(2, 'Geison Enmanuel Peña Trinidad', 'Villa Mella C.29', '2145463658', 'geisonpeña@gmail.com', 1, 234233),
(3, 'Eury Samuel Caraballo Tapia', 'Villa altagracia C.5', '234567890076', 'eurysamuelcaraballotapia@gmail.com', 1, 124235),
(4, 'David Almonte', 'Villa Maria C.4', '435672343', 'davidbatista.db45@gmail.com', 1, 123124);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `closing_box`
--

CREATE TABLE `closing_box` (
  `id_closing` int(11) NOT NULL,
  `fechahora` datetime NOT NULL,
  `saldoinicial` decimal(10,2) NOT NULL,
  `totalingresos` decimal(10,2) NOT NULL,
  `totalegresos` decimal(10,2) NOT NULL,
  `totalventasefectivo` decimal(10,2) NOT NULL,
  `totalventastarjeta` decimal(10,2) NOT NULL,
  `totaldevoluciones` decimal(10,2) NOT NULL,
  `arqueocaja` decimal(10,2) NOT NULL,
  `observaciones` text NOT NULL,
  `cajero` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estado_bills`
--

CREATE TABLE `estado_bills` (
  `id` int(11) NOT NULL,
  `estado` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `estado_bills`
--

INSERT INTO `estado_bills` (`id`, `estado`) VALUES
(1, 'abierto'),
(2, 'cerrado');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `products`
--

CREATE TABLE `products` (
  `product_id` int(11) NOT NULL,
  `product_name` varchar(50) NOT NULL,
  `product_price` decimal(65,2) NOT NULL,
  `product_itbis` decimal(65,2) NOT NULL,
  `product_amount` bigint(20) NOT NULL,
  `amount` bigint(11) NOT NULL,
  `product_catalogue` varchar(100) NOT NULL,
  `image` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `products`
--

INSERT INTO `products` (`product_id`, `product_name`, `product_price`, `product_itbis`, `product_amount`, `amount`, `product_catalogue`, `image`) VALUES
(3, 'PC Gamer HD full 4k rgb', 200.00, 18.00, 5, 5, 'laptop', 'desktop.jpeg'),
(11, 'PC Gamer HD', 23.00, 18.00, 10, 10, 'laptop', 'laptop.jpeg'),
(12, 'Nvidia RTX 4090', 500.00, 18.00, 29, 29, 'gpu', 'Nvidia RTX 4090.jpeg'),
(13, 'G. SKILL DDR4 SDRAM 8 GB ', 100.00, 12.00, 10, 10, 'ram', 'G. SKILL DDR4 SDRAM 8 GB.jpeg'),
(14, 'Laptop DELL', 2000.00, 18.00, 10, 10, 'laptop', 'laptop.jpeg');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE `roles` (
  `role_id` int(1) NOT NULL,
  `name` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `roles`
--

INSERT INTO `roles` (`role_id`, `name`) VALUES
(0, 'Prueba'),
(1, 'Owner'),
(2, 'User'),
(3, 'Employee');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sales`
--

CREATE TABLE `sales` (
  `sale_id` int(11) NOT NULL,
  `user_name` varchar(50) NOT NULL,
  `client_name` varchar(50) NOT NULL,
  `sale_date` datetime NOT NULL,
  `total_sale` decimal(10,0) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sales_details`
--

CREATE TABLE `sales_details` (
  `sale_detail_id` int(11) NOT NULL,
  `sale_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `amount` bigint(20) NOT NULL,
  `unit_price` decimal(65,30) NOT NULL,
  `subtotal` decimal(65,30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `suppliers`
--

CREATE TABLE `suppliers` (
  `supplier_id` int(11) NOT NULL,
  `supplier_name` varchar(50) NOT NULL,
  `supplier_address` varchar(50) NOT NULL,
  `supplier_phone` varchar(50) NOT NULL,
  `supplier_email` varchar(50) NOT NULL,
  `activity_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `suppliers`
--

INSERT INTO `suppliers` (`supplier_id`, `supplier_name`, `supplier_address`, `supplier_phone`, `supplier_email`, `activity_id`) VALUES
(1, 'Jose Roberto Martinez', 'Villa maria C#4', '8492825457', 'slimerbatista27@gmail.com', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `time`
--

CREATE TABLE `time` (
  `id` int(11) NOT NULL,
  `id_users` int(11) NOT NULL,
  `entry_date` datetime NOT NULL,
  `departure_date` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `time`
--

INSERT INTO `time` (`id`, `id_users`, `entry_date`, `departure_date`) VALUES
(1, 1, '2024-04-30 09:45:00', '2024-04-25 17:38:32'),
(2, 2, '2024-05-08 12:32:59', '2024-05-08 12:33:52'),
(7, 7, '2024-03-26 16:54:36', '2024-03-27 12:29:35'),
(12, 12, '2024-04-08 23:13:49', '2024-04-08 22:49:05'),
(13, 13, '2024-04-17 10:39:26', '0000-00-00 00:00:00'),
(14, 14, '2024-05-01 10:57:35', '0000-00-00 00:00:00');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `time_online`
--

CREATE TABLE `time_online` (
  `id` int(11) NOT NULL,
  `id_user` int(11) NOT NULL,
  `time` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `fullname` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role_id` int(1) NOT NULL,
  `state` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `users`
--

INSERT INTO `users` (`user_id`, `fullname`, `email`, `username`, `password`, `role_id`, `state`) VALUES
(1, 'Jhoneymi D. Batista Mena', 'slimerbatista27@gmail.com', 'Owner', '$2b$12$JMVOr.NuYu4pmBTB0icU8.J9p..ZWNCOonxSANuXE5gHrXOzFDnDO', 1, 1),
(2, 'David Mena', 'slimerbatista29@gmail.com', 'Jeff', '$2b$12$B4NzCTbSzB/vusMU5aRRS.DjTwUIBhQioHKKTAJ4BiMY10yo0Lwdu', 2, 2),
(3, 'Eury S. Caraballo Tapia', 'eurysamuelct@hotmail.com', 'Eury', '$2b$12$c5.Zuga02QA4LozftSfSxOZqAewgzDB//Bay9OyVZ/JfUUYel3DuS', 2, 2),
(4, 'Angel Alexander Perez Martinez', 'angelalexanderperezmartinez47@gmail.com', 'Angel', '$2b$12$7vjIsfzOjVCkx9aZsyz5EOwCxBVm3dL8wmggSgiuWXA49dTzM/qnO', 2, 2),
(5, 'Geyson E. Peña Trinidad', 'slimerbatista27@gmail.com', 'Jeff-2', '$2b$12$1R3nU45ZdcU7RrKvjVkVl.p8iUnfyvbMhkxp8w58cNv7fZpTEB4.i', 2, 2),
(7, 'Eury S. Caraballo Tapia', 'EuryS@gmail.com', 'Empleado-02', '$2b$12$GaXf.sEcLNCMcNCrEjybbe8bNhV3JJ5s8v9E7VvNAsBjVhqMB.cFC', 3, 2),
(10, 'Natanael Mathurin', 'nm813913@gmail.com', '1nonly', '$2b$12$WrV3DOclCK.c8l6gSQEGG.6VVYP2CjcGzcIDtAzQyR01IFO2AfQKG', 2, 2),
(11, 'alexander liranzo', 'alex@gmail.com', 'alexander', '$2b$12$ROPCMxtHJ9z./SumcwWpAu8sS5qBhLETCtDEL00OEiSOfSWLwS6lu', 2, 2),
(12, 'Jhoneymi D. Batista Mena', 'slimerbatista28@gmail.com', 'Empleado', '$2b$12$J7LvuOQZoPGb3ToQnRJNQOLXA6PULpZEgHUDN8.41xVEXLswWIpfu', 3, 1),
(13, 'rosa', 'rosa@gmail.com', 'rosa', '$2b$12$3JoFIAIo692SqDg6TItCJOwX.nabxOwC9KZadOX4BtduvHnBK./9i', 2, 1),
(14, 'alexander liranzo', 'alex@gmail.com', 'alex', '$2b$12$u9OWKzV7MF8q.wxC2DIfTe5k1oYEkjhyK.GMjvfgSnPVEj5zmtvNm', 2, 1);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `activity`
--
ALTER TABLE `activity`
  ADD PRIMARY KEY (`activity_id`);

--
-- Indices de la tabla `articles`
--
ALTER TABLE `articles`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `art_bill`
--
ALTER TABLE `art_bill`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_bills` (`id_bills`);

--
-- Indices de la tabla `bills`
--
ALTER TABLE `bills`
  ADD PRIMARY KEY (`id`),
  ADD KEY `estado` (`estado`);

--
-- Indices de la tabla `clients`
--
ALTER TABLE `clients`
  ADD PRIMARY KEY (`client_id`),
  ADD KEY `activity_id` (`activity_id`);

--
-- Indices de la tabla `closing_box`
--
ALTER TABLE `closing_box`
  ADD PRIMARY KEY (`id_closing`);

--
-- Indices de la tabla `estado_bills`
--
ALTER TABLE `estado_bills`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`product_id`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`role_id`);

--
-- Indices de la tabla `sales`
--
ALTER TABLE `sales`
  ADD PRIMARY KEY (`sale_id`);

--
-- Indices de la tabla `sales_details`
--
ALTER TABLE `sales_details`
  ADD PRIMARY KEY (`sale_detail_id`),
  ADD KEY `sale_id` (`sale_id`,`product_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indices de la tabla `suppliers`
--
ALTER TABLE `suppliers`
  ADD PRIMARY KEY (`supplier_id`),
  ADD KEY `activity_id` (`activity_id`);

--
-- Indices de la tabla `time`
--
ALTER TABLE `time`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_users` (`id_users`);

--
-- Indices de la tabla `time_online`
--
ALTER TABLE `time_online`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_time` (`id_user`);

--
-- Indices de la tabla `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD KEY `role_id` (`role_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `activity`
--
ALTER TABLE `activity`
  MODIFY `activity_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `articles`
--
ALTER TABLE `articles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=38;

--
-- AUTO_INCREMENT de la tabla `art_bill`
--
ALTER TABLE `art_bill`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=167;

--
-- AUTO_INCREMENT de la tabla `bills`
--
ALTER TABLE `bills`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT de la tabla `clients`
--
ALTER TABLE `clients`
  MODIFY `client_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `closing_box`
--
ALTER TABLE `closing_box`
  MODIFY `id_closing` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `estado_bills`
--
ALTER TABLE `estado_bills`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `products`
--
ALTER TABLE `products`
  MODIFY `product_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT de la tabla `roles`
--
ALTER TABLE `roles`
  MODIFY `role_id` int(1) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `sales`
--
ALTER TABLE `sales`
  MODIFY `sale_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `sales_details`
--
ALTER TABLE `sales_details`
  MODIFY `sale_detail_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `suppliers`
--
ALTER TABLE `suppliers`
  MODIFY `supplier_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `time`
--
ALTER TABLE `time`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT de la tabla `time_online`
--
ALTER TABLE `time_online`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `art_bill`
--
ALTER TABLE `art_bill`
  ADD CONSTRAINT `art_bill_ibfk_1` FOREIGN KEY (`id_bills`) REFERENCES `bills` (`id`);

--
-- Filtros para la tabla `bills`
--
ALTER TABLE `bills`
  ADD CONSTRAINT `bills_ibfk_1` FOREIGN KEY (`estado`) REFERENCES `estado_bills` (`id`);

--
-- Filtros para la tabla `clients`
--
ALTER TABLE `clients`
  ADD CONSTRAINT `clients_ibfk_1` FOREIGN KEY (`activity_id`) REFERENCES `activity` (`activity_id`);

--
-- Filtros para la tabla `sales_details`
--
ALTER TABLE `sales_details`
  ADD CONSTRAINT `sales_details_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
  ADD CONSTRAINT `sales_details_ibfk_2` FOREIGN KEY (`sale_id`) REFERENCES `clients` (`client_id`);

--
-- Filtros para la tabla `suppliers`
--
ALTER TABLE `suppliers`
  ADD CONSTRAINT `suppliers_ibfk_1` FOREIGN KEY (`activity_id`) REFERENCES `activity` (`activity_id`);

--
-- Filtros para la tabla `time`
--
ALTER TABLE `time`
  ADD CONSTRAINT `time_ibfk_1` FOREIGN KEY (`id_users`) REFERENCES `users` (`user_id`);

--
-- Filtros para la tabla `time_online`
--
ALTER TABLE `time_online`
  ADD CONSTRAINT `time_online_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `users` (`user_id`);

--
-- Filtros para la tabla `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
