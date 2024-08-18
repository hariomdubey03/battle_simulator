# BattleSimulator

Base URLs: http://localhost:8000

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
  "page": 1,
  "has_next": true,
  "has_prev": false,
  "data": [
    {
      "name": "Kartana",
      "type1": "grass",
      "type2": "steel",
      "attack": 181,
      "hp": 59,
      "Category": "Legendary"
    },
    {
      "name": "Rayquaza",
      "type1": "dragon",
      "type2": "flying",
      "attack": 180,
      "hp": 105,
      "Category": "Legendary"
    },
    {
      "name": "Groudon",
      "type1": "ground",
      "type2": "",
      "attack": 180,
      "hp": 100,
      "Category": "Legendary"
    },
    {
      "name": "Hoopa",
      "type1": "psychic",
      "type2": "ghost",
      "attack": 160,
      "hp": 80,
      "Category": "Legendary"
    },
    {
      "name": "Diancie",
      "type1": "rock",
      "type2": "fairy",
      "attack": 160,
      "hp": 50,
      "Category": "Legendary"
    },
    {
      "name": "Regigigas",
      "type1": "normal",
      "type2": "",
      "attack": 160,
      "hp": 110,
      "Category": "Legendary"
    },
    {
      "name": "Kyogre",
      "type1": "water",
      "type2": "",
      "attack": 150,
      "hp": 100,
      "Category": "Legendary"
    },
    {
      "name": "Mewtwo",
      "type1": "psychic",
      "type2": "",
      "attack": 150,
      "hp": 106,
      "Category": "Legendary"
    },
    {
      "name": "Zekrom",
      "type1": "dragon",
      "type2": "electric",
      "attack": 150,
      "hp": 100,
      "Category": "Legendary"
    },
    {
      "name": "Landorus",
      "type1": "ground",
      "type2": "flying",
      "attack": 145,
      "hp": 89,
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

GET /v1/pokemon/battle/c728770e-9a20-461a-bd93-930490150e1c

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
  "battle_id": "c728770e-9a20-461a-bd93-930490150e1c"
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
