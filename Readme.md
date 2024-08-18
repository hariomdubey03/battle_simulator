# Battle Simulator

Base URLs: https://battle-simulator.hariomdubey.me

# Pokemon

## GET Pokemon List

GET /v1/pokemon/list

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|page|query|string| no |none|
|name|query|string| no |none|

> Response Examples

> Pokemon List - Page No

```json
{
  "page": 2,
  "has_next": true,
  "has_prev": true,
  "data": [
    {
      "name": "Buzzwole",
      "type1": "bug",
      "type2": "fighting",
      "attack": 139,
      "hp": 107,
      "Category": "Legendary"
    },
    {
      "name": "Pheromosa",
      "type1": "bug",
      "type2": "fighting",
      "attack": 137,
      "hp": 71,
      "Category": "Legendary"
    },
    {
      "name": "Solgaleo",
      "type1": "psychic",
      "type2": "steel",
      "attack": 137,
      "hp": 137,
      "Category": "Legendary"
    },
    {
      "name": "Xerneas",
      "type1": "fairy",
      "type2": "",
      "attack": 131,
      "hp": 126,
      "Category": "Legendary"
    },
    {
      "name": "Yveltal",
      "type1": "dark",
      "type2": "flying",
      "attack": 131,
      "hp": 126,
      "Category": "Legendary"
    },
    {
      "name": "Tapu Bulu",
      "type1": "grass",
      "type2": "fairy",
      "attack": 130,
      "hp": 70,
      "Category": "Legendary"
    },
    {
      "name": "Ho-Oh",
      "type1": "fire",
      "type2": "flying",
      "attack": 130,
      "hp": 106,
      "Category": "Legendary"
    },
    {
      "name": "Latios",
      "type1": "dragon",
      "type2": "psychic",
      "attack": 130,
      "hp": 80,
      "Category": "Legendary"
    },
    {
      "name": "Terrakion",
      "type1": "rock",
      "type2": "fighting",
      "attack": 129,
      "hp": 91,
      "Category": "Legendary"
    },
    {
      "name": "Meloetta",
      "type1": "normal",
      "type2": "psychic",
      "attack": 128,
      "hp": 100,
      "Category": "Legendary"
    }
  ]
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Pokemon List - Page No|Inline|

### Responses Data Schema

HTTP Status Code **200**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» page|integer|true|none||none|
|» has_next|boolean|true|none||none|
|» has_prev|boolean|true|none||none|
|» data|[object]|true|none||none|
|»» name|string|true|none||none|
|»» type1|string|true|none||none|
|»» type2|string|true|none||none|
|»» attack|integer|true|none||none|
|»» hp|integer|true|none||none|
|»» Category|string|true|none||none|

## GET Battle Status

GET /v1/pokemon/battle/d2e7affd-ad05-4995-833a-4044a62eeba4

> Response Examples

> Battle Status

```json
{
  "data": {
    "status": "BATTLE_COMPLETED",
    "result": {
      "winnerName": "ekans",
      "wonByMargin": 7.5
    }
  }
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Battle Status|Inline|

### Responses Data Schema

HTTP Status Code **200**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» data|object|true|none||none|
|»» status|string|true|none||none|
|»» result|object|true|none||none|
|»»» winnerName|string|true|none||none|
|»»» wonByMargin|number|true|none||none|

## POST Perform Battle

POST /v1/pokemon/battle

> Body Parameters

```json
{
  "pokemon_a": "Ekans",
  "pokemon_b": "Electrike"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| no |none|
|» pokemon_a|body|string| yes |none|
|» pokemon_b|body|string| yes |none|

> Response Examples

> Perform Battle

```json
{
  "battle_id": "83f89b93-cc27-4087-9192-77531b841c14"
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|202|[Accepted](https://tools.ietf.org/html/rfc7231#section-6.3.3)|Perform Battle|Inline|

### Responses Data Schema

HTTP Status Code **202**

|Name|Type|Required|Restrictions|Title|description|
|---|---|---|---|---|---|
|» battle_id|string|true|none||none|

