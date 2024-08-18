-- battle_simulator.battle definition

CREATE TABLE `battle` (
  `battle_id` varchar(36) NOT NULL DEFAULT (uuid()),
  `pokemon_a` varchar(100) DEFAULT NULL,
  `pokemon_b` varchar(100) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `winner_name` varchar(100) DEFAULT NULL,
  `won_by_margin` float DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`battle_id`),
  KEY `fk_pokemon_a` (`pokemon_a`),
  KEY `fk_pokemon_b` (`pokemon_b`),
  CONSTRAINT `fk_pokemon_a` FOREIGN KEY (`pokemon_a`) REFERENCES `pokemon` (`name`),
  CONSTRAINT `fk_pokemon_b` FOREIGN KEY (`pokemon_b`) REFERENCES `pokemon` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;