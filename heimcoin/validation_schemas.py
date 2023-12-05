submit_transaction_validation_schema = {
    "type": "object",
    "properties": {
      "private_key": { "type": "string" },
      "input_list": { 
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "receiver_address": { "type": "string" },
            "receiver_amount": { "type": "number" },
            "otrnx": { "type": "string" },
          },
          "required": ["receiver_address", "receiver_amount", "otrnx"],
        },
        "minItems": 1
      },
      "output_list": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "receiver_address": { "type": "string" },
            "receiver_amount": { "type": "number" },
          },
          "required": ["receiver_address", "receiver_amount"]
        },
        "minItems": 1
      },
    },
    "required": ["private_key", "input_list", "output_list"]
}

mine_block_validation_schema = {
    "type": "object",
    "properties": {
      "miner_address": { "type": "string" },
    },
    "required": ["miner_address"]
}

wallet_transactions_validation_schema = {
    "type": "object",
    "properties": {
      "wallet_address": { "type": "string" },
    },
    "required": ["wallet_address"]
}

derive_wallet_validation_schema = {
    "type": "object",
    "properties": {
      "pass_phrase": { "type": "string" },
    },
    "required": ["pass_phrase"]
}

add_node_validation_schema = {
    "type": "object",
    "properties": {
      "nodes": {
        "type": "array",
        "items": {
          "type": "string"
        },
      },
    },
    "required": ["pass_phrase"]
}

